import { createContext, useContext, useRef, useCallback, ReactNode } from 'react';
import WaveSurfer from 'wavesurfer.js';

interface AudioContextValue {
  registerPlayer: (player: WaveSurfer, id: string) => void;
  unregisterPlayer: (id: string) => void;
  stopAllExcept: (id: string) => void;
}

const AudioContext = createContext<AudioContextValue | null>(null);

export function AudioProvider({ children }: { children: ReactNode }) {
  const playersRef = useRef<Map<string, WaveSurfer>>(new Map());

  const registerPlayer = useCallback((player: WaveSurfer, id: string) => {
    playersRef.current.set(id, player);
  }, []);

  const unregisterPlayer = useCallback((id: string) => {
    playersRef.current.delete(id);
  }, []);

  const stopAllExcept = useCallback((exceptId: string) => {
    playersRef.current.forEach((player, id) => {
      if (id !== exceptId && player.isPlaying()) {
        player.pause();
      }
    });
  }, []);

  return (
    <AudioContext.Provider value={{ registerPlayer, unregisterPlayer, stopAllExcept }}>
      {children}
    </AudioContext.Provider>
  );
}

export function useAudioContext() {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error('useAudioContext must be used within AudioProvider');
  }
  return context;
}
