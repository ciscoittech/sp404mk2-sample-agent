"""
Smart Kit Completion Service for intelligent drum kit assembly.

Analyzes a seed sample (melodic loop) and intelligently selects:
- 8 drum sounds (kicks, snares, toms, hats, percussion)
- 7 complementary melodic/harmonic samples

Uses metadata matching (BPM, key, genre, tags) for intelligent recommendations.
"""
import logging
from typing import List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from collections import Counter

from app.models.sample import Sample
from app.models.kit import KitSample

logger = logging.getLogger(__name__)

# Drum sound categorization by priority
DRUM_CATEGORIES = {
    "kicks": {
        "tags": ["kick"],
        "min_samples": 1,
        "max_samples": 2,
    },
    "snares": {
        "tags": ["snare"],
        "min_samples": 1,
        "max_samples": 2,
    },
    "toms": {
        "tags": ["tom"],
        "min_samples": 1,
        "max_samples": 2,
    },
    "hats": {
        "tags": ["hihat", "hat", "closed"],
        "min_samples": 1,
        "max_samples": 2,
    },
    "open_hats": {
        "tags": ["open hat", "open hihat"],
        "min_samples": 0,
        "max_samples": 1,
    },
    "percussion": {
        "tags": ["percussion", "perc", "conga", "clap"],
        "min_samples": 1,
        "max_samples": 2,
    },
}


