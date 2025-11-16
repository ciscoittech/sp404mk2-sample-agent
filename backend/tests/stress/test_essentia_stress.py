"""
Stress tests for Essentia integration under heavy load.

Tests concurrent requests, large files, corrupted data, memory limits,
and timeout behavior to validate production readiness.
"""
import pytest
import asyncio
import time
import psutil
import os
from pathlib import Path
from typing import List
import numpy as np
import soundfile as sf

from app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from app.services.essentia_analyzer import EssentiaAnalyzer

from app.services.audio_features_service import AudioFeaturesService
from app.models.audio_features import AudioError


@pytest.fixture
def stress_test_samples(tmp_path):
    """Create audio samples for stress testing."""
    samples = {}
    sample_rate = 44100

    # 1. Normal sample (5s)
    duration = 5.0
    t = np.linspace(0, duration, int(duration * sample_rate))
    normal = 0.5 * np.sin(2 * np.pi * 440 * t)
    normal_path = tmp_path / "normal_5s.wav"
    sf.write(str(normal_path), normal, sample_rate)
    samples["normal"] = normal_path

    # 2. Large file (2 minutes)
    duration = 120.0
    t = np.linspace(0, duration, int(duration * sample_rate))
    large = 0.5 * np.sin(2 * np.pi * 440 * t)
    large_path = tmp_path / "large_2min.wav"
    sf.write(str(large_path), large, sample_rate)
    samples["large"] = large_path

    # 3. Very large file (5 minutes) - only create if stress level high
    # Skip for normal test runs to save time/disk

    return samples


@pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
class TestConcurrentLoad:
    """Test Essentia under concurrent load."""

    @pytest.mark.asyncio
    async def test_10_concurrent_requests(self, stress_test_samples):
        """Test 10 concurrent BPM analyses."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["normal"]

        start = time.perf_counter()

        # Launch 10 concurrent analyses
        tasks = [analyzer.analyze_bpm(audio_path) for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.perf_counter() - start

        # Check results
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]

        print(f"\n  10 concurrent requests:")
        print(f"    Time: {elapsed:.2f}s")
        print(f"    Successful: {len(successful)}")
        print(f"    Failed: {len(failed)}")

        # All should succeed
        assert len(successful) == 10, f"Some requests failed: {failed}"

        # Should complete in reasonable time
        assert elapsed < 60.0, f"10 concurrent took {elapsed:.1f}s (target: <60s)"

    @pytest.mark.asyncio
    async def test_20_concurrent_requests(self, stress_test_samples):
        """Test 20 concurrent BPM analyses."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["normal"]

        start = time.perf_counter()

        # Launch 20 concurrent analyses
        tasks = [analyzer.analyze_bpm(audio_path) for _ in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.perf_counter() - start

        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]

        print(f"\n  20 concurrent requests:")
        print(f"    Time: {elapsed:.2f}s")
        print(f"    Successful: {len(successful)}")
        print(f"    Failed: {len(failed)}")

        # Most should succeed (some may timeout)
        assert len(successful) >= 15, f"Too many failures: {len(failed)}/20"

    @pytest.mark.asyncio
    async def test_concurrent_different_files(self, stress_test_samples):
        """Test concurrent analyses of different files."""
        analyzer = EssentiaAnalyzer()

        # Analyze normal and large files concurrently
        tasks = [
            analyzer.analyze_bpm(stress_test_samples["normal"])
            for _ in range(5)
        ] + [
            analyzer.analyze_bpm(stress_test_samples["large"])
            for _ in range(5)
        ]

        start = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.perf_counter() - start

        successful = [r for r in results if not isinstance(r, Exception)]

        print(f"\n  Mixed file sizes (10 concurrent):")
        print(f"    Time: {elapsed:.2f}s")
        print(f"    Successful: {len(successful)}/10")

        assert len(successful) >= 8


class TestLargeFiles:
    """Test handling of large audio files."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_2_minute_file(self, stress_test_samples):
        """Test analysis of 2-minute audio file."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["large"]

        start = time.perf_counter()
        result = await analyzer.analyze_bpm(audio_path, method="degara")
        elapsed = time.perf_counter() - start

        assert result is not None
        print(f"\n  2-minute file analysis:")
        print(f"    Time: {elapsed:.2f}s")
        print(f"    BPM: {result.bpm:.1f}")

        # Should complete in reasonable time
        assert elapsed < 30.0, f"2-minute file took {elapsed:.1f}s (target: <30s)"

    @pytest.mark.slow
    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_5_minute_file(self, tmp_path):
        """Test analysis of 5-minute audio file (slow test)."""
        # Create 5-minute file
        sample_rate = 44100
        duration = 300.0
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        file_path = tmp_path / "5min.wav"
        sf.write(str(file_path), audio, sample_rate)

        analyzer = EssentiaAnalyzer()

        start = time.perf_counter()
        result = await analyzer.analyze_bpm(file_path, method="degara")
        elapsed = time.perf_counter() - start

        assert result is not None
        print(f"\n  5-minute file analysis:")
        print(f"    Time: {elapsed:.2f}s")

        # Should still complete reasonably
        assert elapsed < 60.0, f"5-minute file took {elapsed:.1f}s (target: <60s)"


