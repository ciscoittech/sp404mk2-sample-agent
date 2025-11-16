"""
CLI tool for assembling SP-404MK2 kits from sample database.

Auto-generates kits with smart sample selection, effect recommendations,
and exports to folder with manifest file.
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from shutil import copy2

# Add backend to path for DB access
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.sample import Sample
from app.core.config import settings


# SP-404MK2 Effect recommendations by genre
GENRE_EFFECT_MAP = {
    "lo-fi hip-hop": {
        "drums": ["Vinyl Sim", "Compressor", "Lo-Fi"],
        "melodic": ["Chorus", "Tape Delay", "Reverb"],
        "bass": ["Sub Boost", "Compressor"],
        "texture": ["Lo-Fi", "Reverb", "Filter"]
    },
    "trap": {
        "drums": ["Compressor", "Distortion", "Hard Clip"],
        "808": ["Sub Boost", "Distortion"],
        "hi-hats": ["Bit Crusher", "Filter"],
        "melodic": ["Reverb", "Delay"]
    },
    "boom-bap": {
        "drums": ["Vinyl Sim", "Compressor", "EQ"],
        "bass": ["Sub Boost", "Compressor"],
        "melodic": ["Chorus", "Reverb"],
        "scratch": ["DJ Looper", "Phaser"]
    },
    "house": {
        "drums": ["Compressor", "Sidechain", "Filter"],
        "bass": ["Sub Boost", "Distortion"],
        "melodic": ["Chorus", "Delay", "Reverb"],
        "synth": ["Phaser", "Flanger"]
    },
    "jazz": {
        "drums": ["Vintage Comp", "EQ"],
        "bass": ["Sub Boost"],
        "melodic": ["Chorus", "Reverb"],
        "brass": ["Reverb", "Tape Sat"]
    }
}


class KitAssembler:
    """Assembles SP-404MK2 kits from sample database"""

    def __init__(self, db_path: str = None):
        """Initialize with database connection"""
        if db_path is None:
            # Try root directory first, then backend
            root_db = Path(__file__).parent.parent.parent / "sp404_samples.db"
            backend_db = Path(__file__).parent.parent.parent / "backend" / "sp404_samples.db"

            if root_db.exists():
                db_path = str(root_db)
            elif backend_db.exists():
                db_path = str(backend_db)
            else:
                db_path = str(backend_db)  # Default to backend path

        db_url = f"sqlite+aiosqlite:///{db_path}"
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def query_samples(
        self,
        genre: Optional[str] = None,
        bpm: Optional[float] = None,
        key: Optional[str] = None,
        limit: int = 50
    ) -> List[Sample]:
        """Query samples from database with filters"""
        async with self.async_session() as session:
            query = select(Sample)

            filters = []

            # Genre filter (simple text search in genre field)
            if genre:
                filters.append(Sample.genre.ilike(f"%{genre}%"))

            # BPM filter (±10 BPM tolerance)
            if bpm:
                filters.append(
                    and_(
                        Sample.bpm >= bpm - 10,
                        Sample.bpm <= bpm + 10
                    )
                )

            # Key filter
            if key:
                filters.append(Sample.musical_key == key)

            if filters:
                query = query.where(and_(*filters))

            query = query.limit(limit)

            result = await session.execute(query)
            samples = list(result.scalars().all())

            # Post-filter by vibe analysis genre if no matches yet
            if genre and not samples:
                # Fallback: get all samples and filter in Python
                query = select(Sample).limit(limit)
                result = await session.execute(query)
                all_samples = list(result.scalars().all())

                # Filter by vibe analysis genre
                samples = [
                    s for s in all_samples
                    if s.extra_metadata and
                       isinstance(s.extra_metadata.get("vibe_analysis"), dict) and
                       genre.lower() in str(s.extra_metadata["vibe_analysis"].get("genre", "")).lower()
                ]

            return samples

    def categorize_sample(self, sample: Sample) -> str:
        """Categorize sample by type (drums, melodic, bass, texture)"""
        # Check vibe analysis
        vibe = sample.extra_metadata.get("vibe_analysis", {})
        descriptors = vibe.get("descriptors", [])

        # Check tags
        tags_lower = [t.lower() for t in sample.tags]

        # Drums detection
        drum_keywords = ["kick", "snare", "hat", "drum", "perc", "clap", "rim"]
        if any(kw in sample.title.lower() for kw in drum_keywords):
            return "drums"
        if any(kw in tags_lower for kw in drum_keywords):
            return "drums"

        # Bass detection
        bass_keywords = ["bass", "808", "sub"]
        if any(kw in sample.title.lower() for kw in bass_keywords):
            return "bass"
        if any(kw in tags_lower for kw in bass_keywords):
            return "bass"

        # Texture/FX detection
        texture_keywords = ["ambient", "pad", "atmosphere", "texture", "fx"]
        if any(kw in descriptors for kw in ["atmospheric", "ambient", "ethereal"]):
            return "texture"
        if any(kw in sample.title.lower() for kw in texture_keywords):
            return "texture"

        # Default to melodic
        return "melodic"

    def recommend_effects(self, sample: Sample, genre: str) -> List[str]:
        """Recommend effect chain for sample based on genre and type"""
        category = self.categorize_sample(sample)

        # Get genre-specific effects
        genre_lower = genre.lower().replace(" ", "-")
        genre_map = GENRE_EFFECT_MAP.get(genre_lower, {})

        # Try to match category
        effects = genre_map.get(category)

        # Fallback to generic effects
        if not effects:
            if category == "drums":
                effects = ["Compressor", "EQ"]
            elif category == "bass":
                effects = ["Sub Boost", "Compressor"]
            elif category == "melodic":
                effects = ["Reverb", "Chorus"]
            else:
                effects = ["Reverb", "Delay"]

        return effects

    def assign_to_banks(
        self,
        samples: List[Sample],
        max_samples: int = 16
    ) -> Dict[str, List[Sample]]:
        """Assign samples to SP-404 banks (A, B, C, D)"""
        # Categorize all samples
        categorized = {
            "drums": [],
            "bass": [],
            "melodic": [],
            "texture": []
        }

        for sample in samples:
            category = self.categorize_sample(sample)
            categorized[category].append(sample)

        # Assign to banks
        banks = {"A": [], "B": [], "C": [], "D": []}

        # Bank A: Drums (up to 16 pads)
        banks["A"] = categorized["drums"][:16]

        # Bank B: Melodic + Bass
        banks["B"] = (categorized["melodic"] + categorized["bass"])[:16]

        # Bank C: Texture + overflow
        banks["C"] = categorized["texture"][:16]

        # Bank D: Variations/overflow
        overflow = (
            categorized["drums"][16:] +
            categorized["melodic"][16:] +
            categorized["bass"][16:]
        )
        banks["D"] = overflow[:16]

        # Remove empty banks
        banks = {k: v for k, v in banks.items() if v}

        return banks

    async def generate_kit(
        self,
        name: str,
        output_dir: Path,
        genre: str = "hip-hop",
        bpm: Optional[float] = None,
        key: Optional[str] = None,
        max_samples: int = 16,
        format: str = "wav"
    ) -> Dict[str, Any]:
        """Generate a complete kit"""
        print(f"\n🎵 Generating SP-404MK2 Kit: {name}")
        print(f"Genre: {genre}")
        if bpm:
            print(f"BPM: {bpm}")
        if key:
            print(f"Key: {key}")
        print()

        # Query samples
        print("📦 Querying sample database...")
        samples = await self.query_samples(genre=genre, bpm=bpm, key=key, limit=50)

        if not samples:
            print(f"❌ No samples found matching criteria")
            return None

        print(f"✅ Found {len(samples)} matching samples")

        # Assign to banks
        print("🎹 Assigning samples to banks...")
        banks = self.assign_to_banks(samples, max_samples)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export samples and generate manifest
        manifest_lines = [
            f"SP-404MK2 KIT: {name}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Genre: {genre}",
            f"Total Samples: {sum(len(pads) for pads in banks.values())}",
            ""
        ]

        total_exported = 0

        for bank_name, bank_samples in banks.items():
            manifest_lines.append(f"=== BANK {bank_name} ===")

            for pad_num, sample in enumerate(bank_samples, 1):
                # Copy WAV file
                source_path = Path(sample.file_path)
                dest_filename = f"bank{bank_name}_pad{pad_num:02d}_{source_path.stem}.{format}"
                dest_path = output_dir / dest_filename

                try:
                    copy2(source_path, dest_path)
                    total_exported += 1
                except Exception as e:
                    print(f"⚠️  Failed to copy {sample.title}: {e}")
                    continue

                # Get vibe analysis
                vibe = sample.extra_metadata.get("vibe_analysis", {})
                mood = vibe.get("mood_primary", "N/A")
                descriptors = ", ".join(vibe.get("descriptors", [])[:3])

                # Recommend effects
                effects = self.recommend_effects(sample, genre)
                effect_chain = " → ".join(effects)

                # Add to manifest
                manifest_lines.extend([
                    f"Pad {pad_num}: {dest_filename}",
                    f"  - Title: {sample.title}",
                    f"  - Sample ID: {sample.id}",
                    f"  - BPM: {sample.bpm or 'N/A'}, Key: {sample.musical_key or 'N/A'}",
                    f"  - Effect Chain: {effect_chain}",
                    f"  - Vibe: {mood}, {descriptors}",
                    ""
                ])

            manifest_lines.append("")

        # Write manifest
        manifest_path = output_dir / "kit_manifest.txt"
        manifest_path.write_text("\n".join(manifest_lines))

        print(f"\n✅ Kit generated successfully!")
        print(f"📁 Output: {output_dir}")
        print(f"🎵 Exported {total_exported} samples across {len(banks)} banks")
        print(f"📄 Manifest: {manifest_path}")

        return {
            "name": name,
            "genre": genre,
            "output_dir": str(output_dir),
            "total_samples": total_exported,
            "banks": len(banks),
            "manifest": str(manifest_path)
        }


async def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate SP-404MK2 kits from sample database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m src.tools.kit_assembler --genre "lo-fi hip-hop" --output ./my_kit

  # With BPM and key
  python -m src.tools.kit_assembler --genre "trap" --bpm 140 --key "Cm" --output ./trap_kit

  # Custom sample count
  python -m src.tools.kit_assembler --genre "jazz" --samples 32 --output ./jazz_kit
        """
    )

    parser.add_argument(
        "--genre", "-g",
        type=str,
        required=True,
        help="Genre for kit (e.g., 'lo-fi hip-hop', 'trap', 'jazz')"
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for kit files"
    )

    parser.add_argument(
        "--name", "-n",
        type=str,
        help="Kit name (default: derived from genre)"
    )

    parser.add_argument(
        "--bpm", "-b",
        type=float,
        help="Target BPM (±10 tolerance)"
    )

    parser.add_argument(
        "--key", "-k",
        type=str,
        help="Musical key (e.g., 'Cm', 'F#')"
    )

    parser.add_argument(
        "--samples", "-s",
        type=int,
        default=16,
        help="Maximum samples per bank (default: 16)"
    )

    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["wav", "aiff"],
        default="wav",
        help="Output format (default: wav)"
    )

    args = parser.parse_args()

    # Default kit name
    if not args.name:
        args.name = args.genre.title().replace("-", " ")

    # Initialize assembler
    assembler = KitAssembler()

    # Generate kit
    result = await assembler.generate_kit(
        name=args.name,
        output_dir=args.output,
        genre=args.genre,
        bpm=args.bpm,
        key=args.key,
        max_samples=args.samples,
        format=args.format
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
