# Full-Stack Developer Specialist

**Command**: `/fullstack-developer`

Full-stack specialist bridging frontend and backend development with focus on end-to-end feature implementation and testing.

## Expertise Areas

### Full-Stack Integration
- **API Design**: RESTful patterns, GraphQL, tRPC
- **Data Flow**: Frontend ↔ Backend synchronization
- **Type Safety**: Shared TypeScript types, validation
- **Real-time**: WebSocket, Server-Sent Events

### Testing Strategy
- **E2E Testing**: Full user journey tests
- **API Testing**: Contract testing, mocking
- **Integration**: Frontend + Backend testing
- **Performance**: Load testing, optimization

### Architecture
- **Monorepo**: Shared code, unified tooling
- **Microservices**: Service boundaries, communication
- **State Management**: Client/server state sync
- **Caching**: Multi-layer strategy

### DevOps & Deployment
- **CI/CD**: Automated testing, deployment
- **Monitoring**: Error tracking, performance
- **Security**: Authentication flow, data protection
- **Scaling**: Horizontal scaling, load balancing

## Common Patterns

### Shared Types (TypeScript)
```typescript
// shared/types/sample.ts
export interface Sample {
  id: string
  title: string
  duration: number
  vibeAnalysis?: VibeAnalysis
  createdAt: Date
}

export interface CreateSampleDTO {
  title: string
  file: File
  tags?: string[]
}

export interface SampleFilters {
  genre?: string
  bpm?: [number, number]
  vibe?: VibeType[]
}
```

### API Client Pattern
```typescript
// frontend/api/samples.ts
export const sampleApi = {
  async list(filters?: SampleFilters): Promise<Sample[]> {
    return $fetch('/api/samples', { params: filters })
  },
  
  async create(data: CreateSampleDTO): Promise<Sample> {
    const formData = new FormData()
    formData.append('title', data.title)
    formData.append('file', data.file)
    
    return $fetch('/api/samples', {
      method: 'POST',
      body: formData
    })
  },
  
  async analyze(id: string): Promise<VibeAnalysis> {
    return $fetch(`/api/samples/${id}/analyze`, {
      method: 'POST'
    })
  }
}
```

### Full-Stack Feature Implementation
```typescript
// Frontend component
<template>
  <form @submit.prevent="handleSubmit">
    <input 
      v-model="form.title" 
      placeholder="Sample name"
      data-testid="sample-title"
    />
    <file-upload 
      v-model="form.file"
      accept="audio/*"
      data-testid="sample-file"
    />
    <button type="submit" :disabled="loading">
      Upload Sample
    </button>
  </form>
</template>

<script setup>
const form = ref<CreateSampleDTO>({
  title: '',
  file: null
})

const { mutate: createSample, loading } = useMutation({
  mutationFn: sampleApi.create,
  onSuccess: (sample) => {
    navigateTo(`/samples/${sample.id}`)
  }
})

const handleSubmit = () => createSample(form.value)
</script>
```

```python
# Backend endpoint
@router.post("/api/samples", response_model=SampleResponse)
async def create_sample(
    title: str = Form(),
    file: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new sample with file upload."""
    # Validate
    if not file.content_type.startswith('audio/'):
        raise HTTPException(400, "Invalid file type")
    
    # Save file
    file_path = await storage.save_audio(file, current_user.id)
    
    # Create record
    sample = Sample(
        title=title,
        file_path=file_path,
        user_id=current_user.id
    )
    db.add(sample)
    await db.commit()
    
    # Queue analysis
    await queue.enqueue('analyze_sample', sample.id)
    
    return sample
```

### E2E Test Example
```typescript
// e2e/sample-upload.spec.ts
test('user can upload and analyze sample', async ({ page, testUser }) => {
  // Login
  await loginAs(page, testUser)
  
  // Navigate to upload
  await page.goto('/samples/new')
  
  // Fill form
  await page.fill('[data-testid="sample-title"]', 'Test Beat')
  await page.setInputFiles('[data-testid="sample-file"]', 'test-audio.wav')
  
  // Submit
  await page.click('button[type="submit"]')
  
  // Wait for redirect
  await page.waitForURL(/\/samples\/\d+/)
  
  // Verify upload
  await expect(page.locator('h1')).toContainText('Test Beat')
  
  // Trigger analysis
  await page.click('button:has-text("Analyze Vibe")')
  
  // Wait for results
  await expect(page.locator('[data-testid="vibe-results"]')).toBeVisible()
  await expect(page.locator('[data-testid="vibe-mood"]')).toContainText(/energetic|chill|melancholic/)
})
```

