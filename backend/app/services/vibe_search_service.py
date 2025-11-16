"""
Vibe Search Service for vector-based sample discovery.

Performs semantic search on samples using vector embeddings stored in PostgreSQL.
Uses Python numpy for cosine similarity calculations.
Supports filtering by BPM, genre, energy level, and other musical attributes.
"""
import time
import logging
import numpy as np
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.sample import Sample
from app.models.vibe_analysis import VibeAnalysis
from app.models.sample_embedding import SampleEmbedding
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Custom exception for search service errors."""

    def __init__(self, message: str, query: Optional[str] = None):
        self.message = message
        self.query = query
        super().__init__(self.message)


class VibeSearchService:
    """
    Service for semantic search of samples using vector embeddings.

    Stores embeddings in PostgreSQL and uses numpy for cosine similarity calculations.
    Provides fast, relevance-ranked sample discovery based on natural language queries.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        db: AsyncSession
    ):
        """
        Initialize vibe search service.

        Args:
            embedding_service: Service for generating query embeddings
            db: SQLAlchemy async session for PostgreSQL queries
        """
        self.embedding_service = embedding_service
        self.db = db

    async def search_by_vibe(
        self,
        query: str,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for samples using natural language query.

        Args:
            query: Natural language search query (e.g., "dark moody loop")
            limit: Maximum number of results to return (default: 20)
            filters: Optional filters to apply:
                - bpm_min (float): Minimum BPM
                - bpm_max (float): Maximum BPM
                - genre (str): Genre to filter by
                - energy_min (float): Minimum energy level (0.0-1.0)
                - energy_max (float): Maximum energy level (0.0-1.0)
                - danceability_min (float): Minimum danceability (0.0-1.0)
                - danceability_max (float): Maximum danceability (0.0-1.0)

        Returns:
            List of sample dictionaries with similarity scores

        Raises:
            SearchError: If search fails or query is invalid
        """
        start_time = time.time()

        # Validate query
        if not query or not query.strip():
            raise SearchError("Search query cannot be empty")

        logger.info(f"Searching for samples with query: '{query}' (limit={limit}, filters={filters})")

        try:
            # Step 1: Generate embedding from query
            logger.debug("Generating embedding for search query")
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Step 2: Query PostgreSQL for similar embeddings
            logger.debug("Querying PostgreSQL for similar embeddings")
            similar_samples = await self._query_similar_embeddings(
                embedding=query_embedding,
                limit=limit * 2  # Get more results before filtering
            )

            if not similar_samples:
                logger.info(f"No similar samples found for query: '{query}'")
                return []

            # Extract sample IDs
            sample_ids = [s["sample_id"] for s in similar_samples]

            # Step 3: Fetch metadata from PostgreSQL
            logger.debug(f"Fetching metadata for {len(sample_ids)} samples from PostgreSQL")
            enriched_results = await self._enrich_with_metadata(
                similar_samples=similar_samples,
                sample_ids=sample_ids,
                filters=filters
            )

            # Apply limit after filtering
            enriched_results = enriched_results[:limit]

            execution_time = (time.time() - start_time) * 1000
            logger.info(
                f"Search completed in {execution_time:.2f}ms: "
                f"query='{query}', results={len(enriched_results)}"
            )

            return enriched_results

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {str(e)}", exc_info=True)
            raise SearchError(f"Search failed: {str(e)}", query=query)

    async def find_similar(
        self,
        sample_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find samples similar to a given sample.

        Args:
            sample_id: ID of the sample to find similar matches for
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of similar sample dictionaries with similarity scores

        Raises:
            SearchError: If sample not found or search fails
        """
        start_time = time.time()

        logger.info(f"Finding samples similar to sample_id={sample_id} (limit={limit})")

        try:
            # Step 1: Get sample's embedding from PostgreSQL
            logger.debug(f"Fetching embedding for sample_id={sample_id}")
            embedding = await self._get_sample_embedding(sample_id)

            if not embedding:
                raise SearchError(
                    f"No embedding found for sample_id={sample_id}. Sample may not be embedded yet."
                )

            # Step 2: Query for similar embeddings (exclude the original sample)
            logger.debug("Querying for similar embeddings")
            similar_samples = await self._query_similar_embeddings(
                embedding=embedding,
                limit=limit + 1,  # Get one extra to exclude original
                exclude_sample_id=sample_id
            )

            if not similar_samples:
                logger.info(f"No similar samples found for sample_id={sample_id}")
                return []

            # Extract sample IDs
            sample_ids = [s["sample_id"] for s in similar_samples]

            # Step 3: Fetch metadata from PostgreSQL
            logger.debug(f"Fetching metadata for {len(sample_ids)} samples")
            enriched_results = await self._enrich_with_metadata(
                similar_samples=similar_samples,
                sample_ids=sample_ids
            )

            # Apply limit
            enriched_results = enriched_results[:limit]

            execution_time = (time.time() - start_time) * 1000
            logger.info(
                f"Similar search completed in {execution_time:.2f}ms: "
                f"sample_id={sample_id}, results={len(enriched_results)}"
            )

            return enriched_results

        except Exception as e:
            logger.error(f"Similar search failed for sample_id={sample_id}: {str(e)}", exc_info=True)
            raise SearchError(f"Similar search failed: {str(e)}")

    async def _query_similar_embeddings(
        self,
        embedding: List[float],
        limit: int,
        exclude_sample_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query PostgreSQL for similar embeddings using cosine similarity with numpy.

        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            exclude_sample_id: Optional sample ID to exclude from results

        Returns:
            List of dicts with sample_id and similarity scores
        """
        try:
            # Build query to fetch all embeddings from PostgreSQL
            query = select(SampleEmbedding.sample_id, SampleEmbedding.vibe_vector)

            if exclude_sample_id is not None:
                query = query.where(SampleEmbedding.sample_id != exclude_sample_id)

            result = await self.db.execute(query)
            rows = result.all()

            if not rows:
                logger.debug("No embeddings found in database")
                return []

            # Calculate cosine similarity for each embedding using numpy
            query_vec = np.array(embedding, dtype=np.float32)
            similarities = []

            for sample_id, vibe_vector in rows:
                if vibe_vector is None:
                    continue

                # Convert to numpy array and calculate cosine similarity
                db_vec = np.array(vibe_vector, dtype=np.float32)

                # Cosine similarity = (A · B) / (||A|| * ||B||)
                dot_product = np.dot(query_vec, db_vec)
                norm_query = np.linalg.norm(query_vec)
                norm_db = np.linalg.norm(db_vec)

                if norm_query > 0 and norm_db > 0:
                    similarity = dot_product / (norm_query * norm_db)
                else:
                    similarity = 0.0

                # Only include if above threshold
                if similarity >= 0.7:
                    similarities.append({
                        "sample_id": sample_id,
                        "similarity": float(similarity)
                    })

            # Sort by similarity (descending) and apply limit
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:limit]

            logger.debug(f"Found {len(results)} similar embeddings")
            return results

        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}", exc_info=True)
            raise SearchError(f"Vector search failed: {str(e)}")

    async def _get_sample_embedding(self, sample_id: int) -> Optional[List[float]]:
        """
        Get embedding vector for a specific sample from PostgreSQL.

        Args:
            sample_id: Sample ID to fetch embedding for

        Returns:
            Embedding vector or None if not found
        """
        try:
            query = select(SampleEmbedding.vibe_vector).where(
                SampleEmbedding.sample_id == sample_id
            )
            result = await self.db.execute(query)
            row = result.first()

            if not row:
                return None

            # PostgreSQL ARRAY type returns as list directly
            return list(row[0]) if row[0] else None

        except Exception as e:
            logger.error(f"Failed to fetch embedding for sample_id={sample_id}: {str(e)}")
            return None

    async def _enrich_with_metadata(
        self,
        similar_samples: List[Dict[str, Any]],
        sample_ids: List[int],
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Enrich similarity results with full metadata from PostgreSQL.

        Args:
            similar_samples: List of samples with similarity scores from Turso
            sample_ids: List of sample IDs to fetch
            filters: Optional filters to apply

        Returns:
            List of enriched sample dictionaries
        """
        if not sample_ids:
            return []

        # Build base query
        query = (
            select(Sample, VibeAnalysis)
            .outerjoin(VibeAnalysis, VibeAnalysis.sample_id == Sample.id)
            .where(Sample.id.in_(sample_ids))
        )

        # Apply filters if provided
        if filters:
            filter_conditions = []

            # BPM filters
            if "bpm_min" in filters:
                filter_conditions.append(Sample.bpm >= filters["bpm_min"])
            if "bpm_max" in filters:
                filter_conditions.append(Sample.bpm <= filters["bpm_max"])

            # Genre filter
            if "genre" in filters:
                filter_conditions.append(Sample.genre == filters["genre"])

            # Energy filters
            if "energy_min" in filters:
                filter_conditions.append(VibeAnalysis.energy_level >= filters["energy_min"])
            if "energy_max" in filters:
                filter_conditions.append(VibeAnalysis.energy_level <= filters["energy_max"])

            # Danceability filters
            if "danceability_min" in filters:
                filter_conditions.append(VibeAnalysis.danceability >= filters["danceability_min"])
            if "danceability_max" in filters:
                filter_conditions.append(VibeAnalysis.danceability <= filters["danceability_max"])

            if filter_conditions:
                query = query.where(and_(*filter_conditions))

        # Execute query
        result = await self.db.execute(query)
        rows = result.all()

        # Create similarity score lookup
        similarity_map = {s["sample_id"]: s["similarity"] for s in similar_samples}

        # Build enriched results
        enriched_results = []
        for row in rows:
            sample, vibe = row

            result_dict = {
                "id": sample.id,
                "title": sample.title,
                "bpm": sample.bpm,
                "musical_key": sample.musical_key,
                "genre": sample.genre,
                "duration": sample.duration,
                "similarity": similarity_map.get(sample.id, 0.0),
                "file_path": sample.file_path,
                "tags": sample.tags or [],
            }

            # Add vibe analysis if available
            if vibe:
                result_dict.update({
                    "mood_primary": vibe.mood_primary,
                    "mood_secondary": vibe.mood_secondary,
                    "energy_level": vibe.energy_level,
                    "danceability": vibe.danceability,
                    "acousticness": vibe.acousticness,
                    "instrumentalness": vibe.instrumentalness,
                    "vibe_tags": vibe.texture_tags or [],
                })

            enriched_results.append(result_dict)

        # Sort by similarity score (descending)
        enriched_results.sort(key=lambda x: x["similarity"], reverse=True)

        logger.debug(f"Enriched {len(enriched_results)} samples with metadata")
        return enriched_results
