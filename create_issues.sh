#!/bin/bash

echo "Creating GitHub issues for Cloud Storage Integration..."

# Issue 1: R2 Storage Service Foundation
gh issue create \
  --title "R2 Storage Service Foundation" \
  --body "Create CloudStorageService class for R2 integration.

Tasks:
- Add R2 config to settings  
- Create CloudStorageService class
- Implement upload/download/delete methods
- Add unit tests
- Document setup

Part of #44" \
  --label "enhancement" \
  --label "backend" \
  --label "infrastructure"

sleep 2

# Issue 2: Database Schema Updates
gh issue create \
  --title "Database Schema Updates for Cloud Storage" \
  --body "Update Sample model for cloud storage metadata.

Tasks:
- Add storage_url field
- Add storage_key field  
- Add storage_type enum
- Create migration script
- Update sample service
- Update tests

Part of #44" \
  --label "enhancement" \
  --label "database" \
  --label "backend"

sleep 2

# Issue 3: Batch Processing Model
gh issue create \
  --title "Batch Processing Model and Service" \
  --body "Create batch processing data model and service.

Tasks:
- Create BatchProcess model
- Create BatchProcessService
- Implement batch discovery
- Implement progress tracking
- Add cancellation support
- Create background task

Part of #44" \
  --label "enhancement" \
  --label "backend" \
  --label "feature"

sleep 2

# Issue 4: Batch Upload API
gh issue create \
  --title "Batch Upload API Endpoints" \
  --body "Create API endpoints for batch processing.

Endpoints:
- POST /api/v1/samples/batch - Start batch
- GET /api/v1/samples/batch/{id} - Status
- GET /api/v1/samples/batches - List batches
- DELETE /api/v1/samples/batch/{id} - Cancel
- Add auth and tests

Part of #44" \
  --label "enhancement" \
  --label "api" \
  --label "backend"

sleep 2

# Issue 5: WebSocket Progress
gh issue create \
  --title "WebSocket Progress Updates" \
  --body "Add real-time batch progress via WebSocket.

Tasks:
- Create /ws/batch/{id} endpoint
- Implement progress publishing
- Add connection management
- Handle reconnection
- Create TS types
- Add tests

Part of #44" \
  --label "enhancement" \
  --label "websocket" \
  --label "backend"

sleep 2

# Issue 6: Processing Pipeline
gh issue create \
  --title "File Processing Pipeline Integration" \
  --body "Integrate audio analysis into batch pipeline.

Tasks:
- Integrate local audio analysis
- Queue samples for AI analysis
- Implement rate limiting
- Add retry logic
- Store analysis results
- Update metadata

Part of #44" \
  --label "enhancement" \
  --label "backend" \
  --label "integration"

sleep 2

# Issue 7: Upload UI
gh issue create \
  --title "Batch Upload UI Component" \
  --body "Build frontend interface for batch uploads.

Tasks:
- Create drag-and-drop zone
- Implement directory selection
- Add file validation
- Show file preview
- Create confirmation dialog
- Style with DaisyUI

Part of #44" \
  --label "enhancement" \
  --label "frontend" \
  --label "ui"

sleep 2

# Issue 8: Progress Dashboard
gh issue create \
  --title "Batch Progress Dashboard" \
  --body "Build batch processing dashboard UI.

Tasks:
- Create batch list view
- Implement progress bars
- Add current file indicator
- Show statistics
- Add cancel/retry buttons
- WebSocket integration

Part of #44" \
  --label "enhancement" \
  --label "frontend" \
  --label "ui"

sleep 2

# Issue 9: R2 Configuration
gh issue create \
  --title "R2 Configuration and CORS Setup" \
  --body "Configure R2 bucket and CORS for streaming.

Tasks:
- Document bucket creation
- Configure CORS
- Set up custom domain (optional)
- Configure lifecycle rules
- Add backup strategy docs
- Create setup script

Part of #44" \
  --label "infrastructure" \
  --label "deployment" \
  --label "documentation"

sleep 2

# Issue 10: Migration Tool
gh issue create \
  --title "Migration Tool for Existing Samples" \
  --body "Build tool to migrate existing samples to R2.

Tasks:
- Create migration script
- Add progress tracking
- Handle duplicate detection
- Update database records
- Add dry-run mode
- Document process

Part of #44" \
  --label "enhancement" \
  --label "backend" \
  --label "migration"

sleep 2

# Issue 11: Error Handling
gh issue create \
  --title "Error Handling and Monitoring" \
  --body "Implement comprehensive error handling.

Tasks:
- Create error tracking
- Add retry queue
- Implement error reporting UI
- Add health checks
- Create alerts
- Add detailed logging

Part of #44" \
  --label "enhancement" \
  --label "backend" \
  --label "reliability"

sleep 2

# Issue 12: Performance Testing
gh issue create \
  --title "Performance Testing and Optimization" \
  --body "Test and optimize batch processing performance.

Tasks:
- Create performance test suite
- Test with 1000+ samples
- Optimize database queries
- Implement connection pooling
- Add caching
- Document limits

Part of #44" \
  --label "performance" \
  --label "testing" \
  --label "backend"

echo "All issues created successfully!"