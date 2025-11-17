import { useEffect, useRef, useState, useCallback, useId } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { useAudioContext } from '@/contexts/AudioContext';

export interface AudioPlayerState {
  isPlaying: boolean;
  isLoading: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  playbackRate: number;
  error: string | null;
}

export interface AudioPlayerControls {
  play: () => void;
  pause: () => void;
  togglePlay: () => void;
  stop: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  setPlaybackRate: (rate: number) => void;
  skip: (seconds: number) => void;
}

export interface UseAudioPlayerOptions {
  audioUrl: string;
  containerRef: React.RefObject<HTMLDivElement>;
  height?: number;
  waveColor?: string;
  progressColor?: string;
  cursorColor?: string;
  onReady?: () => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
  onError?: (error: Error) => void;
}

export function useAudioPlayer({
  audioUrl,
  containerRef,
  height = 128,
  waveColor = 'rgb(100, 116, 139)',
  progressColor = 'rgb(31, 199, 255)',
  cursorColor = 'rgb(21, 184, 87)',
  onReady,
  onPlay,
  onPause,
  onFinish,
  onError,
}: UseAudioPlayerOptions): [AudioPlayerState, AudioPlayerControls, WaveSurfer | null] {
  const playerId = useId();
  const audioContext = useAudioContext();
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [state, setState] = useState<AudioPlayerState>({
    isPlaying: false,
    isLoading: true,
    currentTime: 0,
    duration: 0,
    volume: 1,
    playbackRate: 1,
    error: null,
  });

  // Initialize WaveSurfer
  useEffect(() => {
    if (!containerRef.current) return;

    try {
      const wavesurfer = WaveSurfer.create({
        container: containerRef.current,
        waveColor,
        progressColor,
        cursorColor,
        barWidth: 2,
        barRadius: 3,
        height,
        normalize: true,
        backend: 'WebAudio',
        interact: true,
        hideScrollbar: false,
        autoCenter: true,
        minPxPerSec: 50,
      });

      // Event handlers
      wavesurfer.on('ready', () => {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          duration: wavesurfer.getDuration(),
        }));
        onReady?.();
      });

      wavesurfer.on('audioprocess', () => {
        setState((prev) => ({
          ...prev,
          currentTime: wavesurfer.getCurrentTime(),
        }));
      });

      wavesurfer.on('seek', () => {
        setState((prev) => ({
          ...prev,
          currentTime: wavesurfer.getCurrentTime(),
        }));
      });

      wavesurfer.on('play', () => {
        setState((prev) => ({ ...prev, isPlaying: true }));
        onPlay?.();
      });

      wavesurfer.on('pause', () => {
        setState((prev) => ({ ...prev, isPlaying: false }));
        onPause?.();
      });

      wavesurfer.on('finish', () => {
        setState((prev) => ({ ...prev, isPlaying: false, currentTime: 0 }));
        onFinish?.();
      });

      wavesurfer.on('error', (error) => {
        setState((prev) => ({
          ...prev,
          error: error.message || 'Failed to load audio',
          isLoading: false,
        }));
        onError?.(error);
      });

      wavesurfer.load(audioUrl);
      wavesurferRef.current = wavesurfer;
      audioContext.registerPlayer(wavesurfer, playerId);

      return () => {
        audioContext.unregisterPlayer(playerId);
        wavesurfer.destroy();
        wavesurferRef.current = null;
      };
    } catch (error) {
      setState((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to initialize audio player',
        isLoading: false,
      }));
      onError?.(error instanceof Error ? error : new Error('Failed to initialize audio player'));
    }
  }, [audioUrl, containerRef, height, waveColor, progressColor, cursorColor, onReady, onPlay, onPause, onFinish, onError, audioContext, playerId]);

  // Control functions
  const play = useCallback(() => {
    audioContext.stopAllExcept(playerId);
    wavesurferRef.current?.play();
  }, [audioContext, playerId]);

  const pause = useCallback(() => {
    wavesurferRef.current?.pause();
  }, []);

  const togglePlay = useCallback(() => {
    wavesurferRef.current?.playPause();
  }, []);

  const stop = useCallback(() => {
    wavesurferRef.current?.stop();
    setState((prev) => ({ ...prev, currentTime: 0, isPlaying: false }));
  }, []);

  const seek = useCallback((time: number) => {
    if (!wavesurferRef.current) return;
    const duration = wavesurferRef.current.getDuration();
    const seekPosition = Math.max(0, Math.min(time, duration));
    wavesurferRef.current.seekTo(seekPosition / duration);
  }, []);

  const setVolume = useCallback((volume: number) => {
    const clampedVolume = Math.max(0, Math.min(1, volume));
    wavesurferRef.current?.setVolume(clampedVolume);
    setState((prev) => ({ ...prev, volume: clampedVolume }));
  }, []);

  const setPlaybackRate = useCallback((rate: number) => {
    const clampedRate = Math.max(0.25, Math.min(2, rate));
    wavesurferRef.current?.setPlaybackRate(clampedRate);
    setState((prev) => ({ ...prev, playbackRate: clampedRate }));
  }, []);

  const skip = useCallback((seconds: number) => {
    if (!wavesurferRef.current) return;
    const newTime = state.currentTime + seconds;
    seek(newTime);
  }, [state.currentTime, seek]);

  const controls: AudioPlayerControls = {
    play,
    pause,
    togglePlay,
    stop,
    seek,
    setVolume,
    setPlaybackRate,
    skip,
  };

  return [state, controls, wavesurferRef.current];
}
