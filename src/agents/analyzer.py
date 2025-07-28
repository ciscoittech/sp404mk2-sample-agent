"""Analyzer Agent - Analyzes audio files for BPM, key, and other characteristics."""

import os
import glob
import json
import shutil
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

from ..logging_config import AgentLogger
from ..tools import audio, database
from .base import Agent, AgentResult, AgentStatus


class AnalyzerAgent(Agent):
    """Agent responsible for analyzing audio samples."""
    
    def __init__(self):
        """Initialize the Analyzer Agent."""
        super().__init__("analyzer")
        self.logger = AgentLogger(self.name)
        
    async def execute(self, task_id: str, **kwargs) -> AgentResult:
        """
        Analyze audio samples for musical characteristics.
        
        Args:
            task_id: Unique task identifier
            file_path: Single file to analyze
            file_paths: List of file paths to analyze
            input_dir: Directory to analyze all audio files
            detect_bpm: Whether to detect BPM (default: True)
            detect_key: Whether to detect musical key
            analyze_spectrum: Whether to analyze frequency content
            organize_by_bpm: Whether to organize files into BPM folders
            bpm_ranges: List of (min, max) tuples for BPM organization
            group_by_key: Whether to group results by musical key
            detect_duplicates: Whether to detect duplicate samples
            create_fingerprints: Whether to create audio fingerprints
            confidence_threshold: Minimum confidence for detections
            batch_size: Number of files to process in parallel
            create_report: Whether to create analysis report
            report_path: Path for analysis report
            
        Returns:
            AgentResult with analysis details
        """
        self.logger.set_task_id(task_id)
        self.logger.info("Starting analysis task")
        started_at = datetime.now(timezone.utc)
        
        # Extract parameters
        file_path = kwargs.get("file_path")
        file_paths = kwargs.get("file_paths", [])
        input_dir = kwargs.get("input_dir")
        detect_bpm = kwargs.get("detect_bpm", True)
        detect_key = kwargs.get("detect_key", False)
        analyze_spectrum = kwargs.get("analyze_spectrum", False)
        organize_by_bpm = kwargs.get("organize_by_bpm", False)
        bpm_ranges = kwargs.get("bpm_ranges", [(80, 90), (90, 100), (100, 110), (110, 120), (120, 130)])
        group_by_key = kwargs.get("group_by_key", False)
        detect_duplicates = kwargs.get("detect_duplicates", False)
        create_fingerprints = kwargs.get("create_fingerprints", False)
        confidence_threshold = kwargs.get("confidence_threshold", 0.0)
        batch_size = kwargs.get("batch_size", 10)
        create_report = kwargs.get("create_report", False)
        report_path = kwargs.get("report_path", "analysis_report.json")
        
        # Gather files to analyze
        if file_path:
            file_paths = [file_path]
        elif input_dir:
            # Find all audio files in directory
            patterns = ["*.wav", "*.mp3", "*.flac", "*.m4a", "*.aiff"]
            file_paths = []
            for pattern in patterns:
                file_paths.extend(glob.glob(os.path.join(input_dir, pattern)))
        
        if not file_paths:
            error_msg = "No files to analyze"
            self.logger.error(error_msg)
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "error",
                "message": error_msg
            })
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=error_msg,
                started_at=started_at,
            )
        
        try:
            self.logger.info(f"Analyzing {len(file_paths)} files")
            
            # Process files
            if len(file_paths) > 1 and batch_size > 1:
                # Batch processing
                analyzed_files = await self._batch_analyze(
                    file_paths, batch_size, detect_bpm, detect_key,
                    analyze_spectrum, confidence_threshold
                )
            else:
                # Single file processing
                analyzed_files = []
                for fp in file_paths:
                    result = await self._analyze_single_file(
                        fp, detect_bpm, detect_key, analyze_spectrum,
                        confidence_threshold
                    )
                    if result:
                        analyzed_files.append(result)
            
            # Post-processing
            low_confidence_count = 0
            duplicate_groups = []
            key_groups = defaultdict(list) if group_by_key else None
            
            for file_data in analyzed_files:
                # Check confidence
                if file_data.get("confidence", 1.0) < confidence_threshold:
                    low_confidence_count += 1
                    file_data["warning"] = "Low confidence BPM detection"
                
                # Group by key
                if group_by_key and "key" in file_data:
                    key_groups[file_data["key"]].append(file_data["file_path"])
                
                # Update database
                await self._update_database(file_data)
            
            # Organize by BPM if requested
            if organize_by_bpm:
                await self._organize_by_bpm(analyzed_files, input_dir or os.path.dirname(file_paths[0]), bpm_ranges)
            
            # Detect duplicates
            if detect_duplicates:
                duplicate_groups = await self._detect_duplicates(analyzed_files)
            
            # Create report
            if create_report:
                await self._create_report(analyzed_files, report_path)
            
            # Log success
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "info",
                "message": f"Successfully analyzed {len(analyzed_files)} files",
                "context": {"analyzed_count": len(analyzed_files)}
            })
            
            result_data = {
                "analyzed_count": len(analyzed_files),
                "files": analyzed_files,
                "low_confidence_count": low_confidence_count,
                "duplicates_found": len(duplicate_groups),
                "duplicate_groups": duplicate_groups
            }
            
            if group_by_key and key_groups:
                result_data["key_groups"] = dict(key_groups)
            
            if create_report:
                result_data["report_created"] = True
                result_data["report_path"] = report_path
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.SUCCESS,
                result=result_data,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                metadata={
                    "detect_bpm": detect_bpm,
                    "detect_key": detect_key,
                    "confidence_threshold": confidence_threshold
                }
            )
            
        except Exception as e:
            self.logger.exception(f"Analysis failed: {str(e)}")
            
            await database.add_agent_log({
                "task_id": task_id,
                "agent_type": self.name,
                "log_level": "error",
                "message": f"Analysis failed: {str(e)}",
                "context": {"error": str(e)}
            })
            
            return AgentResult(
                agent_name=self.name,
                task_id=task_id,
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc)
            )
    
    async def _analyze_single_file(
        self,
        file_path: str,
        detect_bpm: bool,
        detect_key: bool,
        analyze_spectrum: bool,
        confidence_threshold: float
    ) -> Optional[Dict]:
        """Analyze a single audio file."""
        try:
            result = {"file_path": file_path}
            
            # Get duration
            duration = audio.get_duration(file_path)
            result["duration"] = duration
            
            # Detect BPM
            if detect_bpm:
                bpm_data = audio.detect_bpm(file_path)
                result["bpm"] = bpm_data["bpm"]
                result["confidence"] = bpm_data["confidence"]
            
            # Detect key
            if detect_key:
                key_data = audio.detect_key(file_path)
                result["key"] = key_data["key"]
                result["key_confidence"] = key_data["confidence"]
            
            # Analyze spectrum
            if analyze_spectrum:
                spectrum_data = audio.analyze_frequency_content(file_path)
                result.update(spectrum_data)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {e}")
            return None
    
    async def _batch_analyze(
        self,
        file_paths: List[str],
        batch_size: int,
        detect_bpm: bool,
        detect_key: bool,
        analyze_spectrum: bool,
        confidence_threshold: float
    ) -> List[Dict]:
        """Analyze files in batches."""
        all_results = []
        
        # Process in batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            
            if detect_bpm:
                # Use batch BPM detection
                batch_results = await audio.batch_analyze(batch)
                
                # Add additional analysis if needed
                for j, result in enumerate(batch_results):
                    if result.get("success", True):
                        if detect_key:
                            key_data = audio.detect_key(batch[j])
                            result["key"] = key_data["key"]
                            result["key_confidence"] = key_data["confidence"]
                        
                        if analyze_spectrum:
                            spectrum_data = audio.analyze_frequency_content(batch[j])
                            result.update(spectrum_data)
                        
                        all_results.append(result)
            else:
                # Process individually if not detecting BPM
                for fp in batch:
                    result = await self._analyze_single_file(
                        fp, detect_bpm, detect_key, analyze_spectrum, confidence_threshold
                    )
                    if result:
                        all_results.append(result)
        
        return all_results
    
    async def _organize_by_bpm(
        self,
        analyzed_files: List[Dict],
        base_dir: str,
        bpm_ranges: List[Tuple[int, int]]
    ) -> None:
        """Organize files into BPM range folders."""
        for file_data in analyzed_files:
            if "bpm" not in file_data:
                continue
            
            bpm = file_data["bpm"]
            file_path = file_data["file_path"]
            
            # Find appropriate range
            target_dir = None
            for min_bpm, max_bpm in bpm_ranges:
                if min_bpm <= bpm < max_bpm:
                    target_dir = os.path.join(base_dir, f"{min_bpm}_{max_bpm}_bpm")
                    break
            
            if not target_dir:
                # Outside defined ranges
                target_dir = os.path.join(base_dir, "other_bpm")
            
            # Create directory and move file
            os.makedirs(target_dir, exist_ok=True)
            filename = os.path.basename(file_path)
            new_path = os.path.join(target_dir, filename)
            
            shutil.move(file_path, new_path)
            file_data["file_path"] = new_path
            
            self.logger.info(f"Moved {filename} to {target_dir}")
    
    async def _detect_duplicates(self, analyzed_files: List[Dict]) -> List[List[str]]:
        """Detect duplicate samples using fingerprints."""
        fingerprint_map = defaultdict(list)
        duplicate_groups = []
        
        for file_data in analyzed_files:
            file_path = file_data["file_path"]
            
            # Create fingerprint
            try:
                fingerprint = audio.create_fingerprint(file_path)
                
                # Check if fingerprint exists in database
                existing = await database.get_samples_by_fingerprint(fingerprint)
                
                if existing:
                    # Found duplicate
                    fingerprint_map[fingerprint].append(file_path)
                    fingerprint_map[fingerprint].extend([s["file_path"] for s in existing])
                else:
                    fingerprint_map[fingerprint].append(file_path)
                
                file_data["fingerprint"] = fingerprint
                
            except Exception as e:
                self.logger.warning(f"Failed to create fingerprint for {file_path}: {e}")
        
        # Group duplicates
        for fingerprint, paths in fingerprint_map.items():
            if len(paths) > 1:
                duplicate_groups.append(list(set(paths)))
        
        return duplicate_groups
    
    async def _update_database(self, file_data: Dict) -> None:
        """Update database with analysis results."""
        try:
            update_data = {
                "file_path": file_data["file_path"],
                "bpm": file_data.get("bpm"),
                "key_signature": file_data.get("key"),
                "duration_seconds": file_data.get("duration"),
                "spectral_centroid": file_data.get("spectral_centroid"),
                "fingerprint": file_data.get("fingerprint"),
                "analyzed_at": datetime.now(timezone.utc)
            }
            
            await database.update_sample(update_data)
            
        except Exception as e:
            self.logger.error(f"Failed to update database: {e}")
    
    async def _create_report(self, analyzed_files: List[Dict], report_path: str) -> None:
        """Create analysis report."""
        report = {
            "analysis_date": datetime.now(timezone.utc).isoformat(),
            "total_files": len(analyzed_files),
            "summary": {
                "average_bpm": sum(f.get("bpm", 0) for f in analyzed_files) / len(analyzed_files) if analyzed_files else 0,
                "key_distribution": defaultdict(int),
                "duration_total": sum(f.get("duration", 0) for f in analyzed_files)
            },
            "files": analyzed_files
        }
        
        # Calculate key distribution
        for f in analyzed_files:
            if "key" in f:
                report["summary"]["key_distribution"][f["key"]] += 1
        
        report["summary"]["key_distribution"] = dict(report["summary"]["key_distribution"])
        
        # Write report
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Created analysis report: {report_path}")


# Mock function for database operations not yet implemented
async def update_sample(data: Dict) -> Dict:
    """Update sample in database."""
    return {"success": True}

async def get_samples_by_fingerprint(fingerprint: str) -> List[Dict]:
    """Get samples by fingerprint."""
    return []

async def update_sample_batch(samples: List[Dict]) -> Dict:
    """Update multiple samples."""
    return {"success": True}

# Add mock functions to database module
database.update_sample = update_sample
database.get_samples_by_fingerprint = get_samples_by_fingerprint
database.update_sample_batch = update_sample_batch