class TestCorruptedData:
    """Test handling of corrupted/invalid audio data."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_random_bytes_file(self, tmp_path):
        """Test handling of completely random bytes."""
        analyzer = EssentiaAnalyzer()

        # Create file with random bytes
        corrupt_file = tmp_path / "random.wav"
        with open(corrupt_file, 'wb') as f:
            f.write(os.urandom(10000))

        result = await analyzer.analyze_bpm(corrupt_file)

        # Should return None gracefully (not crash)
        assert result is None
        print(f"\n  Random bytes file: handled gracefully (returned None)")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_truncated_wav_file(self, tmp_path):
        """Test handling of truncated WAV file."""
        analyzer = EssentiaAnalyzer()

        # Create valid file then truncate it
        sample_rate = 44100
        duration = 5.0
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        file_path = tmp_path / "truncated.wav"
        sf.write(str(file_path), audio, sample_rate)

        # Truncate the file
        with open(file_path, 'r+b') as f:
            f.truncate(1000)  # Keep only first 1000 bytes

        result = await analyzer.analyze_bpm(file_path)

        # Should handle gracefully
        assert result is None
        print(f"\n  Truncated WAV file: handled gracefully")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_zero_audio_file(self, tmp_path):
        """Test handling of valid WAV with all zeros (silence)."""
        analyzer = EssentiaAnalyzer()

        # Create silent file
        sample_rate = 44100
        duration = 5.0
        audio = np.zeros(int(duration * sample_rate))

        file_path = tmp_path / "silence.wav"
        sf.write(str(file_path), audio, sample_rate)

        result = await analyzer.analyze_bpm(file_path)

        # May return result with low confidence or None
        print(f"\n  Silent file: BPM={result.bpm if result else None}")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_extreme_values_audio(self, tmp_path):
        """Test handling of audio with extreme values."""
        analyzer = EssentiaAnalyzer()

        # Create audio with clipping
        sample_rate = 44100
        duration = 5.0
        t = np.linspace(0, duration, int(duration * sample_rate))
        audio = 10.0 * np.sin(2 * np.pi * 440 * t)  # Way beyond [-1, 1]

        file_path = tmp_path / "clipped.wav"
        sf.write(str(file_path), np.clip(audio, -1, 1), sample_rate)

        result = await analyzer.analyze_bpm(file_path)

        # Should still work (clipped audio is still valid)
        assert result is not None
        print(f"\n  Clipped audio: BPM={result.bpm:.1f}")


class TestMemoryLimits:
    """Test memory consumption limits."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_memory_limit_large_file(self, stress_test_samples):
        """Test memory usage stays within limits for large file."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["large"]

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / (1024 * 1024)

        result = await analyzer.analyze_bpm(audio_path)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_used = mem_after - mem_before

        print(f"\n  Large file memory usage:")
        print(f"    Before: {mem_before:.1f}MB")
        print(f"    After: {mem_after:.1f}MB")
        print(f"    Used: {mem_used:.1f}MB")

        # Should not exceed 1GB for 2-minute file
        assert mem_used < 1000, f"Used {mem_used:.1f}MB (limit: 1000MB)"

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_memory_limit_concurrent(self, stress_test_samples):
        """Test memory usage during concurrent analyses."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["normal"]

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / (1024 * 1024)

        # Run 10 concurrent analyses
        tasks = [analyzer.analyze_bpm(audio_path) for _ in range(10)]
        await asyncio.gather(*tasks)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_used = mem_after - mem_before

        print(f"\n  10 concurrent memory usage:")
        print(f"    Before: {mem_before:.1f}MB")
        print(f"    After: {mem_after:.1f}MB")
        print(f"    Used: {mem_used:.1f}MB")

        # Should not use excessive memory
        assert mem_used < 2000, f"Used {mem_used:.1f}MB (limit: 2000MB)"


