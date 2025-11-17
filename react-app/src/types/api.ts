// Sample types
export interface Sample {
  id: number;
  user_id: number;
  title: string;
  file_path: string;
  file_url: string; // URL for downloading/streaming audio
  duration?: number;
  genre?: string;
  bpm?: number;
  musical_key?: string;
  tags: string[];
  rating?: number;
  created_at: string;
  updated_at: string;
  audio_features?: AudioFeatures;
  ai_analysis?: AIAnalysis;
}

export interface AudioFeatures {
  bpm?: number;
  key?: string;
  scale?: string;
  spectral_centroid?: number;
  spectral_bandwidth?: number;
  spectral_rolloff?: number;
  spectral_flatness?: number;
  zero_crossing_rate?: number;
  rms_energy?: number;
  harmonic_ratio?: number;
  mfcc_mean?: number[];
  mfcc_std?: number[];
  chroma_mean?: number[];
  chroma_std?: number[];
}

export interface AIAnalysis {
  genre_tags: string[];
  mood_tags: string[];
  description: string;
  confidence: number;
}

// Kit types
export interface Kit {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  samples: PadAssignment[];
}

export interface PadAssignment {
  kit_id: number;
  sample_id: number;
  pad_bank: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J';
  pad_number: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16;
  volume?: number;
  pitch_shift?: number;
  sample: Sample;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

// User preferences
export interface UserPreferences {
  id: number;
  vibe_analysis_model: 'qwen3-7b' | 'qwen3-235b';
  auto_vibe_analysis: boolean;
  auto_audio_features: boolean;
  batch_processing_model: 'qwen3-7b' | 'qwen3-235b';
  batch_auto_analyze: boolean;
  max_cost_per_request?: number;
  default_export_format: 'wav' | 'aiff';
  default_export_organization: 'flat' | 'genre' | 'bpm' | 'kit';
  auto_sanitize_filenames: boolean;
  created_at: string;
  updated_at: string;
}

// AI Model type
export interface Model {
  id: string;
  name: string;
  description: string;
  cost_per_sample: number;
}

export interface ModelsResponse {
  models: Model[];
}

// Vibe search types
export interface VibeSearchResult extends Sample {
  similarity: number; // 0-1 cosine similarity score
}

export interface VibeSearchResponse {
  query: string;
  results: VibeSearchResult[];
  count: number;
  execution_time_ms: number;
}

export interface VibeSearchFilters {
  bpm_min?: number;
  bpm_max?: number;
  genre?: string;
  energy_min?: number;
  energy_max?: number;
  danceability_min?: number;
  danceability_max?: number;
}

// API Error types
export interface APIError {
  detail: string;
  status_code: number;
}
