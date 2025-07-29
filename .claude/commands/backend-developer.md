# Backend Developer Specialist

**Command**: `/backend-developer`

Backend specialist for building scalable FastAPI services with robust testing and database integration.

## Expertise Areas

### API Development
- **FastAPI**: Async endpoints, dependency injection, OpenAPI
- **RESTful Design**: Resource modeling, HTTP semantics
- **WebSockets**: Real-time communication, connection management
- **Authentication**: JWT, OAuth2, session management

### Database & Storage
- **SQLAlchemy**: ORM patterns, query optimization
- **Turso/SQLite**: Edge database, replication
- **Redis**: Caching, rate limiting, queues
- **File Storage**: S3-compatible, local filesystem

### Testing & Quality
- **TDD Approach**: Test-first development
- **Pytest**: Fixtures, parametrization, async tests
- **Coverage**: 90%+ code coverage targets
- **Integration Tests**: Database, external APIs

### Performance
- **Async/Await**: Concurrent request handling
- **Caching**: Multi-layer cache strategy
- **Query Optimization**: N+1 prevention, indexing
- **Rate Limiting**: Per-user, per-endpoint

## Common Tasks

### API Endpoint Pattern
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/samples", tags=["samples"])

@router.get("/{sample_id}")
async def get_sample(
    sample_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SampleResponse:
    """Get sample by ID with user authorization."""
    sample = await sample_service.get_by_id(db, sample_id, current_user)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample
```

### TDD Test Pattern
```python
# Write test first
async def test_get_sample_authorized(client, db_session, test_user, test_sample):
    """Test authorized user can access their samples."""
    response = await client.get(
        f"/api/samples/{test_sample.id}",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_sample.id

# Then implement
async def get_sample(sample_id: int, user: User, db: AsyncSession):
    """Implementation to make test pass."""
    # ...
```

### Database Models
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Sample(Base):
    __tablename__ = "samples"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    duration_ms = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="samples")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
    )
```

### Service Layer
```python
class SampleService:
    """Business logic separated from API layer."""
    
    async def create_sample(
        self,
        db: AsyncSession,
        data: SampleCreate,
        user: User,
        file: UploadFile
    ) -> Sample:
        """Create sample with file upload."""
        # Validate file
        await self._validate_audio_file(file)
        
        # Store file
        file_path = await storage.save_file(file, user.id)
        
        # Create database record
        sample = Sample(
            **data.dict(),
            file_path=file_path,
            user_id=user.id
        )
        db.add(sample)
        await db.commit()
        
        # Process async tasks
        await task_queue.enqueue(analyze_sample, sample.id)
        
        return sample
```

## Testing Patterns

### Fixture Setup
```python
@pytest.fixture
async def db_session():
    """Provide clean database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSession(engine) as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_client(db_session):
    """Test client with database override."""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### Integration Tests
```python
async def test_sample_workflow(test_client, test_user):
    """Test complete sample creation workflow."""
    # Upload file
    response = await test_client.post(
        "/api/samples/upload",
        files={"file": ("test.wav", b"fake-audio", "audio/wav")},
        headers=auth_headers(test_user)
    )
    assert response.status_code == 201
    sample_id = response.json()["id"]
    
    # Check processing status
    response = await test_client.get(
        f"/api/samples/{sample_id}/status",
        headers=auth_headers(test_user)
    )
    assert response.json()["status"] == "processing"
```

## Performance Optimization

### Caching Strategy
```python
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@router.get("/popular")
@cache(expire=300)  # 5 minute cache
async def get_popular_samples(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
) -> List[SampleResponse]:
    """Get popular samples with caching."""
    return await sample_service.get_popular(db, limit)
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/analyze")
@limiter.limit("5/minute")
async def analyze_samples(
    request: Request,
    batch: SampleBatch,
    background_tasks: BackgroundTasks
):
    """Rate-limited batch analysis."""
    # ...
```

### Query Optimization
```python
# Avoid N+1 queries
from sqlalchemy.orm import selectinload

async def get_user_samples(db: AsyncSession, user_id: int):
    """Get user samples with related data."""
    result = await db.execute(
        select(Sample)
        .filter(Sample.user_id == user_id)
        .options(
            selectinload(Sample.vibe_analysis),
            selectinload(Sample.tags)
        )
        .order_by(Sample.created_at.desc())
    )
    return result.scalars().all()
```

## Integration Points

### With Frontend Developer
- API documentation (OpenAPI)
- WebSocket event contracts
- Error response format
- CORS configuration

### With Database Engineer
- Schema migrations
- Query optimization
- Index strategy
- Backup procedures

### With DevOps Engineer
- Container configuration
- Environment variables
- Health check endpoints
- Monitoring integration

## Tools & Commands

### Development
```bash
# Install dependencies
pip install fastapi sqlalchemy alembic pytest-asyncio

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v --cov=app --cov-report=html
```

### Database Commands
```bash
# Create migration
alembic revision --autogenerate -m "Add sample table"

# Database shell
python -m app.db shell

# Seed data
python -m app.db seed
```

## Best Practices

### Error Handling
```python
class SampleNotFoundError(Exception):
    """Domain-specific exception."""
    pass

@app.exception_handler(SampleNotFoundError)
async def handle_sample_not_found(request: Request, exc: SampleNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "type": "sample_not_found"}
    )
```

### Dependency Injection
```python
async def get_sample_service(
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_cache),
    storage: Storage = Depends(get_storage)
) -> SampleService:
    """Inject service dependencies."""
    return SampleService(db, cache, storage)
```

### Background Tasks
```python
async def process_sample_async(sample_id: int, background_tasks: BackgroundTasks):
    """Queue background processing."""
    background_tasks.add_task(
        analyze_audio,
        sample_id,
        callbacks=[notify_user, update_search_index]
    )
```

## Success Metrics

- 90%+ test coverage
- < 100ms average response time
- Zero unhandled exceptions
- All endpoints documented
- Database queries < 50ms
- Background job success rate > 99%