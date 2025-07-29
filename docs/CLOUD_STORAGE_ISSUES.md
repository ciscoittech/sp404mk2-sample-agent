# Cloud Storage Integration GitHub Issues

Epic: [#44 - Cloud Storage Integration for Batch Processing](https://github.com/ciscoittech/sp404mk2-sample-agent/issues/44)

## Issues to Create

### Issue #45: R2 Storage Service Foundation
**Labels**: `enhancement`, `backend`, `infrastructure`
**Description**: Create CloudStorageService class for R2 integration.

**Tasks**:
- [ ] Add R2 configuration to settings (access keys, bucket name, endpoint)
- [ ] Create `CloudStorageService` class with boto3 client
- [ ] Implement `upload_sample()` method
- [ ] Implement `download_sample()` method  
- [ ] Implement `delete_sample()` method
- [ ] Add unit tests for all methods
- [ ] Document R2 bucket setup process

**Acceptance Criteria**:
- Can upload a file to R2 and get back a storage key
- Can generate public URLs for samples
- All operations have error handling
- Tests pass with mocked R2 client

---

### Issue #46: Database Schema Updates for Cloud Storage
**Labels**: `enhancement`, `database`, `backend`
**Description**: Update Sample model for cloud storage metadata.

**Tasks**:
- [ ] Add `storage_url` field to Sample model
- [ ] Add `storage_key` field for R2 object key
- [ ] Add `storage_type` enum field (r2, local, etc.)
- [ ] Create Alembic migration script
- [ ] Update sample service to handle new fields
- [ ] Update tests for new schema

**Acceptance Criteria**:
- Migration runs successfully
- Existing samples remain functional
- New samples store R2 metadata

---

### Issue #47: Batch Processing Model and Service
**Labels**: `enhancement`, `backend`, `feature`
**Description**: Create batch processing data model and service.

**Tasks**:
- [ ] Create `BatchProcess` model with status tracking
- [ ] Create `BatchProcessService` for managing batches
- [ ] Implement batch discovery (scan directory)
- [ ] Implement progress tracking
- [ ] Add batch cancellation support
- [ ] Create background task for processing

**Acceptance Criteria**:
- Can create and track batch processing jobs
- Progress updates stored in database
- Can cancel in-progress batches

---

### Issue #48: Batch Upload API Endpoints
**Labels**: `enhancement`, `api`, `backend`
**Description**: Create API endpoints for batch processing operations.

**Endpoints**:
- [ ] `POST /api/v1/samples/batch` - Start new batch
- [ ] `GET /api/v1/samples/batch/{id}` - Get batch status
- [ ] `GET /api/v1/samples/batches` - List all batches
- [ ] `DELETE /api/v1/samples/batch/{id}` - Cancel batch
- [ ] Add proper authentication/authorization
- [ ] Write API tests

**Acceptance Criteria**:
- All endpoints return proper status codes
- Swagger documentation updated
- Integration tests pass

---

### Issue #49: WebSocket Progress Updates
**Labels**: `enhancement`, `websocket`, `backend`
**Description**: Add real-time batch progress via WebSocket.

**Tasks**:
- [ ] Create WebSocket endpoint `/ws/batch/{batch_id}`
- [ ] Implement progress event publishing
- [ ] Add connection management
- [ ] Handle reconnection logic
- [ ] Create TypeScript types for messages
- [ ] Add WebSocket tests

**Acceptance Criteria**:
- Clients receive real-time progress updates
- Multiple clients can monitor same batch
- Graceful disconnection handling

---

### Issue #50: File Processing Pipeline Integration
**Labels**: `enhancement`, `backend`, `integration`
**Description**: Integrate existing audio analysis into batch pipeline.

**Tasks**:
- [ ] Integrate local audio analysis (BPM, key detection)
- [ ] Queue samples for AI vibe analysis
- [ ] Implement rate limiting for API calls
- [ ] Add retry logic for failures
- [ ] Store analysis results in database
- [ ] Update sample metadata after processing

**Acceptance Criteria**:
- Each uploaded sample gets analyzed
- Rate limits are respected
- Failed analyses are retried

---

### Issue #51: Batch Upload UI Component
**Labels**: `enhancement`, `frontend`, `ui`
**Description**: Build frontend interface for batch uploads.

**Tasks**:
- [ ] Create drag-and-drop upload zone component
- [ ] Implement directory selection dialog
- [ ] Add file type validation (audio only)
- [ ] Show preview of selected files
- [ ] Create upload confirmation dialog
- [ ] Style with DaisyUI components

**Acceptance Criteria**:
- Can drag folders or select via dialog
- Shows count and size of audio files
- Validates file types before upload

---

### Issue #52: Batch Progress Dashboard
**Labels**: `enhancement`, `frontend`, `ui`
**Description**: Build batch processing dashboard UI.

**Tasks**:
- [ ] Create batch list view with status
- [ ] Implement progress bars for active batches
- [ ] Add current file indicator
- [ ] Show processing statistics
- [ ] Add cancel/retry buttons
- [ ] WebSocket integration for real-time updates

**Acceptance Criteria**:
- Shows all batches with their status
- Real-time progress updates
- Can cancel active batches

---

### Issue #53: R2 Configuration and CORS Setup
**Labels**: `infrastructure`, `deployment`, `documentation`
**Description**: Configure R2 bucket and CORS for web streaming.

**Tasks**:
- [ ] Document R2 bucket creation steps
- [ ] Configure CORS for web audio streaming
- [ ] Set up custom domain (optional)
- [ ] Configure lifecycle rules
- [ ] Add backup strategy documentation
- [ ] Create setup script

**Acceptance Criteria**:
- Audio files stream correctly in browser
- CORS headers properly configured
- Setup documented for reproduction

---

### Issue #54: Migration Tool for Existing Samples
**Labels**: `enhancement`, `backend`, `migration`
**Description**: Build tool to migrate existing samples to R2.

**Tasks**:
- [ ] Create migration script
- [ ] Add progress tracking
- [ ] Handle already-uploaded detection
- [ ] Update database records
- [ ] Add dry-run mode
- [ ] Document migration process

**Acceptance Criteria**:
- Can migrate existing Docker volume samples
- No data loss during migration
- Can resume interrupted migrations

---

### Issue #55: Error Handling and Monitoring
**Labels**: `enhancement`, `backend`, `reliability`
**Description**: Implement comprehensive error handling for batch processing.

**Tasks**:
- [ ] Create error tracking for failed uploads
- [ ] Add retry queue for failed samples
- [ ] Implement error reporting UI
- [ ] Add health check for R2 connectivity
- [ ] Create alerts for processing issues
- [ ] Add detailed logging

**Acceptance Criteria**:
- Failed samples can be retried
- Users see clear error messages
- Admins get notified of systematic failures

---

### Issue #56: Performance Testing and Optimization
**Labels**: `performance`, `testing`, `backend`
**Description**: Test and optimize batch processing performance.

**Tasks**:
- [ ] Create performance test suite
- [ ] Test with 1000+ sample batches
- [ ] Optimize database queries
- [ ] Implement connection pooling
- [ ] Add caching where appropriate
- [ ] Document performance limits

**Acceptance Criteria**:
- Can process 1000 samples without issues
- Memory usage stays reasonable
- Database queries are optimized

---

## Implementation Phases

### Phase 1: Foundation (Issues #45-47)
Storage service, database updates, batch processing model

### Phase 2: API and Processing (Issues #48-50)
REST endpoints, WebSocket updates, processing pipeline

### Phase 3: User Interface (Issues #51-52)
Upload UI and progress dashboard

### Phase 4: Infrastructure (Issues #53-54)
R2 setup and migration tools

### Phase 5: Production Ready (Issues #55-56)
Error handling and performance optimization

---

## Next Steps

1. Wait for GitHub API to recover
2. Create remaining issues manually or retry script
3. Start with Issue #45 (R2 Storage Service Foundation)
4. Implement in order of dependencies

## Cost Estimates

- **Current**: Free tier covers 1,448 samples (~7.2GB)
- **Growth to 20GB**: ~$0.15/month
- **Growth to 100GB**: ~$1.35/month
- **No bandwidth charges** (R2 advantage for streaming)