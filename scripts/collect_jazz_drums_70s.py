#!/usr/bin/env python3
"""
Jazz Drum Breaks Collection Script
Demonstrates the enhanced SP404MK2 Sample Agent system
for GitHub Issue #12: Jazz drum breaks from 1970s
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.tools.youtube_search import YouTubeSearcher
from src.tools.timestamp_extractor import TimestampExtractor
from src.agents.groove_analyst import analyze_groove
from src.agents.era_expert import analyze_era, get_era_search_queries
from src.agents.sample_relationship import analyze_sample_compatibility
from src.tools.intelligent_organizer import organize_samples
from src.chat.musical_understanding import MusicalUnderstanding


class JazzDrumCollector:
    """Specialized collector for 1970s jazz drum breaks."""
    
    def __init__(self, output_dir: str = "jazz_drums_70s"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.youtube_searcher = YouTubeSearcher()
        self.timestamp_extractor = TimestampExtractor()
        self.musical_understanding = MusicalUnderstanding()
        
        # Collection parameters from issue
        self.target_style = "Jazz"
        self.target_era = "1970s"
        self.target_bpm = (80, 100)
        self.target_count = 20
        
    async def collect_samples(self):
        """Main collection workflow."""
        print("🎵 SP404MK2 Sample Agent - Jazz Drum Breaks Collection")
        print("=" * 60)
        print(f"Target: {self.target_style} drum breaks from {self.target_era}")
        print(f"BPM Range: {self.target_bpm[0]}-{self.target_bpm[1]}")
        print(f"Target Count: {self.target_count} samples")
        print("=" * 60)
        
        # Step 1: Generate era-specific search queries
        print("\n📚 Step 1: Generating era-specific search queries...")
        search_queries = await get_era_search_queries(
            era=self.target_era,
            genre=self.target_style.lower(),
            base_query="drum breaks drum solo"
        )
        
        # Add specific 70s jazz references
        search_queries.extend([
            "Billy Cobham drum solo 1970s",
            "Tony Williams drum break",
            "Buddy Rich drum solo 1974",
            "Art Blakey press roll 1970s",
            "Elvin Jones drum break",
            "Max Roach drum solo bebop",
            "jazz fusion drum break 1970s"
        ])
        
        print(f"Generated {len(search_queries)} search queries")
        for i, query in enumerate(search_queries[:5], 1):
            print(f"  {i}. {query}")
        
        # Step 2: Search YouTube with quality scoring
        print("\n🔍 Step 2: Searching YouTube with quality scoring...")
        all_videos = []
        
        for query in search_queries[:5]:  # Limit to first 5 queries
            print(f"\nSearching: {query}")
            try:
                videos = await self.youtube_searcher.search(
                    query=query,
                    max_results=10,
                    quality_threshold=0.5
                )
                all_videos.extend(videos)
                print(f"  Found {len(videos)} quality videos")
            except Exception as e:
                print(f"  Error: {str(e)}")
        
        # Sort by quality score
        all_videos.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        print(f"\nTotal videos found: {len(all_videos)}")
        
        # Step 3: Extract samples with timestamp detection
        print("\n⏱️ Step 3: Extracting samples with timestamp detection...")
        extracted_samples = []
        
        for video in all_videos[:10]:  # Process top 10 videos
            print(f"\nProcessing: {video['title'][:60]}...")
            print(f"  Quality Score: {video.get('quality_score', 0):.2f}")
            
            try:
                # Check for timestamps
                timestamps = await self.timestamp_extractor.extract_timestamps(
                    video["url"]
                )
                
                if timestamps:
                    print(f"  Found {len(timestamps)} timestamps")
                    # Extract high-quality segments
                    quality_timestamps = [
                        ts for ts in timestamps 
                        if ts.get("fire_count", 0) >= 2
                    ][:3]  # Top 3 segments
                    
                    if quality_timestamps:
                        output_path = self.output_dir / f"{video['id']}_segments"
                        await self.timestamp_extractor.extract_segments(
                            url=video["url"],
                            output_dir=str(output_path),
                            timestamps=quality_timestamps
                        )
                        
                        # Add extracted files to list
                        for segment_file in output_path.glob("*.wav"):
                            extracted_samples.append(str(segment_file))
                else:
                    # Extract full video if no timestamps
                    print("  No timestamps found, extracting full audio...")
                    # Would implement full extraction here
                    
            except Exception as e:
                print(f"  Extraction error: {str(e)}")
        
        print(f"\nExtracted {len(extracted_samples)} samples")
        
        # Step 4: Analyze with specialized agents
        print("\n🔬 Step 4: Analyzing samples with specialized agents...")
        
        # Groove analysis
        print("\n🥁 Analyzing groove characteristics...")
        groove_results = await analyze_groove(
            file_paths=extracted_samples[:self.target_count],
            analysis_depth="standard",
            reference_artists=["Art Blakey", "Tony Williams", "Elvin Jones"]
        )
        
        # Filter by BPM range
        valid_samples = []
        for analysis in groove_results.get("analyses", []):
            bpm = analysis["bpm"]
            if self.target_bpm[0] <= bpm <= self.target_bpm[1]:
                valid_samples.append(analysis["file_path"])
                print(f"  ✓ {Path(analysis['file_path']).name}: {bpm:.1f} BPM, "
                      f"{analysis['groove_type']}, "
                      f"{analysis['swing_percentage']:.1f}% swing")
            else:
                print(f"  ✗ {Path(analysis['file_path']).name}: {bpm:.1f} BPM (out of range)")
        
        # Era verification
        print("\n📅 Verifying era authenticity...")
        era_results = await analyze_era(
            file_paths=valid_samples,
            target_era=self.target_era,
            genre=self.target_style.lower()
        )
        
        era_confirmed = []
        for analysis in era_results.get("analyses", []):
            if analysis.get("detected_era") == self.target_era:
                era_confirmed.append(analysis["file_path"])
                print(f"  ✓ {Path(analysis['file_path']).name}: "
                      f"Confirmed {self.target_era} "
                      f"({analysis.get('confidence', 0):.1%} confidence)")
        
        # Step 5: Check sample relationships
        print("\n🔗 Step 5: Analyzing sample compatibility...")
        if len(era_confirmed) > 1:
            # Create pairs for compatibility analysis
            pairs = []
            for i in range(len(era_confirmed) - 1):
                pairs.append((era_confirmed[i], era_confirmed[i + 1]))
            
            compatibility_results = await analyze_sample_compatibility(
                sample_pairs=pairs[:5],  # Check first 5 pairs
                genre="jazz"
            )
            
            print("\nCompatibility Results:")
            for analysis in compatibility_results.get("analyses", []):
                score = analysis["overall_score"]
                print(f"  {Path(analysis['sample1_path']).name} + "
                      f"{Path(analysis['sample2_path']).name}: "
                      f"{score}/10")
        
        # Step 6: Intelligent organization
        print("\n📁 Step 6: Organizing samples intelligently...")
        
        # Use multiple organization strategies
        org_result = await organize_samples(
            sample_paths=era_confirmed[:self.target_count],
            strategy="groove",  # Organize by groove style
            output_dir=str(self.output_dir / "organized")
        )
        
        print("\nOrganization Summary:")
        for folder, files in org_result["organization_plan"].items():
            print(f"  {folder}: {len(files)} samples")
        
        # Step 7: Generate collection report
        print("\n📊 Step 7: Generating collection report...")
        report = self._generate_report(
            search_queries=search_queries,
            videos_found=len(all_videos),
            samples_extracted=len(extracted_samples),
            samples_validated=len(era_confirmed),
            groove_results=groove_results,
            era_results=era_results,
            organization=org_result
        )
        
        report_path = self.output_dir / f"collection_report_{datetime.now():%Y%m%d_%H%M%S}.md"
        report_path.write_text(report)
        print(f"\nReport saved to: {report_path}")
        
        # Step 8: Update GitHub issue
        print("\n📝 Step 8: Updating GitHub issue...")
        self._update_github_issue(
            samples_collected=len(era_confirmed),
            report_path=str(report_path)
        )
        
        print("\n✅ Collection complete!")
        print(f"Successfully collected {len(era_confirmed)} jazz drum breaks from the 1970s")
        
        return {
            "samples_collected": era_confirmed,
            "organization": org_result,
            "report_path": str(report_path)
        }
    
    def _generate_report(self, **kwargs) -> str:
        """Generate a detailed collection report."""
        report = f"""# Jazz Drum Breaks Collection Report

