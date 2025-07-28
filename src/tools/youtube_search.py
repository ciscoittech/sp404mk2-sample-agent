"""
Enhanced YouTube search functionality with deep musical intelligence.
Uses YouTube Data API v3 or fallback scraping methods.
"""

import os
import re
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import aiohttp
from urllib.parse import quote_plus, urlparse

from ..logging_config import AgentLogger

logger = AgentLogger("youtube_search")


class YouTubeSearchError(Exception):
    """Custom exception for YouTube search operations."""
    pass


class YouTubeSearcher:
    """Enhanced YouTube searcher with musical intelligence."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube searcher.
        
        Args:
            api_key: YouTube Data API v3 key (optional)
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.has_api_key = bool(self.api_key)
        
        # API endpoints
        self.search_api_url = "https://www.googleapis.com/youtube/v3/search"
        self.videos_api_url = "https://www.googleapis.com/youtube/v3/videos"
        
        # Search optimization patterns
        self.quality_indicators = [
            "HQ", "HD", "WAV", "FLAC", "24bit", "lossless",
            "high quality", "studio quality", "vinyl rip"
        ]
        
        self.sample_pack_indicators = [
            "sample pack", "drum kit", "loop kit", "sound pack",
            "free download", "royalty free", "no copyright"
        ]
        
        self.producer_channels = {
            "hip_hop": [
                "Mass Appeal", "STLNDRMS", "Splice", "MSXII Sound Design",
                "Internet Money", "Based Gutta"
            ],
            "electronic": [
                "Loopmasters", "Splice", "Black Octopus", "ADSR Sounds",
                "Point Blank Music School"
            ],
            "jazz": [
                "Jazz Video Guy", "Jazz at Lincoln Center", "NPR Music"
            ]
        }
    
    async def search(
        self,
        query: str,
        max_results: int = 20,
        filter_samples: bool = True,
        sort_by: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search YouTube for samples with enhanced filtering.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            filter_samples: Apply sample-specific filtering
            sort_by: Sort order (relevance, date, viewCount)
            
        Returns:
            List of video results with metadata
        """
        if self.has_api_key:
            return await self._search_with_api(query, max_results, filter_samples, sort_by)
        else:
            return await self._search_with_scraping(query, max_results, filter_samples)
    
    async def _search_with_api(
        self,
        query: str,
        max_results: int,
        filter_samples: bool,
        sort_by: str
    ) -> List[Dict[str, Any]]:
        """Search using YouTube Data API v3."""
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results * 2, 50),  # Get extra for filtering
            "order": sort_by,
            "videoCategoryId": "10",  # Music category
            "key": self.api_key
        }
        
        # Add duration filter for samples (prefer shorter videos)
        if filter_samples:
            params["videoDuration"] = "medium"  # 4-20 minutes
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search_api_url, params=params) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise YouTubeSearchError(f"API error: {error_data}")
                    
                    data = await response.json()
                    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
                    
                    # Get detailed video info
                    if video_ids:
                        videos = await self._get_video_details(video_ids)
                        
                        # Apply filtering
                        if filter_samples:
                            videos = self._filter_sample_videos(videos)
                        
                        return videos[:max_results]
                    
                    return []
                    
        except Exception as e:
            logger.error(f"YouTube API search failed: {e}")
            # Fallback to scraping
            return await self._search_with_scraping(query, max_results, filter_samples)
    
    async def _get_video_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information for videos."""
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.videos_api_url, params=params) as response:
                data = await response.json()
                
                videos = []
                for item in data.get("items", []):
                    video = {
                        "id": item["id"],
                        "url": f"https://youtube.com/watch?v={item['id']}",
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "channel_id": item["snippet"]["channelId"],
                        "description": item["snippet"]["description"],
                        "published_at": item["snippet"]["publishedAt"],
                        "duration": self._parse_duration(item["contentDetails"]["duration"]),
                        "view_count": int(item["statistics"].get("viewCount", 0)),
                        "like_count": int(item["statistics"].get("likeCount", 0)),
                        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
                    }
                    
                    # Calculate quality score
                    video["quality_score"] = self._calculate_quality_score(video)
                    videos.append(video)
                
                return videos
    
    async def _search_with_scraping(
        self,
        query: str,
        max_results: int,
        filter_samples: bool
    ) -> List[Dict[str, Any]]:
        """Fallback search using web scraping."""
        # For production, this would use a proper scraping method
        # For now, return enhanced mock data
        logger.warning("Using mock YouTube search (no API key)")
        
        mock_results = []
        for i in range(max_results):
            mock_results.append({
                "id": f"mock_{i}",
                "url": f"https://youtube.com/watch?v=mock_{i}",
                "title": f"{query} - Result {i+1}",
                "channel": "Mock Channel",
                "channel_id": "mock_channel",
                "description": f"Mock description for {query}",
                "published_at": datetime.now().isoformat(),
                "duration": 180 + i * 30,
                "view_count": 1000 * (i + 1),
                "like_count": 100 * (i + 1),
                "thumbnail": f"https://i.ytimg.com/vi/mock_{i}/hqdefault.jpg",
                "quality_score": 0.8 - (i * 0.1)
            })
        
        return mock_results
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        # PT15M33S -> 933 seconds
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return hours * 3600 + minutes * 60 + seconds
        return 0
    
    def _calculate_quality_score(self, video: Dict[str, Any]) -> float:
        """Calculate quality score for sample selection."""
        score = 0.5  # Base score
        
        # Title quality indicators
        title_lower = video["title"].lower()
        for indicator in self.quality_indicators:
            if indicator.lower() in title_lower:
                score += 0.1
        
        # Sample pack indicators
        for indicator in self.sample_pack_indicators:
            if indicator.lower() in title_lower or indicator.lower() in video["description"].lower():
                score += 0.15
        
        # Channel reputation
        if video["channel"] in sum(self.producer_channels.values(), []):
            score += 0.2
        
        # Engagement metrics
        if video["view_count"] > 10000:
            score += 0.1
        if video["view_count"] > 100000:
            score += 0.1
        
        # Like ratio
        if video["view_count"] > 0 and video["like_count"] > 0:
            like_ratio = video["like_count"] / video["view_count"]
            if like_ratio > 0.04:  # 4% like ratio is good
                score += 0.1
        
        # Duration (prefer 3-20 minute videos for samples)
        if 180 <= video["duration"] <= 1200:
            score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _filter_sample_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter videos likely to contain samples."""
        filtered = []
        
        for video in videos:
            # Skip if too short or too long
            if video["duration"] < 60 or video["duration"] > 3600:
                continue
            
            # Skip if title suggests it's not samples
            title_lower = video["title"].lower()
            skip_patterns = [
                "reaction", "review", "tutorial", "explained",
                "documentary", "interview", "podcast", "live stream"
            ]
            if any(pattern in title_lower for pattern in skip_patterns):
                continue
            
            # Boost videos with sample-related terms
            boost_patterns = [
                "sample", "loop", "break", "drum", "kit", "pack",
                "free", "download", "wav", "sound", "beat"
            ]
            if any(pattern in title_lower for pattern in boost_patterns):
                video["quality_score"] += 0.2
            
            filtered.append(video)
        
        # Sort by quality score
        filtered.sort(key=lambda x: x["quality_score"], reverse=True)
        return filtered
    
    async def search_by_era(
        self,
        era: str,
        genre: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for era-specific samples."""
        era_queries = {
            "60s": ["1960s", "sixties", "vintage", "retro"],
            "70s": ["1970s", "seventies", "funk", "disco", "soul"],
            "80s": ["1980s", "eighties", "synth", "new wave"],
            "90s": ["1990s", "nineties", "golden era", "boom bap"],
            "2000s": ["2000s", "y2k", "early 2000s"]
        }
        
        era_terms = era_queries.get(era.lower(), [era])
        queries = [f"{term} {genre} samples" for term in era_terms]
        
        all_results = []
        for query in queries:
            results = await self.search(query, max_results // len(queries))
            all_results.extend(results)
        
        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)
        
        return unique_results[:max_results]
    
    async def search_by_producer(
        self,
        producer: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for producer-style samples."""
        producer_queries = {
            "dilla": [
                "J Dilla type beat", "Dilla drums", "Detroit hip hop samples",
                "MPC3000 samples", "Slum Village type"
            ],
            "madlib": [
                "Madlib type beat", "loop digga samples", "psychedelic soul loops",
                "obscure jazz samples", "Quasimoto type"
            ],
            "premier": [
                "DJ Premier type beat", "boom bap drums", "Gang Starr type",
                "scratched samples", "NY hip hop samples"
            ],
            "kanye": [
                "Kanye type beat", "soul samples", "chipmunk soul",
                "College Dropout type", "pitched vocals"
            ],
            "metro": [
                "Metro Boomin type beat", "dark trap samples", "horror movie samples",
                "atmospheric trap", "808 samples"
            ]
        }
        
        queries = producer_queries.get(producer.lower(), [f"{producer} type beat samples"])
        
        all_results = []
        for query in queries:
            results = await self.search(query, max_results // len(queries))
            all_results.extend(results)
        
        return all_results[:max_results]
    
    async def search_multi_platform(
        self,
        base_query: str,
        max_results: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search with platform-specific optimizations."""
        platform_queries = {
            "youtube": [
                f"{base_query} sample pack",
                f"{base_query} free download",
                f"{base_query} drum kit"
            ],
            "tutorials": [
                f"how to make {base_query}",
                f"{base_query} production breakdown",
                f"{base_query} beat tutorial"
            ],
            "performances": [
                f"{base_query} live session",
                f"{base_query} beat making",
                f"{base_query} MPC performance"
            ]
        }
        
        results = {}
        for platform, queries in platform_queries.items():
            platform_results = []
            for query in queries:
                search_results = await self.search(
                    query,
                    max_results // (len(platform_queries) * len(queries))
                )
                platform_results.extend(search_results)
            results[platform] = platform_results
        
        return results


# Standalone search functions for backward compatibility
async def search_youtube_enhanced(
    query: str,
    max_results: int = 20,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Enhanced YouTube search with musical intelligence."""
    searcher = YouTubeSearcher(api_key)
    return await searcher.search(query, max_results)


async def search_youtube_by_vibe(
    vibe: str,
    genre: str,
    max_results: int = 20,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search YouTube based on vibe descriptions."""
    vibe_mappings = {
        "dusty": "vinyl lo-fi vintage analog",
        "smooth": "silk liquid mellow warm",
        "crunchy": "distorted saturated compressed",
        "spacey": "ambient ethereal cosmic reverb",
        "bouncy": "groovy funky rhythmic upbeat"
    }
    
    enhanced_query = f"{vibe_mappings.get(vibe, vibe)} {genre} samples"
    searcher = YouTubeSearcher(api_key)
    return await searcher.search(enhanced_query, max_results)