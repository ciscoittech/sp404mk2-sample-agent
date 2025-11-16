"""
Performance benchmarking tests for Essentia vs librosa analysis.

Tests analyze speed, memory usage, and performance across different file sizes
and complexity scenarios. Generates performance report for production readiness.
"""
import pytest
import time
import asyncio
import psutil
import os
from pathlib import Path
from typing import Dict, List
import numpy as np
import soundfile as sf

from app.utils.essentia_check import ESSENTIA_AVAILABLE

if ESSENTIA_AVAILABLE:
    from app.services.essentia_analyzer import EssentiaAnalyzer

from app.services.audio_features_service import AudioFeaturesService


@pytest.fixture
def performance_fixtures(tmp_path) -> Dict[str, Path]:
    """Create audio fixtures of various durations for performance testing."""
    fixtures = {}
    sample_rate = 44100

    # Create test samples of different durations
    durations = {
        "1s": 1.0,
        "5s": 5.0,
        "30s": 30.0,
        "60s": 60.0
    }

    for name, duration in durations.items():
        # Generate simple sine wave (440Hz A note)
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        # Add some harmonics for realism
        audio += 0.25 * np.sin(2 * np.pi * 880 * t)  # Octave
        audio += 0.125 * np.sin(2 * np.pi * 1320 * t)  # Fifth

        file_path = tmp_path / f"test_{name}.wav"
        sf.write(str(file_path), audio, sample_rate)
        fixtures[name] = file_path

    return fixtures


class TestEssentiaPerformance:
    """Performance benchmarking for Essentia analyzer."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_bpm_performance_1s(self, performance_fixtures):
        """Benchmark BPM analysis on 1-second sample."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["1s"]

        start = time.perf_counter()
        result = await analyzer.analyze_bpm(audio_path, method="multifeature")
        elapsed = time.perf_counter() - start

        assert result is not None
        assert elapsed < 5.0, f"1s analysis took {elapsed:.2f}s (target: <5s)"
        print(f"\n  1s sample (multifeature): {elapsed:.3f}s")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_bpm_performance_5s(self, performance_fixtures):
        """Benchmark BPM analysis on 5-second sample."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["5s"]

        start = time.perf_counter()
        result = await analyzer.analyze_bpm(audio_path, method="multifeature")
        elapsed = time.perf_counter() - start

        assert result is not None
        assert elapsed < 5.0, f"5s analysis took {elapsed:.2f}s (target: <5s)"
        print(f"\n  5s sample (multifeature): {elapsed:.3f}s")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_bpm_performance_30s(self, performance_fixtures):
        """Benchmark BPM analysis on 30-second sample."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["30s"]

        start = time.perf_counter()
        result = await analyzer.analyze_bpm(audio_path, method="multifeature")
        elapsed = time.perf_counter() - start

        assert result is not None
        assert elapsed < 10.0, f"30s analysis took {elapsed:.2f}s (target: <10s)"
        print(f"\n  30s sample (multifeature): {elapsed:.3f}s")

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_bpm_performance_60s(self, performance_fixtures):
        """Benchmark BPM analysis on 60-second sample."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["60s"]

        start = time.perf_counter()
        result = await analyzer.analyze_bpm(audio_path, method="degara")
        elapsed = time.perf_counter() - start

        assert result is not None
        assert elapsed < 15.0, f"60s analysis took {elapsed:.2f}s (target: <15s)"
        print(f"\n  60s sample (degara): {elapsed:.3f}s")


class TestMethodComparison:
    """Compare performance of multifeature vs degara methods."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_multifeature_vs_degara_30s(self, performance_fixtures):
        """Compare multifeature vs degara methods on 30s sample."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["30s"]

        # Test multifeature
        start = time.perf_counter()
        result_multi = await analyzer.analyze_bpm(audio_path, method="multifeature")
        time_multi = time.perf_counter() - start

        # Test degara
        start = time.perf_counter()
        result_degara = await analyzer.analyze_bpm(audio_path, method="degara")
        time_degara = time.perf_counter() - start

        assert result_multi is not None
        assert result_degara is not None

        print(f"\n  30s multifeature: {time_multi:.3f}s")
        print(f"  30s degara: {time_degara:.3f}s")
        print(f"  Speedup: {time_multi/time_degara:.2f}x")

        # degara should be faster (typically)
        # Note: This may not always be true for short samples


class TestMemoryUsage:
    """Test memory consumption during analysis."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_memory_usage_60s(self, performance_fixtures):
        """Measure memory usage during 60-second sample analysis."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["60s"]

        # Get process handle
        process = psutil.Process(os.getpid())

        # Measure memory before
        mem_before = process.memory_info().rss / (1024 * 1024)  # MB

        # Run analysis
        result = await analyzer.analyze_bpm(audio_path)

        # Measure memory after
        mem_after = process.memory_info().rss / (1024 * 1024)  # MB
        mem_used = mem_after - mem_before

        assert result is not None
        print(f"\n  Memory before: {mem_before:.1f}MB")
        print(f"  Memory after: {mem_after:.1f}MB")
        print(f"  Memory used: {mem_used:.1f}MB")

        # Should not use more than 500MB for single 60s analysis
        assert mem_used < 500, f"Used {mem_used:.1f}MB (target: <500MB)"

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_memory_no_leak(self, performance_fixtures):
        """Test for memory leaks with multiple analyses."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["5s"]

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / (1024 * 1024)

        # Run 10 analyses
        for _ in range(10):
            await analyzer.analyze_bpm(audio_path)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_growth = mem_after - mem_before

        print(f"\n  Memory growth after 10 analyses: {mem_growth:.1f}MB")

        # Should not grow significantly (some growth is normal)
        assert mem_growth < 200, f"Memory grew {mem_growth:.1f}MB (possible leak)"


