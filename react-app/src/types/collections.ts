// Collection types
export interface Collection {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  parent_collection_id?: number;
  is_smart: boolean;
  smart_rules?: SmartRules;
  sample_count: number;
  created_at: string;
  updated_at: string;
}

export interface SmartRules {
  genres?: string[];
  bpm_min?: number;
  bpm_max?: number;
  tags?: string[];
  min_confidence?: number;
  sample_types?: string[];
}

export interface CreateCollectionRequest {
  name: string;
  description?: string;
  is_smart?: boolean;
  smart_rules?: SmartRules;
  parent_collection_id?: number;
}

export interface UpdateCollectionRequest {
  name?: string;
  description?: string;
  smart_rules?: SmartRules;
}

export interface AddSamplesToCollectionRequest {
  sample_ids: number[];
}

export interface CollectionSample {
  collection_id: number;
  sample_id: number;
  added_at: string;
}
