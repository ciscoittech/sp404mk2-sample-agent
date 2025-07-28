"""
Intelligent Organization System - Smart sample library management.
Automatically organizes samples based on musical characteristics, compatibility, and usage patterns.
"""

import os
import shutil
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import asyncio

from ..logging_config import AgentLogger
from ..agents.groove_analyst import GrooveAnalystAgent
from ..agents.era_expert import EraExpertAgent
from ..agents.sample_relationship import SampleRelationshipAgent
from .audio import detect_bpm, detect_key, analyze_frequency_content, get_duration


class IntelligentOrganizer:
    """Intelligent sample organization system."""
    
    def __init__(self, base_path: str = "organized_samples"):
        """Initialize the intelligent organizer.
        
        Args:
            base_path: Root directory for organized samples
        """
        self.logger = AgentLogger("intelligent_organizer")
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # Initialize agents
        self.groove_agent = GrooveAnalystAgent()
        self.era_agent = EraExpertAgent()
        self.relationship_agent = SampleRelationshipAgent()
        
        # Organization strategies
        self.strategies = {
            "musical": self._organize_by_musical_properties,
            "genre": self._organize_by_genre_and_era,
            "groove": self._organize_by_groove_style,
            "compatibility": self._organize_by_compatibility_groups,
            "sp404": self._organize_for_sp404_banks,
            "project": self._organize_by_project_type
        }
        
        # SP-404 bank templates
        self.sp404_templates = {
            "hip_hop_kit": {
                "A": ["kick", "snare", "hihat_closed", "hihat_open"],
                "B": ["perc1", "perc2", "crash", "ride"],
                "C": ["bass", "sub", "808", "bass_stab"],
                "D": ["melody", "sample", "vocal", "fx"]
            },
            "live_performance": {
                "A": ["intro", "verse1", "verse2", "verse3"],
                "B": ["chorus1", "chorus2", "bridge", "outro"],
                "C": ["drums_full", "drums_minimal", "drums_break", "drums_fill"],
                "D": ["fx_rise", "fx_impact", "fx_transition", "fx_atmosphere"]
            },
            "finger_drumming": {
                "A": ["kick1", "kick2", "snare1", "snare2"],
                "B": ["hihat1", "hihat2", "open_hat", "crash"],
                "C": ["tom1", "tom2", "tom3", "clap"],
                "D": ["perc1", "perc2", "perc3", "perc4"]
            }
        }
        
        # Genre templates
        self.genre_templates = {
            "hip_hop": ["drums", "bass", "melody", "vocal_chops", "fx"],
            "jazz": ["drums", "bass", "piano", "horns", "atmosphere"],
            "electronic": ["drums", "bass", "synths", "pads", "fx"],
            "soul": ["drums", "bass", "keys", "strings", "vocals"]
        }
    
    async def organize_samples(
        self,
        sample_paths: List[str],
        strategy: str = "musical",
        analyze_relationships: bool = True,
        copy_files: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Organize samples using intelligent analysis.
        
        Args:
            sample_paths: List of sample file paths
            strategy: Organization strategy to use
            analyze_relationships: Whether to analyze sample compatibility
            copy_files: Whether to copy files (True) or just plan organization (False)
            **kwargs: Strategy-specific parameters
            
        Returns:
            Organization results and statistics
        """
        self.logger.info(f"Organizing {len(sample_paths)} samples using '{strategy}' strategy")
        
        # Validate strategy
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.strategies.keys())}")
        
        # Analyze all samples
        analyses = await self._analyze_samples(sample_paths, analyze_relationships)
        
        # Apply organization strategy
        organization_plan = await self.strategies[strategy](analyses, **kwargs)
        
        # Execute organization
        if copy_files:
            stats = await self._execute_organization(organization_plan)
        else:
            stats = {"planned": True, "folders": len(organization_plan)}
        
        # Generate report
        report = self._generate_organization_report(organization_plan, analyses, stats)
        
        return {
            "strategy": strategy,
            "organization_plan": organization_plan,
            "statistics": stats,
            "report": report
        }
    
    async def _analyze_samples(
        self,
        sample_paths: List[str],
        analyze_relationships: bool
    ) -> List[Dict[str, Any]]:
        """Analyze all samples for organization."""
        analyses = []
        
        for path in sample_paths:
            if not os.path.exists(path):
                self.logger.warning(f"Sample not found: {path}")
                continue
            
            # Basic audio analysis
            analysis = {
                "path": path,
                "filename": os.path.basename(path),
                "bpm": detect_bpm(path),
                "key": detect_key(path),
                "frequency": analyze_frequency_content(path),
                "duration": get_duration(path)
            }
            
            # Groove analysis
            groove_result = await self.groove_agent.execute(
                task_id=f"org_groove_{datetime.now().timestamp()}",
                file_paths=[path]
            )
            if groove_result.result:
                analysis["groove"] = groove_result.result["analyses"][0]
            
            # Era detection
            era_result = await self.era_agent.execute(
                task_id=f"org_era_{datetime.now().timestamp()}",
                file_paths=[path]
            )
            if era_result.result:
                analysis["era"] = era_result.result["analyses"][0]
            
            analyses.append(analysis)
        
        # Analyze relationships if requested
        if analyze_relationships and len(analyses) > 1:
            await self._analyze_compatibility(analyses)
        
        return analyses
    
    async def _analyze_compatibility(self, analyses: List[Dict[str, Any]]) -> None:
        """Analyze compatibility between samples."""
        # Create pairs for compatibility analysis
        pairs = []
        for i, a1 in enumerate(analyses):
            for a2 in analyses[i+1:]:
                pairs.append((a1["path"], a2["path"]))
        
        # Limit to reasonable number of pairs
        if len(pairs) > 50:
            pairs = pairs[:50]
            self.logger.info(f"Limited compatibility analysis to first 50 pairs")
        
        # Analyze compatibility
        compat_result = await self.relationship_agent.execute(
            task_id=f"org_compat_{datetime.now().timestamp()}",
            sample_pairs=pairs
        )
        
        # Store compatibility scores in analyses
        if compat_result.result:
            for compat in compat_result.result.get("analyses", []):
                # Find samples in analyses
                for analysis in analyses:
                    if analysis["path"] == compat["sample1_path"]:
                        if "compatibility" not in analysis:
                            analysis["compatibility"] = {}
                        analysis["compatibility"][compat["sample2_path"]] = compat["overall_score"]
                    elif analysis["path"] == compat["sample2_path"]:
                        if "compatibility" not in analysis:
                            analysis["compatibility"] = {}
                        analysis["compatibility"][compat["sample1_path"]] = compat["overall_score"]
    
    async def _organize_by_musical_properties(
        self,
        analyses: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize by BPM, key, and type."""
        organization = {}
        
        for analysis in analyses:
            # Determine sample type
            sample_type = self._detect_sample_type(analysis)
            
            # Create folder structure
            bpm = analysis["bpm"]["bpm"]
            key = analysis["key"]["key"]
            
            # BPM ranges
            if bpm < 70:
                bpm_range = "slow_60-70"
            elif bpm < 90:
                bpm_range = "medium_70-90"
            elif bpm < 120:
                bpm_range = "uptempo_90-120"
            elif bpm < 140:
                bpm_range = "fast_120-140"
            else:
                bpm_range = "very_fast_140+"
            
            # Folder path
            folder = f"{sample_type}/{bpm_range}/{key}"
            
            if folder not in organization:
                organization[folder] = []
            
            organization[folder].append({
                "source": analysis["path"],
                "analysis": analysis,
                "rename": self._generate_descriptive_name(analysis)
            })
        
        return organization
    
    async def _organize_by_genre_and_era(
        self,
        analyses: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize by detected era and genre."""
        organization = {}
        
        for analysis in analyses:
            # Get era info
            era = "unknown"
            genre = "general"
            
            if "era" in analysis:
                era = analysis["era"].get("detected_era", "unknown")
                # Infer genre from groove style
                if "groove" in analysis:
                    groove_type = analysis["groove"].get("groove_type", "")
                    genre = self._infer_genre_from_groove(groove_type)
            
            # Create folder
            folder = f"{genre}/{era}"
            
            if folder not in organization:
                organization[folder] = []
            
            organization[folder].append({
                "source": analysis["path"],
                "analysis": analysis,
                "rename": self._generate_descriptive_name(analysis)
            })
        
        return organization
    
    async def _organize_by_groove_style(
        self,
        analyses: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize by groove characteristics."""
        organization = {}
        
        for analysis in analyses:
            if "groove" not in analysis:
                folder = "no_groove"
            else:
                groove = analysis["groove"]
                groove_type = groove.get("groove_type", "straight")
                swing_pct = groove.get("swing_percentage", 50)
                
                # Categorize by feel
                if swing_pct < 55:
                    feel = "straight"
                elif swing_pct < 65:
                    feel = "slight_swing"
                elif swing_pct < 75:
                    feel = "heavy_swing"
                else:
                    feel = "extreme_swing"
                
                folder = f"{groove_type}/{feel}"
            
            if folder not in organization:
                organization[folder] = []
            
            organization[folder].append({
                "source": analysis["path"],
                "analysis": analysis,
                "rename": self._generate_descriptive_name(analysis)
            })
        
        return organization
    
    async def _organize_by_compatibility_groups(
        self,
        analyses: List[Dict[str, Any]],
        threshold: float = 7.0,
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group samples that work well together."""
        organization = {}
        used_samples = set()
        
        # Sort by average compatibility score
        for analysis in analyses:
            if "compatibility" in analysis:
                scores = list(analysis["compatibility"].values())
                analysis["avg_compatibility"] = sum(scores) / len(scores) if scores else 0
            else:
                analysis["avg_compatibility"] = 0
        
        # Create compatibility groups
        group_num = 1
        for analysis in sorted(analyses, key=lambda x: x["avg_compatibility"], reverse=True):
            if analysis["path"] in used_samples:
                continue
            
            # Find compatible samples
            group = [analysis]
            used_samples.add(analysis["path"])
            
            if "compatibility" in analysis:
                for other_path, score in analysis["compatibility"].items():
                    if score >= threshold and other_path not in used_samples:
                        # Find the other analysis
                        for other in analyses:
                            if other["path"] == other_path:
                                group.append(other)
                                used_samples.add(other_path)
                                break
            
            # Create group folder
            if len(group) > 1:
                folder = f"compatible_group_{group_num}"
                group_num += 1
            else:
                folder = "standalone"
            
            if folder not in organization:
                organization[folder] = []
            
            for member in group:
                organization[folder].append({
                    "source": member["path"],
                    "analysis": member,
                    "rename": self._generate_descriptive_name(member)
                })
        
        return organization
    
    async def _organize_for_sp404_banks(
        self,
        analyses: List[Dict[str, Any]],
        template: str = "hip_hop_kit",
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize samples into SP-404 bank structure."""
        if template not in self.sp404_templates:
            template = "hip_hop_kit"
        
        organization = {}
        template_config = self.sp404_templates[template]
        
        # Categorize samples
        categorized = self._categorize_for_sp404(analyses)
        
        # Fill banks according to template
        for bank, slots in template_config.items():
            bank_folder = f"SP404_Bank_{bank}"
            organization[bank_folder] = []
            
            for i, slot_type in enumerate(slots):
                # Find best match for slot
                if slot_type in categorized and categorized[slot_type]:
                    sample = categorized[slot_type].pop(0)
                    pad_num = i + 1
                    
                    organization[bank_folder].append({
                        "source": sample["path"],
                        "analysis": sample,
                        "rename": f"{bank}{pad_num:02d}_{slot_type}_{sample['filename']}"
                    })
        
        # Add overflow samples
        overflow_folder = "SP404_Overflow"
        organization[overflow_folder] = []
        
        for category, samples in categorized.items():
            for sample in samples:
                organization[overflow_folder].append({
                    "source": sample["path"],
                    "analysis": sample,
                    "rename": f"overflow_{category}_{sample['filename']}"
                })
        
        return organization
    
    async def _organize_by_project_type(
        self,
        analyses: List[Dict[str, Any]],
        project_type: str = "beat_making",
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize for specific production workflows."""
        organization = {}
        
        if project_type == "beat_making":
            # Organize for beat production
            categories = {
                "drums": lambda a: self._detect_sample_type(a) == "drums",
                "bass": lambda a: self._detect_sample_type(a) == "bass",
                "melodies": lambda a: self._detect_sample_type(a) in ["melody", "harmony"],
                "textures": lambda a: self._detect_sample_type(a) == "texture",
                "oneshots": lambda a: a["duration"] < 1.0
            }
        elif project_type == "live_looping":
            # Organize for live performance
            categories = {
                "loops_4bar": lambda a: 3.5 < a["duration"] < 4.5,
                "loops_8bar": lambda a: 7.5 < a["duration"] < 8.5,
                "transitions": lambda a: "fx" in a["filename"].lower(),
                "oneshots": lambda a: a["duration"] < 1.0
            }
        else:
            # Default project organization
            categories = {
                "rhythmic": lambda a: "groove" in a and a["groove"].get("has_rhythm", False),
                "tonal": lambda a: a["key"]["confidence"] > 0.7,
                "atmospheric": lambda a: a["duration"] > 4.0,
                "percussive": lambda a: self._detect_sample_type(a) == "drums"
            }
        
        # Sort samples into categories
        for analysis in analyses:
            placed = False
            for category, test_func in categories.items():
                if test_func(analysis):
                    folder = f"{project_type}/{category}"
                    if folder not in organization:
                        organization[folder] = []
                    
                    organization[folder].append({
                        "source": analysis["path"],
                        "analysis": analysis,
                        "rename": self._generate_descriptive_name(analysis)
                    })
                    placed = True
                    break
            
            if not placed:
                # Uncategorized
                folder = f"{project_type}/other"
                if folder not in organization:
                    organization[folder] = []
                
                organization[folder].append({
                    "source": analysis["path"],
                    "analysis": analysis,
                    "rename": self._generate_descriptive_name(analysis)
                })
        
        return organization
    
    async def _execute_organization(
        self,
        organization_plan: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Execute the organization plan by copying/moving files."""
        stats = {
            "folders_created": 0,
            "files_organized": 0,
            "errors": []
        }
        
        for folder, files in organization_plan.items():
            # Create folder
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            stats["folders_created"] += 1
            
            # Copy/move files
            for file_info in files:
                try:
                    source = file_info["source"]
                    new_name = file_info["rename"]
                    dest = folder_path / new_name
                    
                    # Copy file
                    shutil.copy2(source, dest)
                    stats["files_organized"] += 1
                    
                    # Save analysis metadata
                    metadata_path = dest.with_suffix(".json")
                    with open(metadata_path, "w") as f:
                        json.dump(file_info["analysis"], f, indent=2, default=str)
                    
                except Exception as e:
                    self.logger.error(f"Failed to organize {source}: {str(e)}")
                    stats["errors"].append(f"{source}: {str(e)}")
        
        return stats
    
    def _detect_sample_type(self, analysis: Dict[str, Any]) -> str:
        """Detect the type of sample from analysis."""
        filename = analysis["filename"].lower()
        freq = analysis["frequency"]
        duration = analysis["duration"]
        
        # Check filename hints
        if any(x in filename for x in ["kick", "bd", "bassdrum"]):
            return "kick"
        elif any(x in filename for x in ["snare", "sd", "sn"]):
            return "snare"
        elif any(x in filename for x in ["hat", "hh", "hihat"]):
            return "hihat"
        elif any(x in filename for x in ["drum", "beat", "loop", "break"]):
            return "drums"
        elif any(x in filename for x in ["bass", "sub", "808"]):
            return "bass"
        elif any(x in filename for x in ["pad", "string", "ambient"]):
            return "pad"
        elif any(x in filename for x in ["lead", "melody", "synth"]):
            return "melody"
        
        # Check frequency content
        centroid = freq.get("spectral_centroid", 2000)
        if centroid < 200:
            return "bass"
        elif centroid > 5000:
            return "hihat"
        elif duration > 4.0:
            return "pad"
        elif duration < 0.5:
            return "oneshot"
        else:
            return "general"
    
    def _generate_descriptive_name(self, analysis: Dict[str, Any]) -> str:
        """Generate a descriptive filename."""
        parts = []
        
        # Original name (cleaned)
        base_name = Path(analysis["filename"]).stem
        base_name = base_name.replace(" ", "_")[:20]
        
        # Add BPM
        bpm = int(analysis["bpm"]["bpm"])
        parts.append(f"{bpm}bpm")
        
        # Add key
        key = analysis["key"]["key"].replace(" ", "")
        parts.append(key)
        
        # Add groove info if available
        if "groove" in analysis:
            groove_type = analysis["groove"].get("groove_type", "").replace("_", "")[:10]
            if groove_type:
                parts.append(groove_type)
        
        # Combine
        suffix = "_".join(parts)
        extension = Path(analysis["filename"]).suffix
        
        return f"{base_name}_{suffix}{extension}"
    
    def _infer_genre_from_groove(self, groove_type: str) -> str:
        """Infer genre from groove type."""
        groove_genre_map = {
            "boom_bap": "hip_hop",
            "trap": "hip_hop",
            "swing": "jazz",
            "straight": "electronic",
            "samba": "latin",
            "afrobeat": "world",
            "breakbeat": "electronic"
        }
        
        for groove, genre in groove_genre_map.items():
            if groove in groove_type.lower():
                return genre
        
        return "general"
    
    def _categorize_for_sp404(self, analyses: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize samples for SP-404 banks."""
        categories = {
            "kick": [],
            "snare": [],
            "hihat_closed": [],
            "hihat_open": [],
            "perc1": [],
            "perc2": [],
            "crash": [],
            "ride": [],
            "bass": [],
            "sub": [],
            "808": [],
            "bass_stab": [],
            "melody": [],
            "sample": [],
            "vocal": [],
            "fx": []
        }
        
        for analysis in analyses:
            sample_type = self._detect_sample_type(analysis)
            filename = analysis["filename"].lower()
            
            # Map to SP-404 categories
            if sample_type == "kick":
                categories["kick"].append(analysis)
            elif sample_type == "snare":
                categories["snare"].append(analysis)
            elif sample_type == "hihat":
                if "open" in filename:
                    categories["hihat_open"].append(analysis)
                else:
                    categories["hihat_closed"].append(analysis)
            elif sample_type == "drums":
                if "crash" in filename:
                    categories["crash"].append(analysis)
                elif "ride" in filename:
                    categories["ride"].append(analysis)
                else:
                    categories["perc1"].append(analysis)
            elif sample_type == "bass":
                if "808" in filename:
                    categories["808"].append(analysis)
                elif "sub" in filename:
                    categories["sub"].append(analysis)
                elif analysis["duration"] < 1.0:
                    categories["bass_stab"].append(analysis)
                else:
                    categories["bass"].append(analysis)
            elif sample_type == "melody":
                categories["melody"].append(analysis)
            elif "vocal" in filename:
                categories["vocal"].append(analysis)
            elif "fx" in filename or "riser" in filename:
                categories["fx"].append(analysis)
            else:
                categories["sample"].append(analysis)
        
        return categories
    
    def _generate_organization_report(
        self,
        organization_plan: Dict[str, List[Dict[str, Any]]],
        analyses: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> str:
        """Generate a human-readable organization report."""
        report = []
        report.append("# Sample Organization Report")
        report.append(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Samples: {len(analyses)}")
        report.append(f"Folders Created: {stats.get('folders_created', 0)}")
        report.append(f"Files Organized: {stats.get('files_organized', 0)}")
        
        if stats.get("errors"):
            report.append(f"\n## Errors ({len(stats['errors'])})")
            for error in stats["errors"][:5]:
                report.append(f"- {error}")
        
        report.append("\n## Organization Structure")
        for folder, files in sorted(organization_plan.items()):
            report.append(f"\n### {folder} ({len(files)} files)")
            
            # Sample details
            for file_info in files[:3]:  # Show first 3
                analysis = file_info["analysis"]
                report.append(f"- {file_info['rename']}")
                report.append(f"  - BPM: {analysis['bpm']['bpm']:.1f}")
                report.append(f"  - Key: {analysis['key']['key']}")
                if "groove" in analysis:
                    report.append(f"  - Groove: {analysis['groove'].get('groove_type', 'N/A')}")
            
            if len(files) > 3:
                report.append(f"  ... and {len(files) - 3} more")
        
        # Compatibility summary
        high_compat_pairs = []
        for analysis in analyses:
            if "compatibility" in analysis:
                for other_path, score in analysis["compatibility"].items():
                    if score >= 8.0:
                        high_compat_pairs.append((
                            os.path.basename(analysis["path"]),
                            os.path.basename(other_path),
                            score
                        ))
        
        if high_compat_pairs:
            report.append("\n## High Compatibility Pairs")
            for s1, s2, score in high_compat_pairs[:5]:
                report.append(f"- {s1} + {s2}: {score}/10")
        
        return "\n".join(report)


# Convenience functions
async def organize_samples(
    sample_paths: List[str],
    strategy: str = "musical",
    output_dir: str = "organized_samples",
    **kwargs
) -> Dict[str, Any]:
    """Organize samples using intelligent analysis."""
    organizer = IntelligentOrganizer(output_dir)
    return await organizer.organize_samples(sample_paths, strategy, **kwargs)


async def create_sp404_banks(
    sample_paths: List[str],
    template: str = "hip_hop_kit",
    output_dir: str = "sp404_banks"
) -> Dict[str, Any]:
    """Organize samples into SP-404 bank structure."""
    organizer = IntelligentOrganizer(output_dir)
    return await organizer.organize_samples(
        sample_paths,
        strategy="sp404",
        template=template
    )


async def group_compatible_samples(
    sample_paths: List[str],
    compatibility_threshold: float = 7.0,
    output_dir: str = "compatible_groups"
) -> Dict[str, Any]:
    """Group samples by compatibility."""
    organizer = IntelligentOrganizer(output_dir)
    return await organizer.organize_samples(
        sample_paths,
        strategy="compatibility",
        threshold=compatibility_threshold
    )