class SmartKitCompletionService:
    """Intelligent kit assembly based on seed sample metadata."""

    async def complete_kit(
        self,
        db: AsyncSession,
        seed_sample_id: int,
        user_id: int,
        exclude_assigned: bool = True,
    ) -> Dict:
        """
        Build a complete kit around a seed sample.

        Returns 8 drum sounds + 7 complementary melodic samples.

        Args:
            db: Database session
            seed_sample_id: ID of the seed melodic sample
            user_id: User ID (for access control)
            exclude_assigned: Whether to exclude already-assigned samples

        Returns:
            Dict with:
            - seed_sample: The original seed sample
            - drum_sounds: List of 8 drum samples
            - melodic_samples: List of 7 complementary melodic samples
            - completion_notes: Explanation of selections
        """
        # Fetch seed sample
        result = await db.execute(
            select(Sample).where(
                and_(Sample.id == seed_sample_id, Sample.user_id == user_id)
            )
        )
        seed_sample = result.scalar_one_or_none()

        if not seed_sample:
            raise ValueError(f"Sample {seed_sample_id} not found")

        logger.info(
            f"Starting kit completion for seed sample: {seed_sample.title} "
            f"(BPM: {seed_sample.bpm}, Key: {seed_sample.musical_key})"
        )

        # Get excluded sample IDs if needed
        excluded_ids = {seed_sample_id}
        if exclude_assigned:
            result = await db.execute(
                select(KitSample.sample_id).where(
                    KitSample.kit.has(user_id=user_id)
                )
            )
            excluded_ids.update(result.scalars().all())

        # Build drum kit
        drum_sounds = await self._select_drum_sounds(
            db, seed_sample, user_id, excluded_ids
        )

        # Build melodic accompaniment
        melodic_samples = await self._select_melodic_samples(
            db, seed_sample, user_id, excluded_ids, target_count=7
        )

        notes = self._generate_completion_notes(
            seed_sample, drum_sounds, melodic_samples
        )

        return {
            "seed_sample": {
                "id": seed_sample.id,
                "title": seed_sample.title,
                "bpm": seed_sample.bpm,
                "musical_key": seed_sample.musical_key,
                "tags": seed_sample.tags,
            },
            "drum_sounds": [
                {
                    "id": s.id,
                    "title": s.title,
                    "tags": s.tags,
                    "category": self._categorize_drum_sample(s),
                }
                for s in drum_sounds
            ],
            "melodic_samples": [
                {
                    "id": s.id,
                    "title": s.title,
                    "bpm": s.bpm,
                    "musical_key": s.musical_key,
                    "tags": s.tags,
                }
                for s in melodic_samples
            ],
            "completion_notes": notes,
        }

    async def _select_drum_sounds(
        self,
        db: AsyncSession,
        seed_sample: Sample,
        user_id: int,
        excluded_ids: set,
    ) -> List[Sample]:
        """Select 8 complementary drum sounds."""
        drum_samples = []

        # Get all drum-related samples
        drum_tags = set()
        for category in DRUM_CATEGORIES.values():
            drum_tags.update(category["tags"])

        # Query for drum samples
        query = select(Sample).where(
            and_(
                Sample.user_id == user_id,
                Sample.id.notin_(excluded_ids),
            )
        )

        result = await db.execute(query)
        all_samples = result.scalars().all()

        # Filter to drum samples
        drum_candidates = [
            s for s in all_samples if self._has_drum_tags(s.tags, drum_tags)
        ]

        logger.debug(f"Found {len(drum_candidates)} drum candidates")

        # Select samples by category
        selected_by_category = {}
        for category_name, category_info in DRUM_CATEGORIES.items():
            category_samples = [
                s
                for s in drum_candidates
                if self._has_any_tag(s.tags, category_info["tags"])
                and s not in drum_samples
            ]

            # Take up to max_samples
            take_count = min(
                len(category_samples), category_info.get("max_samples", 1)
            )
            selected = category_samples[:take_count]
            selected_by_category[category_name] = selected
            drum_samples.extend(selected)

            logger.debug(f"  {category_name}: {len(selected)} selected")

        # Ensure we have at least 8 drum sounds
        if len(drum_samples) < 8:
            # Fill with remaining candidates
            remaining = [s for s in drum_candidates if s not in drum_samples]
            drum_samples.extend(remaining[: 8 - len(drum_samples)])

        return drum_samples[:8]

    async def _select_melodic_samples(
        self,
        db: AsyncSession,
        seed_sample: Sample,
        user_id: int,
        excluded_ids: set,
        target_count: int = 7,
    ) -> List[Sample]:
        """Select complementary melodic samples based on seed sample."""
        # Get BPM range for matching
        bpm_min = None
        bpm_max = None
        if seed_sample.bpm:
            bpm_min = seed_sample.bpm - 10
            bpm_max = seed_sample.bpm + 10

        # Build query
        query = select(Sample).where(
            and_(
                Sample.user_id == user_id,
                Sample.id.notin_(excluded_ids),
            )
        )

        # Filter by BPM if available
        if bpm_min and bpm_max:
            query = query.where(
                or_(
                    Sample.bpm.is_(None),
                    and_(Sample.bpm >= bpm_min, Sample.bpm <= bpm_max),
                )
            )

        # Exclude pure drum sounds
        drum_tags = set()
        for category in DRUM_CATEGORIES.values():
            drum_tags.update(category["tags"])

        result = await db.execute(query)
        candidates = result.scalars().all()

        # Filter out drum sounds
        melodic_candidates = [
            s for s in candidates if not self._has_drum_tags(s.tags, drum_tags)
        ]

        logger.debug(f"Found {len(melodic_candidates)} melodic candidates")

        # Score candidates by relevance
        scored_samples = []
        for sample in melodic_candidates:
            score = self._score_melodic_sample(sample, seed_sample)
            scored_samples.append((sample, score))

        # Sort by score (descending) and take top candidates
        scored_samples.sort(key=lambda x: x[1], reverse=True)
        melodic_samples = [s[0] for s in scored_samples[:target_count]]

        return melodic_samples

    def _score_melodic_sample(self, candidate: Sample, seed: Sample) -> float:
        """Score how well a sample complements the seed sample."""
        score = 0.0

        # BPM match (up to 30 points)
        if seed.bpm and candidate.bpm:
            bpm_diff = abs(candidate.bpm - seed.bpm)
            if bpm_diff <= 10:
                score += 30
            elif bpm_diff <= 20:
                score += 15
        elif candidate.bpm is None:
            score += 5  # Slight bonus for flexible tempo

        # Key match (up to 25 points)
        if seed.musical_key and candidate.musical_key:
            if seed.musical_key == candidate.musical_key:
                score += 25
            elif self._keys_compatible(seed.musical_key, candidate.musical_key):
                score += 15
        elif candidate.musical_key is None:
            score += 5  # Slight bonus for flexible key

        # Genre/tag match (up to 25 points)
        if seed.tags and candidate.tags:
            matching_tags = set(seed.tags) & set(candidate.tags)
            tag_score = min(25, len(matching_tags) * 5)
            score += tag_score
        elif candidate.tags:
            # Bonus for non-drum samples with clear metadata
            score += 10

        # Metadata completeness (up to 20 points)
        metadata_count = sum(
            [
                candidate.duration is not None,
                candidate.bpm is not None,
                candidate.musical_key is not None,
            ]
        )
        score += metadata_count * 6

        return score

    def _keys_compatible(self, key1: str, key2: str) -> bool:
        """Check if two musical keys are compatible."""
        if not key1 or not key2:
            return False

        # Extract root note (before space)
        root1 = key1.split()[0]
        root2 = key2.split()[0]

        # Same root is compatible
        if root1 == root2:
            return True

        # Relative major/minor (e.g., C major and A minor)
        relatives = {
            "C": ["A"],
            "A": ["C"],
            "G": ["E"],
            "E": ["G"],
            "D": ["B"],
            "B": ["D", "G#"],
            "A": ["F#"],
            "F#": ["A"],
            "F": ["D"],
            "D": ["B"],
        }

        return root2 in relatives.get(root1, [])

    def _categorize_drum_sample(self, sample: Sample) -> str:
        """Determine drum sample category."""
        if not sample.tags:
            return "percussion"

        for category_name, category_info in DRUM_CATEGORIES.items():
            if self._has_any_tag(sample.tags, category_info["tags"]):
                return category_name

        return "percussion"

    def _has_drum_tags(self, tags: List[str], drum_tags: set) -> bool:
        """Check if sample has any drum-related tags."""
        if not tags:
            return False
        return any(t.lower() in drum_tags for t in tags)

    def _has_any_tag(self, tags: List[str], search_tags: List[str]) -> bool:
        """Check if sample has any of the search tags."""
        if not tags:
            return False
        search_set = {t.lower() for t in search_tags}
        return any(t.lower() in search_set for t in tags)

    def _generate_completion_notes(
        self, seed: Sample, drums: List[Sample], melodics: List[Sample]
    ) -> List[str]:
        """Generate human-readable notes about the completion."""
        notes = []

        notes.append(
            f"Built kit around '{seed.title}' "
            f"({seed.bpm or '?'} BPM, {seed.musical_key or 'no key'} key)"
        )

        # Drum notes
        drum_counts = Counter(self._categorize_drum_sample(d) for d in drums)
        drum_desc = ", ".join(f"{count} {cat}" for cat, count in drum_counts.items())
        notes.append(f"Selected drum kit: {drum_desc}")

        # Melodic notes
        melodic_bpms = [m.bpm for m in melodics if m.bpm]
        if melodic_bpms:
            avg_bpm = sum(melodic_bpms) / len(melodic_bpms)
            notes.append(
                f"Melodic samples averaged {avg_bpm:.0f} BPM "
                f"(seed: {seed.bpm or '?'} BPM)"
            )

        melodic_keys = [m.musical_key for m in melodics if m.musical_key]
        if melodic_keys:
            notes.append(f"Melodic key matches: {', '.join(set(melodic_keys))}")

        return notes
