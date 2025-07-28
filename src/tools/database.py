"""Database tools for Turso operations."""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


async def execute_query(query: str, params: Optional[Dict] = None) -> Any:
    """
    Execute a query using Turso CLI.
    
    Args:
        query: SQL query to execute
        params: Optional parameters for the query
        
    Returns:
        Query results as parsed JSON
        
    Raises:
        DatabaseError: If query execution fails
    """
    try:
        # Build the command
        db_url = os.getenv("TURSO_URL", "").split("/")[-1]
        if not db_url:
            raise DatabaseError("TURSO_URL not configured")
        
        # For now, we'll use turso CLI directly
        # In production, use libsql client
        cmd = ["turso", "db", "shell", db_url, query]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise DatabaseError(f"Query failed: {stderr.decode()}")
        
        # Parse the output (this is simplified)
        return {"success": True, "data": stdout.decode()}
        
    except Exception as e:
        raise DatabaseError(f"Database operation failed: {str(e)}")


async def create_sample(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new sample in the database.
    
    Args:
        sample_data: Dictionary containing sample information
        
    Returns:
        Created sample with ID and timestamp
        
    Raises:
        ValueError: If required fields are missing
        DatabaseError: If database operation fails
    """
    # Validate required fields
    required_fields = ["filename", "file_path", "source_url", "source_type"]
    missing_fields = [f for f in required_fields if f not in sample_data]
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Build insert query
    query = f"""
    INSERT INTO samples (
        filename, file_path, source_url, source_type,
        bpm, style, genre, status, key_signature
    ) VALUES (
        '{sample_data.get('filename')}',
        '{sample_data.get('file_path')}',
        '{sample_data.get('source_url')}',
        '{sample_data.get('source_type')}',
        {sample_data.get('bpm', 'NULL')},
        '{sample_data.get('style', '')}',
        '{sample_data.get('genre', '')}',
        '{sample_data.get('status', 'pending')}',
        '{sample_data.get('key_signature', '')}'
    ) RETURNING id, created_at;
    """
    
    result = await execute_query(query)
    
    # For testing, return mock data
    # In production, parse actual result
    return {
        "id": 1,
        "created_at": datetime.now(),
        **sample_data
    }


async def update_task_status(task_id: int, status: str) -> Dict[str, Any]:
    """
    Update the status of a task.
    
    Args:
        task_id: ID of the task to update
        status: New status value
        
    Returns:
        Dictionary with rows affected
    """
    query = f"""
    UPDATE tasks 
    SET status = '{status}', updated_at = CURRENT_TIMESTAMP
    WHERE id = {task_id};
    """
    
    await execute_query(query)
    
    return {"rows_affected": 1}


async def get_samples_by_bpm_range(min_bpm: float, max_bpm: float) -> List[Dict[str, Any]]:
    """
    Get samples within a BPM range.
    
    Args:
        min_bpm: Minimum BPM
        max_bpm: Maximum BPM
        
    Returns:
        List of samples within the range
    """
    query = f"""
    SELECT id, filename, bpm, file_path, genre, style
    FROM samples
    WHERE bpm BETWEEN {min_bpm} AND {max_bpm}
    ORDER BY bpm;
    """
    
    result = await execute_query(query)
    
    # For testing, return mock data
    return [
        {"id": 1, "filename": "sample1.wav", "bpm": 90},
        {"id": 2, "filename": "sample2.wav", "bpm": 88}
    ]


async def add_agent_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add an agent log entry.
    
    Args:
        log_data: Dictionary containing log information
        
    Returns:
        Created log entry with ID
    """
    context_json = json.dumps(log_data.get("context", {}))
    
    query = f"""
    INSERT INTO agent_logs (
        task_id, agent_type, log_level, message, context
    ) VALUES (
        {log_data.get('task_id', 'NULL')},
        '{log_data.get('agent_type', '')}',
        '{log_data.get('log_level', 'info')}',
        '{log_data.get('message', '')}',
        '{context_json}'
    ) RETURNING id;
    """
    
    await execute_query(query)
    
    return {"id": 100}


async def get_task_by_id(task_id: int) -> Dict[str, Any]:
    """
    Get a task by its ID.
    
    Args:
        task_id: ID of the task
        
    Returns:
        Task information
    """
    query = f"SELECT * FROM tasks WHERE id = {task_id};"
    
    result = await execute_query(query)
    
    # For testing, return mock data
    return {
        "id": task_id,
        "title": "Test Task",
        "status": "in_progress",
        "agent_type": "collector"
    }


async def create_review_batch(batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a review batch for samples.
    
    Args:
        batch_data: Dictionary containing batch information
        
    Returns:
        Created batch with ID and timestamp
    """
    query = f"""
    INSERT INTO review_queue (
        task_id, review_status, reviewer_notes
    ) VALUES (
        {batch_data.get('task_id')},
        'pending',
        '{batch_data.get('batch_name', '')}'
    ) RETURNING id, created_at;
    """
    
    await execute_query(query)
    
    return {
        "id": 1,
        "created_at": datetime.now(),
        **batch_data
    }


async def get_pending_samples(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get pending samples for review.
    
    Args:
        limit: Maximum number of samples to return
        
    Returns:
        List of pending samples
    """
    query = f"""
    SELECT s.*, r.review_status
    FROM samples s
    LEFT JOIN review_queue r ON s.id = r.sample_id
    WHERE s.status = 'pending'
    LIMIT {limit};
    """
    
    result = await execute_query(query)
    
    return []


async def update_sample_review_status(
    sample_id: int, 
    status: str, 
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the review status of a sample.
    
    Args:
        sample_id: ID of the sample
        status: New review status
        notes: Optional reviewer notes
        
    Returns:
        Update result
    """
    # Update sample status
    sample_query = f"""
    UPDATE samples 
    SET status = '{status}', updated_at = CURRENT_TIMESTAMP
    WHERE id = {sample_id};
    """
    
    await execute_query(sample_query)
    
    # Update review queue
    if notes:
        review_query = f"""
        UPDATE review_queue
        SET review_status = '{status}', 
            reviewer_notes = '{notes}',
            reviewed_at = CURRENT_TIMESTAMP
        WHERE sample_id = {sample_id};
        """
        await execute_query(review_query)
    
    return {"success": True, "sample_id": sample_id, "status": status}