**Date**: {datetime.now():%Y-%m-%d %H:%M:%S}
**Target**: Jazz drum breaks from 1970s
**BPM Range**: {self.target_bpm[0]}-{self.target_bpm[1]}

## Collection Summary

- **Search Queries Generated**: {len(kwargs['search_queries'])}
- **Videos Found**: {kwargs['videos_found']}
- **Samples Extracted**: {kwargs['samples_extracted']}
- **Samples Validated**: {kwargs['samples_validated']}

## Groove Analysis Summary

"""
        # Add groove analysis details
        if 'groove_results' in kwargs and 'summary' in kwargs['groove_results']:
            summary = kwargs['groove_results']['summary']
            report += f"- **Average Swing**: {summary.get('average_swing', 0):.1f}%\n"
            report += f"- **Dominant Groove**: {summary.get('dominant_groove', 'N/A')}\n"
        
        report += "\n## Era Verification\n\n"
        
        # Add era details
        if 'era_results' in kwargs and 'summary' in kwargs['era_results']:
            summary = kwargs['era_results']['summary']
            report += f"- **Confirmed 1970s**: {summary.get('detected_eras', {}).get('1970s', 0)} samples\n"
        
        report += "\n## Organization Structure\n\n"
        
        # Add organization details
        if 'organization' in kwargs:
            for folder, files in kwargs['organization']['organization_plan'].items():
                report += f"- **{folder}**: {len(files)} samples\n"
        
        report += "\n## Next Steps\n\n"
        report += "1. Review samples in organized folders\n"
        report += "2. Load favorites into SP-404MK2\n"
        report += "3. Create kit using compatibility analysis\n"
        
        return report
    
    def _update_github_issue(self, samples_collected: int, report_path: str):
        """Update the GitHub issue with results."""
        comment = f"""✅ Sample collection completed!

