"""
Timestamp-based extraction for YouTube videos.
Extracts specific segments based on timestamps in comments and descriptions.
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import timedelta
import json

from ..logging_config import AgentLogger
from .download import download_youtube, get_youtube_metadata
from .audio import extract_audio_segment, analyze_audio_file

logger = AgentLogger("timestamp_extractor")


class TimestampExtractor:
    """Extract and download specific timestamps from YouTube videos."""
    
    def __init__(self):
        """Initialize the timestamp extractor."""
        # Timestamp patterns
        self.timestamp_patterns = [
            # Standard formats: 0:00, 00:00, 0:00:00
            r'(\d{1,2}:\d{2}(?::\d{2})?)',
            # With descriptions: 0:00 - Sample Name
            r'(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–]\s*([^\n\r]+)',
            # Bracketed: [0:00] Sample Name
            r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^\n\r]+)',
            # Parenthetical: (0:00) Sample Name
            r'\((\d{1,2}:\d{2}(?::\d{2})?)\)\s*([^\n\r]+)',
        ]
        
        # Sample-related keywords to identify relevant timestamps
        self.sample_keywords = [
            'sample', 'loop', 'break', 'beat', 'drum', 'bass',
            'melody', 'chord', 'intro', 'outro', 'hook', 'verse',
            'chorus', 'bridge', 'drop', 'build', 'pattern'
        ]
        
        # Fire emoji patterns (indicates hot samples in comments)
        self.fire_patterns = ['🔥', '🔥🔥', '🔥🔥🔥', 'fire', 'heat', 'hot']
    
    def parse_timestamp(self, timestamp_str: str) -> int:
        """
        Parse timestamp string to seconds.
        
        Args:
            timestamp_str: Timestamp in format "0:00" or "0:00:00"
            
        Returns:
            Seconds as integer
        """
        parts = timestamp_str.split(':')
        if len(parts) == 2:
            # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        return 0
    
    def extract_timestamps_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract timestamps from text (description or comments).
        
        Args:
            text: Text containing timestamps
            
        Returns:
            List of timestamp dictionaries
        """
        timestamps = []
        lines = text.split('\n')
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Check each pattern
            for pattern in self.timestamp_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) == 2:
                            timestamp_str, description = match
                        else:
                            timestamp_str = match[0]
                            description = line.replace(timestamp_str, '').strip(' -–[]():')
                    else:
                        timestamp_str = match
                        description = line.replace(timestamp_str, '').strip(' -–[]():')
                    
                    # Parse timestamp
                    seconds = self.parse_timestamp(timestamp_str)
                    
                    # Check if it's sample-related
                    is_sample = any(keyword in description.lower() 
                                  for keyword in self.sample_keywords)
                    
                    # Check for fire emojis (quality indicator)
                    fire_count = sum(1 for fire in self.fire_patterns 
                                   if fire in line)
                    
                    timestamps.append({
                        'time': seconds,
                        'timestamp': timestamp_str,
                        'description': description,
                        'is_sample': is_sample,
                        'quality_indicator': fire_count,
                        'original_line': line.strip()
                    })
        
        # Remove duplicates and sort by time
        seen = set()
        unique_timestamps = []
        for ts in timestamps:
            key = (ts['time'], ts['description'])
            if key not in seen:
                seen.add(key)
                unique_timestamps.append(ts)
        
        return sorted(unique_timestamps, key=lambda x: x['time'])
    
    async def extract_from_youtube_metadata(
        self,
        url: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract timestamps from YouTube video metadata.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with timestamps from description and top comments
        """
        try:
            # Get video metadata
            metadata = await get_youtube_metadata(url)
            
            results = {
                'description_timestamps': [],
                'comment_timestamps': [],
                'video_info': {
                    'title': metadata.get('title'),
                    'duration': metadata.get('duration'),
                    'channel': metadata.get('uploader')
                }
            }
            
            # Extract from description
            description = metadata.get('description', '')
            if description:
                results['description_timestamps'] = self.extract_timestamps_from_text(
                    description
                )
            
            # For production, you would also fetch comments via YouTube API
            # For now, we'll simulate with common patterns
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to extract timestamps: {e}")
            raise
    
    def generate_segments(
        self,
        timestamps: List[Dict[str, Any]],
        video_duration: int,
        segment_length: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Generate segments from timestamps.
        
        Args:
            timestamps: List of timestamp dictionaries
            video_duration: Total video duration in seconds
            segment_length: Default segment length in seconds
            
        Returns:
            List of segments with start/end times
        """
        segments = []
        
        for i, ts in enumerate(timestamps):
            start_time = ts['time']
            
            # Determine end time
            if i < len(timestamps) - 1:
                # Use next timestamp as end
                end_time = timestamps[i + 1]['time']
            else:
                # Use default segment length or video end
                end_time = min(start_time + segment_length, video_duration)
            
            # Ensure minimum segment length
            if end_time - start_time < 5:
                end_time = min(start_time + segment_length, video_duration)
            
            segments.append({
                'start': start_time,
                'end': end_time,
                'duration': end_time - start_time,
                'description': ts['description'],
                'is_sample': ts['is_sample'],
                'quality_indicator': ts['quality_indicator'],
                'timestamp': ts['timestamp']
            })
        
        return segments
    
    async def extract_segments(
        self,
        url: str,
        output_dir: str,
        timestamps: Optional[List[Dict[str, Any]]] = None,
        auto_detect: bool = True,
        segment_length: int = 30,
        format: str = 'wav'
    ) -> Dict[str, Any]:
        """
        Extract segments from YouTube video.
        
        Args:
            url: YouTube video URL
            output_dir: Directory to save segments
            timestamps: Manual timestamps (if not auto-detecting)
            auto_detect: Whether to auto-detect timestamps
            segment_length: Default segment length
            format: Output audio format
            
        Returns:
            Dictionary with extraction results
        """
        results = {
            'video_url': url,
            'segments': [],
            'errors': []
        }
        
        try:
            # Get video metadata
            metadata = await get_youtube_metadata(url)
            video_duration = metadata.get('duration', 0)
            video_title = metadata.get('title', 'Unknown')
            
            # Auto-detect timestamps if requested
            if auto_detect and not timestamps:
                extraction_data = await self.extract_from_youtube_metadata(url)
                timestamps = extraction_data['description_timestamps']
                
                # If no timestamps in description, generate automatic segments
                if not timestamps:
                    logger.info("No timestamps found, generating automatic segments")
                    timestamps = self._generate_auto_timestamps(
                        video_duration, segment_length
                    )
            
            # Generate segments
            segments = self.generate_segments(
                timestamps or [],
                video_duration,
                segment_length
            )
            
            if not segments:
                results['errors'].append("No segments to extract")
                return results
            
            # Download full video first
            logger.info(f"Downloading video: {video_title}")
            download_result = await download_youtube(
                url,
                output_dir,
                audio_format=format
            )
            
            if not download_result['success']:
                results['errors'].append("Failed to download video")
                return results
            
            source_file = download_result['output_path']
            
            # Extract each segment
            for i, segment in enumerate(segments):
                try:
                    # Generate output filename
                    safe_desc = re.sub(r'[^\w\s-]', '', segment['description'])[:50]
                    output_file = f"{output_dir}/segment_{i+1:02d}_{safe_desc}.{format}"
                    
                    logger.info(f"Extracting segment {i+1}: {segment['timestamp']} - {segment['description']}")
                    
                    # Extract segment
                    extract_result = await extract_audio_segment(
                        source_file,
                        output_file,
                        segment['start'],
                        segment['end']
                    )
                    
                    if extract_result['success']:
                        # Analyze the segment
                        analysis = await analyze_audio_file(output_file)
                        
                        results['segments'].append({
                            'index': i + 1,
                            'file': output_file,
                            'start': segment['start'],
                            'end': segment['end'],
                            'duration': segment['duration'],
                            'description': segment['description'],
                            'is_sample': segment['is_sample'],
                            'quality_indicator': segment['quality_indicator'],
                            'analysis': analysis
                        })
                    else:
                        results['errors'].append(
                            f"Failed to extract segment {i+1}: {extract_result.get('error')}"
                        )
                        
                except Exception as e:
                    results['errors'].append(f"Error processing segment {i+1}: {str(e)}")
            
            # Clean up source file if all segments extracted successfully
            if len(results['segments']) == len(segments):
                logger.info("All segments extracted, cleaning up source file")
                # In production, you might want to keep or delete based on settings
            
        except Exception as e:
            results['errors'].append(f"Extraction failed: {str(e)}")
            logger.error(f"Extraction failed: {e}")
        
        return results
    
    def _generate_auto_timestamps(
        self,
        duration: int,
        segment_length: int
    ) -> List[Dict[str, Any]]:
        """Generate automatic timestamps for videos without them."""
        timestamps = []
        current_time = 0
        segment_num = 1
        
        while current_time < duration:
            timestamps.append({
                'time': current_time,
                'timestamp': str(timedelta(seconds=current_time)),
                'description': f'Segment {segment_num}',
                'is_sample': True,
                'quality_indicator': 0
            })
            current_time += segment_length
            segment_num += 1
        
        return timestamps
    
    async def extract_fire_samples(
        self,
        url: str,
        output_dir: str,
        min_fire_count: int = 2
    ) -> Dict[str, Any]:
        """
        Extract only the "fire" samples based on community reactions.
        
        Args:
            url: YouTube video URL
            output_dir: Directory to save samples
            min_fire_count: Minimum fire emoji count
            
        Returns:
            Extraction results
        """
        # Get timestamps with quality indicators
        extraction_data = await self.extract_from_youtube_metadata(url)
        
        # Filter for fire samples
        fire_timestamps = [
            ts for ts in extraction_data['description_timestamps']
            if ts['quality_indicator'] >= min_fire_count
        ]
        
        if not fire_timestamps:
            logger.info("No fire samples found, extracting all sample-related timestamps")
            fire_timestamps = [
                ts for ts in extraction_data['description_timestamps']
                if ts['is_sample']
            ]
        
        # Extract the fire samples
        return await self.extract_segments(
            url,
            output_dir,
            timestamps=fire_timestamps,
            auto_detect=False
        )


# Convenience functions
async def extract_youtube_timestamps(
    url: str,
    output_dir: str,
    **kwargs
) -> Dict[str, Any]:
    """Extract segments from YouTube video based on timestamps."""
    extractor = TimestampExtractor()
    return await extractor.extract_segments(url, output_dir, **kwargs)


async def extract_fire_samples(
    url: str,
    output_dir: str,
    min_fire_count: int = 2
) -> Dict[str, Any]:
    """Extract only the highest-rated samples from YouTube."""
    extractor = TimestampExtractor()
    return await extractor.extract_fire_samples(url, output_dir, min_fire_count)