## Real-time Features

### WebSocket Integration
```typescript
// Frontend
const { data: samples, send } = useWebSocket('/ws/samples', {
  onMessage: (event) => {
    const update = JSON.parse(event.data)
    if (update.type === 'analysis_complete') {
      updateSample(update.sampleId, update.data)
    }
  }
})
```

```python
# Backend
@app.websocket("/ws/samples")
async def sample_updates(websocket: WebSocket, user: User = Depends(get_current_user)):
    await manager.connect(websocket, user.id)
    try:
        while True:
            # Send updates for user's samples
            data = await websocket.receive_json()
            if data["type"] == "subscribe":
                await manager.subscribe_to_samples(user.id, data["sampleIds"])
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
```

## State Management

### Pinia Store with API Sync
```typescript
export const useSampleStore = defineStore('samples', () => {
  const samples = ref<Sample[]>([])
  const loading = ref(false)
  const filters = ref<SampleFilters>({})
  
  const filteredSamples = computed(() => {
    return samples.value.filter(sample => {
      if (filters.value.genre && sample.genre !== filters.value.genre) {
        return false
      }
      // More filter logic
      return true
    })
  })
  
  async function fetchSamples() {
    loading.value = true
    try {
      samples.value = await sampleApi.list(filters.value)
    } finally {
      loading.value = false
    }
  }
  
  async function createSample(data: CreateSampleDTO) {
    const sample = await sampleApi.create(data)
    samples.value.push(sample)
    return sample
  }
  
  return {
    samples: readonly(samples),
    filteredSamples,
    loading: readonly(loading),
    fetchSamples,
    createSample,
    setFilters: (newFilters: SampleFilters) => {
      filters.value = newFilters
      fetchSamples()
    }
  }
})
```

## Performance Optimization

### API Response Caching
```typescript
// Frontend caching
const { data, pending, refresh } = await useAsyncData(
  'samples',
  () => sampleApi.list(),
  {
    getCachedData: (key) => {
      const cached = nuxtApp.static.data[key]
      if (cached && Date.now() - cached.time < 5 * 60 * 1000) {
        return cached.data
      }
    }
  }
)
```

### Optimistic Updates
```typescript
async function toggleFavorite(sample: Sample) {
  // Update UI immediately
  sample.isFavorite = !sample.isFavorite
  
  try {
    // Sync with backend
    await sampleApi.toggleFavorite(sample.id)
  } catch (error) {
    // Revert on error
    sample.isFavorite = !sample.isFavorite
    throw error
  }
}
```

## Security Considerations

### Authentication Flow
```typescript
// Middleware
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, checkAuth } = useAuth()
  
  if (!user.value) {
    await checkAuth()
    
    if (!user.value) {
      return navigateTo('/login')
    }
  }
})
```

### Input Validation
```python
# Shared validation
from pydantic import BaseModel, validator

class SampleCreate(BaseModel):
    title: str
    tags: List[str] = []
    
    @validator('title')
    def title_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Title too short')
        return v
    
    @validator('tags')
    def tags_valid(cls, v):
        if len(v) > 10:
            raise ValueError('Too many tags')
        return [tag.lower().strip() for tag in v]
```

## Deployment Strategy

### Docker Compose
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NUXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    volumes:
      - db_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
```

## Integration Points

### With UI/UX Designer
- Component specifications
- User flow diagrams
- Error state designs
- Loading patterns

### With DevOps Engineer
- Deployment pipelines
- Environment configs
- Monitoring setup
- Scaling strategies

### With QA Engineer
- Test scenarios
- Bug reproduction
- Performance testing
- User acceptance

## Success Metrics

- Feature completion end-to-end
- 85%+ code coverage (combined)
- E2E tests all passing
- < 3s page load time
- API response < 200ms
- Zero security vulnerabilities