**Results**:
- Collected {samples_collected} jazz drum breaks from the 1970s
- All samples verified for era authenticity
- Samples organized by groove characteristics
- Full report available at: {report_path}

The enhanced agent system successfully:
1. Generated era-specific search queries
2. Scored YouTube videos for quality
3. Extracted timestamp-based segments
4. Analyzed groove characteristics
5. Verified 1970s production style
6. Organized samples intelligently

Ready for review and SP-404MK2 loading!"""
        
        # Would run: gh issue comment 12 --body "{comment}"
        print("\nGitHub issue comment prepared (not submitted in test mode)")


async def main():
    """Run the jazz drum collection workflow."""
    collector = JazzDrumCollector()
    
    try:
        results = await collector.collect_samples()
        return results
    except Exception as e:
        print(f"\n❌ Collection failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Note: This is a demonstration script
    # Actual execution would require:
    # 1. YouTube API or yt-dlp setup
    # 2. Audio files for analysis
    # 3. Write permissions for organization
    
    print("\n🎵 Jazz Drum Breaks Collection Demo")
    print("This demonstrates how the enhanced agent system would work.")
    print("\nIn production, this would:")
    print("- Search YouTube for 1970s jazz drum content")
    print("- Extract high-quality segments")
    print("- Analyze and organize samples")
    print("- Update GitHub issue with results")
    
    # Uncomment to run actual collection:
    # asyncio.run(main())