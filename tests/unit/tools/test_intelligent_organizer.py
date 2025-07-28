"""
Unit tests for Intelligent Organizer Tool.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import shutil

from src.tools.intelligent_organizer import IntelligentOrganizer


class TestIntelligentOrganizer:
    """Test suite for Intelligent Organizer Tool."""
    
    @pytest.fixture
    def organizer(self, temp_output_dir):
        """Create an intelligent organizer instance."""
        return IntelligentOrganizer(str(temp_output_dir))
    
    @pytest.fixture
    def mock_sample_metadata(self):
        """Mock sample metadata for testing."""
        return [
            {
                "path": "/samples/kick_90bpm_Cmaj.wav",
                "filename": "kick_90bpm_Cmaj.wav",
                "bpm": 90.0,
                "key": "C major",
                "type": "drums",
                "genre": "hip-hop",
                "energy": 0.8,
                "groove_type": "boom_bap",
                "era": "1990s"
            },
            {
                "path": "/samples/bass_120bpm_Gmaj.wav",
                "filename": "bass_120bpm_Gmaj.wav",
                "bpm": 120.0,
                "key": "G major",
                "type": "bass",
                "genre": "house",
                "energy": 0.7,
                "groove_type": "four_on_floor",
                "era": "2000s-2010s"
            },
            {
                "path": "/samples/snare_93bpm.wav",
                "filename": "snare_93bpm.wav",
                "bpm": 93.0,
                "key": None,
                "type": "drums",
                "genre": "jazz",
                "energy": 0.6,
                "groove_type": "swing",
                "era": "1970s"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_initialization(self, organizer, temp_output_dir):
        """Test organizer initialization."""
        assert organizer.output_dir == Path(temp_output_dir)
        assert organizer.output_dir.exists()
        assert hasattr(organizer, "strategies")
        assert "musical" in organizer.strategies
        assert "sp404" in organizer.strategies
    
    @pytest.mark.asyncio
    async def test_musical_organization(self, organizer, mock_sample_metadata):
        """Test organization by musical properties."""
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=[s["path"] for s in mock_sample_metadata],
                strategy="musical",
                metadata=mock_sample_metadata
            )
            
            assert "organization_plan" in result
            plan = result["organization_plan"]
            
            # Check key-based organization
            assert "C_major" in plan or "c_major" in str(plan).lower()
            assert "G_major" in plan or "g_major" in str(plan).lower()
            
            # Check BPM organization
            assert any("90" in str(folder) for folder in plan.keys())
            assert any("120" in str(folder) for folder in plan.keys())
    
    @pytest.mark.asyncio
    async def test_genre_organization(self, organizer, mock_sample_metadata):
        """Test organization by genre."""
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=[s["path"] for s in mock_sample_metadata],
                strategy="genre",
                metadata=mock_sample_metadata
            )
            
            plan = result["organization_plan"]
            
            # Check genre folders
            assert any("hip-hop" in folder.lower() for folder in plan.keys())
            assert any("house" in folder.lower() for folder in plan.keys())
            assert any("jazz" in folder.lower() for folder in plan.keys())
    
    @pytest.mark.asyncio
    async def test_groove_organization(self, organizer, mock_sample_metadata):
        """Test organization by groove type."""
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=[s["path"] for s in mock_sample_metadata],
                strategy="groove",
                metadata=mock_sample_metadata
            )
            
            plan = result["organization_plan"]
            
            # Check groove folders
            assert any("boom_bap" in folder.lower() for folder in plan.keys())
            assert any("four_on_floor" in folder.lower() or "4_on_floor" in folder.lower() 
                      for folder in plan.keys())
            assert any("swing" in folder.lower() for folder in plan.keys())
    
    @pytest.mark.asyncio
    async def test_sp404_organization(self, organizer, mock_sample_metadata):
        """Test SP-404 bank organization."""
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=[s["path"] for s in mock_sample_metadata],
                strategy="sp404",
                metadata=mock_sample_metadata,
                sp404_template="boom_bap"
            )
            
            plan = result["organization_plan"]
            
            # Check SP-404 structure
            assert any("bank" in folder.lower() for folder in plan.keys())
            assert "pad_assignments" in result
            
            # Check pad assignments
            assignments = result["pad_assignments"]
            assert len(assignments) > 0
            assert all("pad" in a for a in assignments)
            assert all("sample" in a for a in assignments)
    
    def test_sp404_templates(self, organizer):
        """Test SP-404 bank templates."""
        templates = organizer.sp404_templates
        
        assert "boom_bap" in templates
        assert "electronic" in templates
        assert "jazz" in templates
        
        # Check boom bap template
        boom_bap = templates["boom_bap"]
        assert "A" in boom_bap  # Bank A
        assert 1 in boom_bap["A"]  # Pad 1
        assert boom_bap["A"][1] == "kick"
    
    @pytest.mark.asyncio
    async def test_compatibility_organization(self, organizer, mock_sample_metadata):
        """Test organization by compatibility."""
        # Mock compatibility scores
        mock_compatibility = {
            ("kick_90bpm_Cmaj.wav", "bass_120bpm_Gmaj.wav"): 7.5,
            ("kick_90bpm_Cmaj.wav", "snare_93bpm.wav"): 8.5,
            ("bass_120bpm_Gmaj.wav", "snare_93bpm.wav"): 5.0
        }
        
        with patch('shutil.copy2'):
            with patch.object(organizer, '_calculate_compatibility',
                            side_effect=lambda s1, s2: mock_compatibility.get(
                                (Path(s1["path"]).name, Path(s2["path"]).name), 5.0)):
                
                result = await organizer.organize_samples(
                    sample_paths=[s["path"] for s in mock_sample_metadata],
                    strategy="compatibility",
                    metadata=mock_sample_metadata,
                    analyze_relationships=True
                )
                
                plan = result["organization_plan"]
                
                # Should group compatible samples
                assert any("compatible" in folder.lower() for folder in plan.keys())
    
    @pytest.mark.asyncio
    async def test_project_organization(self, organizer, mock_sample_metadata):
        """Test project-based organization."""
        with patch('shutil.copy2'):
            result = await organizer.organize_samples(
                sample_paths=[s["path"] for s in mock_sample_metadata],
                strategy="project",
                metadata=mock_sample_metadata,
                project_name="MyBeat"
            )
            
            plan = result["organization_plan"]
            
            # Check project structure
            assert any("mybeat" in folder.lower() for folder in plan.keys())
            assert any("drums" in folder.lower() for folder in plan.keys())
            assert any("bass" in folder.lower() for folder in plan.keys())
    
    def test_smart_naming(self, organizer):
        """Test smart file naming."""
        # Test with full metadata
        name = organizer._generate_smart_name(
            original="sample.wav",
            metadata={
                "bpm": 90.0,
                "key": "C major",
                "type": "drums",
                "groove_type": "boom_bap"
            }
        )
        
        assert "90bpm" in name
        assert "Cmaj" in name or "C_major" in name
        assert "drums" in name
        assert "boom_bap" in name
        
        # Test with partial metadata
        name = organizer._generate_smart_name(
            original="bass.wav",
            metadata={"type": "bass"}
        )
        
        assert "bass" in name
        assert name.endswith(".wav")
    
    def test_folder_structure_creation(self, organizer, temp_output_dir):
        """Test folder structure creation."""
        structure = {
            "drums/kicks": ["kick1.wav", "kick2.wav"],
            "bass": ["bass1.wav"],
            "melodic/keys": ["piano.wav"]
        }
        
        organizer._create_folder_structure(structure)
        
        # Check folders exist
        assert (organizer.output_dir / "drums" / "kicks").exists()
        assert (organizer.output_dir / "bass").exists()
        assert (organizer.output_dir / "melodic" / "keys").exists()
    
    @pytest.mark.asyncio
    async def test_metadata_extraction(self, organizer, mock_audio_files):
        """Test metadata extraction from files."""
        file_path = mock_audio_files["drum_90bpm.wav"]["path"]
        
        metadata = await organizer._extract_metadata(file_path)
        
        assert "bpm" in metadata
        assert "duration" in metadata
        assert "energy" in metadata
        assert metadata["bpm"] == 90.0
    
    def test_organization_summary(self, organizer):
        """Test organization summary generation."""
        plan = {
            "drums": ["kick.wav", "snare.wav"],
            "bass": ["bass1.wav"],
            "melodic": ["piano.wav", "strings.wav"]
        }
        
        summary = organizer._generate_summary(
            plan=plan,
            strategy="genre",
            total_samples=5
        )
        
        assert "total_samples" in summary
        assert "folders_created" in summary
        assert "strategy_used" in summary
        assert summary["total_samples"] == 5
        assert summary["folders_created"] == 3
        assert summary["strategy_used"] == "genre"
    
    @pytest.mark.asyncio
    async def test_copy_vs_move_files(self, organizer, mock_sample_metadata, temp_output_dir):
        """Test copy vs move file operations."""
        # Create dummy files
        for sample in mock_sample_metadata:
            Path(sample["path"]).parent.mkdir(parents=True, exist_ok=True)
            Path(sample["path"]).touch()
        
        # Test copy
        with patch('shutil.copy2') as mock_copy:
            await organizer.organize_samples(
                sample_paths=[s["path"] for s in mock_sample_metadata],
                strategy="musical",
                copy_files=True
            )
            
            assert mock_copy.called
        
        # Test move
        with patch('shutil.move') as mock_move:
            await organizer.organize_samples(
                sample_paths=[s["path"] for s in mock_sample_metadata],
                strategy="musical",
                copy_files=False
            )
            
            assert mock_move.called
    
    def test_invalid_strategy(self, organizer):
        """Test handling of invalid organization strategy."""
        with pytest.raises(ValueError):
            organizer.strategies["invalid_strategy"]
    
    @pytest.mark.asyncio
    async def test_empty_input(self, organizer):
        """Test handling of empty input."""
        result = await organizer.organize_samples(
            sample_paths=[],
            strategy="musical"
        )
        
        assert result["organization_plan"] == {}
        assert result["summary"]["total_samples"] == 0
    
    def test_template_based_organization(self, organizer):
        """Test template-based folder creation."""
        template = {
            "structure": {
                "drums": ["kicks", "snares", "hats"],
                "bass": [],
                "melodic": ["keys", "strings", "brass"],
                "fx": []
            }
        }
        
        folders = organizer._create_from_template(template)
        
        assert "drums/kicks" in folders
        assert "drums/snares" in folders
        assert "melodic/strings" in folders
        assert "fx" in folders


class TestOrganizationStrategies:
    """Test specific organization strategies."""
    
    def test_bpm_grouping(self):
        """Test BPM-based grouping logic."""
        organizer = IntelligentOrganizer("/tmp")
        
        # Test BPM ranges
        assert organizer._get_bpm_range(90) == "80-100_bpm"
        assert organizer._get_bpm_range(120) == "110-130_bpm"
        assert organizer._get_bpm_range(140) == "130-150_bpm"
        assert organizer._get_bpm_range(75) == "70-90_bpm"
    
    def test_key_normalization(self):
        """Test musical key normalization."""
        organizer = IntelligentOrganizer("/tmp")
        
        assert organizer._normalize_key("C major") == "C_major"
        assert organizer._normalize_key("F# minor") == "Fsharp_minor"
        assert organizer._normalize_key("Bb major") == "Bb_major"
        assert organizer._normalize_key(None) == "unknown_key"
    
    def test_energy_grouping(self):
        """Test energy level grouping."""
        organizer = IntelligentOrganizer("/tmp")
        
        assert organizer._get_energy_level(0.9) == "high_energy"
        assert organizer._get_energy_level(0.5) == "medium_energy"
        assert organizer._get_energy_level(0.2) == "low_energy"


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_organize_by_key_function(self, temp_output_dir):
        """Test the organize_by_musical_key convenience function."""
        sample_paths = ["/test/sample1.wav", "/test/sample2.wav"]
        
        with patch('src.tools.intelligent_organizer.IntelligentOrganizer') as MockOrganizer:
            mock_instance = MockOrganizer.return_value
            mock_instance.organize_samples = AsyncMock(
                return_value={"organization_plan": {"C_major": ["sample1.wav"]}}
            )
            
            result = await organize_by_musical_key(
                sample_paths=sample_paths,
                output_dir=str(temp_output_dir)
            )
            
            assert "organization_plan" in result
    
    @pytest.mark.asyncio
    async def test_organize_sp404_function(self, temp_output_dir):
        """Test the organize_for_sp404_banks convenience function."""
        sample_paths = ["/test/kick.wav", "/test/snare.wav"]
        
        with patch('src.tools.intelligent_organizer.IntelligentOrganizer') as MockOrganizer:
            mock_instance = MockOrganizer.return_value
            mock_instance.organize_samples = AsyncMock(
                return_value={
                    "organization_plan": {"Bank_A": ["kick.wav"]},
                    "pad_assignments": [{"pad": "A1", "sample": "kick.wav"}]
                }
            )
            
            result = await organize_for_sp404_banks(
                sample_paths=sample_paths,
                output_dir=str(temp_output_dir),
                template="boom_bap"
            )
            
            assert "pad_assignments" in result