# Essentia Pre-trained Models

This directory contains pre-trained TensorFlow models for genre classification using Essentia.

## Models

### 1. Embedding Model
- **Filename:** `discogs-maest-30s-pw-519l-2.pb`
- **Size:** 332MB
- **Purpose:** Extract audio embeddings from 30-second audio segments
- **Architecture:** MAEST (Music Audio Embedding Space with Transformers)
- **Updated:** January 2025

### 2. Genre Classification Model
- **Filename:** `genre_discogs519-discogs-maest-30s-pw-519l-1.pb`
- **Size:** 1.5MB
- **Purpose:** Classify audio into 519 Discogs genre categories
- **Classes:** 519 fine-grained music styles from Discogs database
- **Updated:** January 2025

## Download

To download the models, run:

```bash
python backend/scripts/download_essentia_models.py
```

Or manually download from:
- Embedding: https://essentia.upf.edu/models/feature-extractors/maest/discogs-maest-30s-pw-519l-2.pb
- Genre: https://essentia.upf.edu/models/classification-heads/genre_discogs519/genre_discogs519-discogs-maest-30s-pw-519l-1.pb

## License

These models are provided by the Essentia team at Music Technology Group (MTG), Universitat Pompeu Fabra.

- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Source:** https://essentia.upf.edu/models.html
- **Citation:** If using these models, please cite the Essentia library and MTG research

## Usage

Models are lazy-loaded by the `EssentiaAnalyzer` service only when genre classification is needed. This keeps memory usage low when only BPM analysis is required.

## Storage

Total disk space required: ~334MB (332MB embedding + 1.5MB genre model)

**Note:** Model files (*.pb) are excluded from git via `.gitignore` due to their size. They must be downloaded separately on each development machine or in Docker containers.