class TestConcurrentPerformance:
    """Test performance under concurrent load."""

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_concurrent_analyses_5_files(self, performance_fixtures):
        """Test concurrent analysis of 5 files."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["5s"]

        start = time.perf_counter()

        # Run 5 concurrent analyses
        tasks = [analyzer.analyze_bpm(audio_path) for _ in range(5)]
        results = await asyncio.gather(*tasks)

        elapsed = time.perf_counter() - start

        assert all(r is not None for r in results)
        print(f"\n  5 concurrent analyses: {elapsed:.3f}s")
        print(f"  Average per file: {elapsed/5:.3f}s")

        # Should complete in reasonable time (parallel execution)
        assert elapsed < 30.0, f"5 concurrent took {elapsed:.2f}s (target: <30s)"

    @pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
    @pytest.mark.asyncio
    async def test_concurrent_analyses_10_files(self, performance_fixtures):
        """Test concurrent analysis of 10 files."""
        analyzer = EssentiaAnalyzer()
        audio_path = performance_fixtures["5s"]

        start = time.perf_counter()

        # Run 10 concurrent analyses
        tasks = [analyzer.analyze_bpm(audio_path) for _ in range(10)]
        results = await asyncio.gather(*tasks)

        elapsed = time.perf_counter() - start

        assert all(r is not None for r in results)
        print(f"\n  10 concurrent analyses: {elapsed:.3f}s")
        print(f"  Average per file: {elapsed/10:.3f}s")

        # Should handle 10 concurrent requests
        assert elapsed < 60.0, f"10 concurrent took {elapsed:.2f}s (target: <60s)"


class TestEssentiaVsLibrosa:
    """Compare Essentia vs librosa performance and accuracy."""

    @pytest.mark.asyncio
    async def test_speed_comparison_5s(self, performance_fixtures, monkeypatch):
        """Compare Essentia vs librosa speed on 5s sample."""
        audio_path = performance_fixtures["5s"]

        # Test Essentia (if available)
        essentia_time = None
        if ESSENTIA_AVAILABLE:
            analyzer = EssentiaAnalyzer()
            start = time.perf_counter()
            essentia_result = await analyzer.analyze_bpm(audio_path)
            essentia_time = time.perf_counter() - start
            print(f"\n  Essentia (5s): {essentia_time:.3f}s")

        # Test librosa (via AudioFeaturesService)
        from app.core.config import settings
        monkeypatch.setattr(settings, 'USE_ESSENTIA', False)

        service = AudioFeaturesService()
        start = time.perf_counter()
        librosa_result = await service.analyze_file(audio_path)
        librosa_time = time.perf_counter() - start

        print(f"  librosa (5s): {librosa_time:.3f}s")

        if essentia_time:
            speedup = librosa_time / essentia_time
            print(f"  Essentia speedup: {speedup:.2f}x")

    @pytest.mark.asyncio
    async def test_full_analysis_comparison(self, performance_fixtures, monkeypatch):
        """Compare full AudioFeaturesService analysis with both analyzers."""
        audio_path = performance_fixtures["5s"]

        # Test with Essentia
        essentia_time = None
        if ESSENTIA_AVAILABLE:
            from app.core.config import settings
            monkeypatch.setattr(settings, 'USE_ESSENTIA', True)
            monkeypatch.setattr(settings, 'ENABLE_GENRE_CLASSIFICATION', False)

            service = AudioFeaturesService()
            start = time.perf_counter()
            essentia_features = await service.analyze_file(audio_path)
            essentia_time = time.perf_counter() - start

            print(f"\n  Full analysis (Essentia): {essentia_time:.3f}s")
            print(f"    BPM: {essentia_features.bpm}")
            print(f"    Analyzer: {essentia_features.metadata.get('analyzer')}")

        # Test with librosa
        from app.core.config import settings
        monkeypatch.setattr(settings, 'USE_ESSENTIA', False)

        service = AudioFeaturesService()
        start = time.perf_counter()
        librosa_features = await service.analyze_file(audio_path)
        librosa_time = time.perf_counter() - start

        print(f"  Full analysis (librosa): {librosa_time:.3f}s")
        print(f"    BPM: {librosa_features.bpm}")
        print(f"    Analyzer: {librosa_features.metadata.get('analyzer')}")


@pytest.mark.skipif(not ESSENTIA_AVAILABLE, reason="Essentia not available")
class TestPerformanceReport:
    """Generate comprehensive performance report."""

    @pytest.mark.asyncio
    async def test_generate_performance_report(self, performance_fixtures):
        """Generate comprehensive performance benchmarking report."""
        analyzer = EssentiaAnalyzer()

        report = {
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "essentia_available": ESSENTIA_AVAILABLE,
            "benchmarks": {}
        }

        # Test different durations and methods
        test_cases = [
            ("1s", "multifeature"),
            ("5s", "multifeature"),
            ("30s", "multifeature"),
            ("30s", "degara"),
            ("60s", "degara")
        ]

        for duration, method in test_cases:
            audio_path = performance_fixtures[duration]

            start = time.perf_counter()
            result = await analyzer.analyze_bpm(audio_path, method=method)
            elapsed = time.perf_counter() - start

            test_name = f"{duration}_{method}"
            report["benchmarks"][test_name] = {
                "duration": duration,
                "method": method,
                "time_seconds": round(elapsed, 3),
                "bpm": round(result.bpm, 1) if result else None,
                "confidence": round(result.confidence, 3) if result else None,
                "status": "PASS" if elapsed < 10.0 else "SLOW"
            }

        # Print report
        print("\n" + "="*60)
        print("ESSENTIA PERFORMANCE BENCHMARK REPORT")
        print("="*60)
        print(f"Test Date: {report['test_date']}")
        print(f"Essentia Available: {report['essentia_available']}")
        print("\nBenchmarks:")
        print("-"*60)

        for test_name, data in report["benchmarks"].items():
            print(f"\n{test_name}:")
            print(f"  Duration: {data['duration']}")
            print(f"  Method: {data['method']}")
            print(f"  Time: {data['time_seconds']}s")
            print(f"  BPM: {data['bpm']}")
            print(f"  Confidence: {data['confidence']}")
            print(f"  Status: {data['status']}")

        print("\n" + "="*60)

        # Validate performance targets
        for test_name, data in report["benchmarks"].items():
            assert data["status"] == "PASS", f"{test_name} exceeded time target"
