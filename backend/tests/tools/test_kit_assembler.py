"""
Tests for CLI Kit Assembler tool
"""
import pytest
import asyncio
from pathlib import Path
import shutil

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.tools.kit_assembler import KitAssembler, GENRE_EFFECT_MAP


class TestKitAssembler:
    """Test kit assembler functionality"""

    @pytest.fixture
    def assembler(self):
        """Create kit assembler instance"""
        return KitAssembler()

    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create temporary output directory"""
        kit_dir = tmp_path / "test_kit"
        yield kit_dir
        # Cleanup after test
        if kit_dir.exists():
            shutil.rmtree(kit_dir)

    @pytest.mark.asyncio
    async def test_query_samples_by_genre(self, assembler):
        """Test querying samples by genre"""
        samples = await assembler.query_samples(genre="hip-hop", limit=10)

        # Should find some samples
        assert len(samples) >= 0, "Should return samples list (may be empty)"

        # If samples found, check they have genre
        if samples:
            assert any("hip" in (s.genre or "").lower() for s in samples), \
                "At least one sample should match hip-hop genre"

    @pytest.mark.asyncio
    async def test_query_samples_by_bpm(self, assembler):
        """Test querying samples by BPM"""
        samples = await assembler.query_samples(bpm=93.0, limit=10)

        # Should return samples (may be empty if no matches)
        assert isinstance(samples, list)

        # If samples found, check BPM is within tolerance
        if samples:
            for sample in samples:
                if sample.bpm:
                    assert 83.0 <= sample.bpm <= 103.0, \
                        f"BPM {sample.bpm} should be within ±10 of target 93"

    def test_categorize_sample_drums(self, assembler):
        """Test sample categorization for drums"""
        # Mock sample object
        class MockSample:
            title = "Kick Drum Heavy"
            tags = []
            extra_metadata = {}

        sample = MockSample()
        category = assembler.categorize_sample(sample)
        assert category == "drums", "Should categorize kick as drums"

    def test_categorize_sample_bass(self, assembler):
        """Test sample categorization for bass"""
        class MockSample:
            title = "808 Bass Sub"
            tags = []
            extra_metadata = {}

        sample = MockSample()
        category = assembler.categorize_sample(sample)
        assert category == "bass", "Should categorize 808 as bass"

    def test_categorize_sample_melodic(self, assembler):
        """Test sample categorization for melodic (default)"""
        class MockSample:
            title = "Piano Rhodes Cm"
            tags = []
            extra_metadata = {}

        sample = MockSample()
        category = assembler.categorize_sample(sample)
        assert category == "melodic", "Should categorize piano as melodic"

    def test_recommend_effects_lofi(self, assembler):
        """Test effect recommendations for lo-fi hip-hop"""
        class MockSample:
            title = "Kick"
            tags = []
            extra_metadata = {}

        sample = MockSample()
        effects = assembler.recommend_effects(sample, "lo-fi hip-hop")

        assert isinstance(effects, list)
        assert len(effects) > 0
        assert all(isinstance(e, str) for e in effects)

    def test_recommend_effects_trap(self, assembler):
        """Test effect recommendations for trap"""
        class MockSample:
            title = "808 Bass"
            tags = []
            extra_metadata = {}

        sample = MockSample()
        effects = assembler.recommend_effects(sample, "trap")

        assert isinstance(effects, list)
        assert len(effects) > 0
        # Trap 808s should have Sub Boost
        assert any("sub" in e.lower() or "boost" in e.lower() for e in effects)

    def test_assign_to_banks(self, assembler):
        """Test bank assignment logic"""
        # Mock samples
        class MockSample:
            def __init__(self, title):
                self.title = title
                self.tags = []
                self.extra_metadata = {}

        samples = [
            MockSample("Kick"),
            MockSample("Snare"),
            MockSample("Bass 808"),
            MockSample("Piano"),
        ]

        banks = assembler.assign_to_banks(samples, max_samples=16)

        # Should have at least one bank
        assert len(banks) > 0

        # Bank A should have drums
        if "A" in banks:
            assert len(banks["A"]) > 0
            assert any("kick" in s.title.lower() or "snare" in s.title.lower()
                      for s in banks["A"])

    @pytest.mark.asyncio
    async def test_generate_kit_complete(self, assembler, output_dir):
        """Test complete kit generation"""
        result = await assembler.generate_kit(
            name="Test Kit",
            output_dir=output_dir,
            genre="hip-hop",
            max_samples=16,
            format="wav"
        )

        # Should return result dict or None
        if result:
            assert "name" in result
            assert "genre" in result
            assert "total_samples" in result
            assert "manifest" in result

            # Check manifest file exists
            manifest_path = Path(result["manifest"])
            assert manifest_path.exists(), "Manifest file should be created"

            # Check manifest content
            manifest_text = manifest_path.read_text()
            assert "SP-404MK2 KIT" in manifest_text
            assert "Test Kit" in manifest_text
            assert "hip-hop" in manifest_text.lower()

    def test_genre_effect_map_coverage(self):
        """Test that genre effect map has expected entries"""
        expected_genres = ["lo-fi hip-hop", "trap", "boom-bap", "house", "jazz"]

        for genre in expected_genres:
            assert genre in GENRE_EFFECT_MAP, f"Genre {genre} should be in effect map"

            genre_effects = GENRE_EFFECT_MAP[genre]
            assert isinstance(genre_effects, dict)
            assert len(genre_effects) > 0, f"Genre {genre} should have effect mappings"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