class TestTimeoutBehavior:
    """Test timeout handling."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_normal_file_completes_in_time(self, stress_test_samples):
        """Test normal files complete well within timeout."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["normal"]

        # Set a reasonable timeout
        timeout = 30.0

        try:
            result = await asyncio.wait_for(
                analyzer.analyze_bpm(audio_path),
                timeout=timeout
            )
            assert result is not None
            print(f"\n  Normal file completed within {timeout}s timeout")

        except asyncio.TimeoutError:
            pytest.fail(f"Normal file exceeded {timeout}s timeout")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_large_file_with_timeout(self, stress_test_samples):
        """Test large files with timeout."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["large"]

        timeout = 60.0  # Generous timeout for 2-minute file

        try:
            result = await asyncio.wait_for(
                analyzer.analyze_bpm(audio_path, method="degara"),
                timeout=timeout
            )
            assert result is not None
            print(f"\n  Large file completed within {timeout}s timeout")

        except asyncio.TimeoutError:
            pytest.fail(f"Large file exceeded {timeout}s timeout")


class TestErrorRecovery:
    """Test error recovery and resilience."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_recovery_after_error(self, stress_test_samples, tmp_path):
        """Test analyzer recovers after encountering error."""
        analyzer = EssentiaAnalyzer()

        # 1. Try to analyze invalid file (will fail)
        invalid_file = tmp_path / "invalid.wav"
        invalid_file.write_bytes(b"not a wav")

        result1 = await analyzer.analyze_bpm(invalid_file)
        assert result1 is None

        # 2. Analyze valid file (should work)
        result2 = await analyzer.analyze_bpm(stress_test_samples["normal"])
        assert result2 is not None

        print(f"\n  Error recovery: analyzer recovered after failure")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_multiple_errors_in_sequence(self, tmp_path):
        """Test analyzer handles multiple errors in sequence."""
        analyzer = EssentiaAnalyzer()

        # Create multiple invalid files
        for i in range(5):
            invalid_file = tmp_path / f"invalid_{i}.wav"
            invalid_file.write_bytes(b"not a wav" * i)

            result = await analyzer.analyze_bpm(invalid_file)
            assert result is None

        print(f"\n  Multiple errors: handled 5 consecutive errors gracefully")


class TestResourceCleanup:
    """Test proper resource cleanup."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_no_file_handle_leak(self, stress_test_samples):
        """Test no file handles are leaked."""
        analyzer = EssentiaAnalyzer()
        audio_path = stress_test_samples["normal"]

        process = psutil.Process(os.getpid())
        handles_before = len(process.open_files())

        # Run many analyses
        for _ in range(50):
            await analyzer.analyze_bpm(audio_path)

        handles_after = len(process.open_files())

        print(f"\n  File handles:")
        print(f"    Before: {handles_before}")
        print(f"    After: {handles_after}")

        # Should not leak file handles
        assert handles_after <= handles_before + 5, \
            f"File handle leak detected: {handles_after - handles_before} handles"


@pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
class TestStressReport:
    """Generate comprehensive stress test report."""

    @pytest.mark.asyncio
    async def test_generate_stress_report(self, stress_test_samples):
        """Generate comprehensive stress test report."""
        analyzer = EssentiaAnalyzer()

        report = {
            "concurrent_load": {},
            "large_files": {},
            "memory_usage": {},
            "error_handling": {}
        }

        # Test 1: Concurrent load
        for concurrency in [5, 10, 15]:
            start = time.perf_counter()
            tasks = [
                analyzer.analyze_bpm(stress_test_samples["normal"])
                for _ in range(concurrency)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.perf_counter() - start

            successful = len([r for r in results if not isinstance(r, Exception)])

            report["concurrent_load"][f"{concurrency}_requests"] = {
                "total": concurrency,
                "successful": successful,
                "time_seconds": round(elapsed, 2),
                "avg_per_request": round(elapsed / concurrency, 2)
            }

        # Test 2: Large file
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / (1024 * 1024)

        start = time.perf_counter()
        result = await analyzer.analyze_bpm(stress_test_samples["large"], method="degara")
        elapsed = time.perf_counter() - start

        mem_after = process.memory_info().rss / (1024 * 1024)

        report["large_files"]["2min_file"] = {
            "duration_seconds": 120,
            "analysis_time": round(elapsed, 2),
            "memory_used_mb": round(mem_after - mem_before, 1),
            "success": result is not None
        }

        # Print report
        print("\n" + "="*70)
        print("ESSENTIA STRESS TEST REPORT")
        print("="*70)

        print("\nConcurrent Load:")
        for test, data in report["concurrent_load"].items():
            print(f"  {test}:")
            print(f"    Success rate: {data['successful']}/{data['total']}")
            print(f"    Total time: {data['time_seconds']}s")
            print(f"    Avg per request: {data['avg_per_request']}s")

        print("\nLarge Files:")
        for test, data in report["large_files"].items():
            print(f"  {test}:")
            print(f"    Duration: {data['duration_seconds']}s")
            print(f"    Analysis time: {data['analysis_time']}s")
            print(f"    Memory used: {data['memory_used_mb']}MB")
            print(f"    Success: {data['success']}")

        print("="*70 + "\n")

        # Validate stress test passes
        assert all(
            data["successful"] >= data["total"] * 0.8  # 80% success rate
            for data in report["concurrent_load"].values()
        ), "Concurrent load test failed"

        assert report["large_files"]["2min_file"]["success"], "Large file test failed"
