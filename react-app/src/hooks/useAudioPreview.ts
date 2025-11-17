import { useEffect, useRef, useCallback } from 'react';
import { useAudioContext } from '@/contexts/AudioContext';

/**
 * Simple hook for quick audio preview without UI
 * Handles audio isolation (only one sample plays at a time)
 */
export function useAudioPreview(audioUrl: string) {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Create or get audio element on mount
  useEffect(() => {
    // Only create audio element if we have a valid URL
    if (!audioUrl) {
      audioRef.current = null;
      return;
    }

    const audio = new Audio(audioUrl);
    audio.preload = 'auto';
    audioRef.current = audio;

    return () => {
      audio.pause();
      audio.src = '';
    };
  }, [audioUrl]);

  const play = useCallback(() => {
    const audio = audioRef.current;
    if (!audio || !audioUrl) return;

    // Stop all other audio for isolation
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach((el) => {
      if (el !== audio && !el.paused) {
        el.pause();
      }
    });

    audio.play().catch((err) => {
      console.error('Failed to play audio:', err);
    });
  }, [audioUrl]);

  const pause = useCallback(() => {
    audioRef.current?.pause();
  }, []);

  const stop = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
  }, []);

  const togglePlay = useCallback(() => {
    const audio = audioRef.current;
    if (!audio || !audioUrl) return;
    if (audio.paused) {
      play();
    } else {
      pause();
    }
  }, [audioUrl, play, pause]);

  return {
    play,
    pause,
    stop,
    togglePlay,
  };
}
