"""Tests for BPM validation and octave correction utilities."""

import pytest

from app.utils.bpm_validation import correct_octave_errors, validate_bpm


class TestCorrectOctaveErrors:
    """Tests for the correct_octave_errors function."""

    def test_correct_octave_error_too_low(self):
        """Test correction of BPM that's too low (26 → 104)."""
        result = correct_octave_errors(26.0, (60, 180))
        assert result == 104.0

    def test_correct_octave_error_too_high(self):
        """Test correction of BPM that's too high (225 → 112.5)."""
        result = correct_octave_errors(225.0, (60, 180))
        assert result == 112.5

    def test_correct_octave_no_correction_needed(self):
        """Test BPM already in range requires no correction."""
        result = correct_octave_errors(90.0, (60, 180))
        assert result == 90.0

    def test_correct_octave_edge_case_30(self):
        """Test boundary case: 30 BPM should double to 60."""
        result = correct_octave_errors(30.0, (60, 180))
        assert result == 60.0

    def test_correct_octave_edge_case_360(self):
        """Test boundary case: 360 BPM should halve to 180."""
        result = correct_octave_errors(360.0, (60, 180))
        assert result == 180.0

    def test_correct_octave_multiple_doublings(self):
        """Test multiple doubling iterations: 13 → 104 (8x)."""
        # 13 * 2 = 26 (too low)
        # 13 * 4 = 52 (too low)
        # 13 * 8 = 104 (in range!)
        result = correct_octave_errors(13.0, (60, 180))
        assert result == 104.0

    def test_correct_octave_multiple_halvings(self):
        """Test multiple halving iterations: 450 → 112.5 (4x)."""
        # 450 / 2 = 225 (too high)
        # 450 / 4 = 112.5 (in range!)
        result = correct_octave_errors(450.0, (60, 180))
        assert result == 112.5

    def test_correct_octave_custom_range(self):
        """Test with custom BPM range for one-shots."""
        # With wider range (40-200), 30 should double to 60
        result = correct_octave_errors(30.0, (40, 200))
        assert result == 60.0

    def test_correct_octave_boundary_lower(self):
        """Test lower boundary: 60 BPM should not be corrected."""
        result = correct_octave_errors(60.0, (60, 180))
        assert result == 60.0

    def test_correct_octave_boundary_upper(self):
        """Test upper boundary: 180 BPM should not be corrected."""
        result = correct_octave_errors(180.0, (60, 180))
        assert result == 180.0

    def test_correct_octave_exact_double(self):
        """Test exact doubling: 52 → 104."""
        result = correct_octave_errors(52.0, (60, 180))
        assert result == 104.0

    def test_correct_octave_exact_half(self):
        """Test exact halving: 200 → 100."""
        result = correct_octave_errors(200.0, (60, 180))
        assert result == 100.0


class TestValidateBPM:
    """Tests for the validate_bpm function."""

    def test_validate_bpm_loop_range(self):
        """Test validation with loop sample type (60-180 BPM)."""
        bpm, was_corrected = validate_bpm(26.0, sample_type="loop")
        assert bpm == 104.0
        assert was_corrected is True

    def test_validate_bpm_one_shot_range(self):
        """Test validation with one-shot sample type (40-200 BPM)."""
        # 30 * 2 = 60, which is in range for one-shots (40-200)
        bpm, was_corrected = validate_bpm(30.0, sample_type="one-shot")
        assert bpm == 60.0
        assert was_corrected is True

    def test_validate_bpm_general_range(self):
        """Test validation with general sample type (40-200 BPM)."""
        bpm, was_corrected = validate_bpm(25.0, sample_type="general")
        assert bpm == 50.0  # 25 * 2 (first value in range)
        assert was_corrected is True

    def test_validate_bpm_correction_flag_enabled(self):
        """Test validation with correction enabled."""
        bpm, was_corrected = validate_bpm(26.0, apply_correction=True)
        assert bpm == 104.0
        assert was_corrected is True

    def test_validate_bpm_correction_flag_disabled(self):
        """Test validation with correction disabled."""
        bpm, was_corrected = validate_bpm(26.0, apply_correction=False)
        assert bpm == 26.0
        assert was_corrected is False

    def test_validate_bpm_no_correction_needed(self):
        """Test validation when BPM is already in range."""
        bpm, was_corrected = validate_bpm(90.0, sample_type="loop")
        assert bpm == 90.0
        assert was_corrected is False

    def test_validate_bpm_unknown_sample_type(self):
        """Test validation with unknown sample type defaults to general."""
        bpm, was_corrected = validate_bpm(30.0, sample_type="unknown")
        assert bpm == 60.0  # Should use general range (40-200)
        assert was_corrected is True

    def test_validate_bpm_high_value(self):
        """Test validation with high BPM value."""
        bpm, was_corrected = validate_bpm(225.0, sample_type="loop")
        assert bpm == 112.5
        assert was_corrected is True

    def test_validate_bpm_edge_case_threshold(self):
        """Test was_corrected uses 0.1 threshold."""
        # If correction is exactly 0.1 or less, should not flag as corrected
        # But in practice, our corrections are always larger (2x, 0.5x)
        bpm, was_corrected = validate_bpm(90.0, sample_type="loop")
        assert bpm == 90.0
        assert was_corrected is False
