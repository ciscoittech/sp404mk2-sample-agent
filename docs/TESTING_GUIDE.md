# SP404MK2 Sample Agent - Testing Guide

**Framework**: Playwright (MCP Chrome DevTools) + pytest + CLI validation
**Status**: Ready for test suite implementation
**Last Updated**: 2025-11-16

---

## Quick Start

```bash
# Verify services are running
./venv/bin/python backend/run.py &
cd react-app && npm run dev &

# Check embeddings (need >= 30)
psql -d sp404_samples -c "SELECT COUNT(*) FROM sample_embeddings;"

# If < 30: Generate embeddings (wait 5 minutes)
./venv/bin/python backend/scripts/generate_embeddings.py --resume &

# Run all tests
pytest backend/tests/ -v
npx playwright test frontend/tests/e2e/ --headed
```

---

## Backend Tests

```bash
# All tests
pytest backend/tests/ -v

# Specific file
pytest backend/tests/test_journey_vibe_search.py -v

# Single test
pytest backend/tests/test_journey_vibe_search.py::test_basic -v

# With coverage
pytest backend/tests/ --cov=backend/app

# Debug output
pytest backend/tests/ -v -s
```

## Frontend Tests

```bash
# All tests (headed - see browser)
npx playwright test frontend/tests/e2e/ --headed

# Specific file
npx playwright test frontend/tests/e2e/journey-2-vibe-search.spec.js --headed

# Debug mode
npx playwright test --debug
```

---

## Debugging

### Service Health

```bash
# Backend
curl http://localhost:8000/api/v1/health

# Frontend
curl http://localhost:8100/

# Embeddings
psql -d sp404_samples -c "SELECT COUNT(*) FROM sample_embeddings;"
```

### Common Issues

**Vibe search tests skipped**: Generate embeddings
```bash
./venv/bin/python backend/scripts/generate_embeddings.py --resume
```

**Connection refused**: Start services
```bash
./venv/bin/python backend/run.py &
cd react-app && npm run dev &
```

**Database locked**: Run tests sequentially
```bash
pytest backend/tests/ -n 0
```

---

## Test Organization

```
backend/tests/
├── utils/
│   ├── embedding_validator.py    # Embedding status checks
│   ├── cli_validator.py          # CLI output parsing
│   └── __init__.py
├── test_journey_sample_collection.py
├── test_journey_vibe_search.py
├── test_journey_kit_building.py
├── test_journey_batch.py
└── test_journey_sp404_export.py

frontend/tests/e2e/
├── journey-1-samples.spec.js
├── journey-2-vibe-search.spec.js
├── journey-3-kits.spec.js
├── journey-4-batch.spec.js
└── journey-5-export.spec.js
```

---

## Performance Targets

| Operation | Target |
|-----------|--------|
| Vibe search | < 2000ms |
| YouTube analysis | < 3000ms |
| Kit recommendations | < 1500ms |
| Sample list | < 500ms |
| Export | < 5000ms |

---

See `docs/USER_JOURNEY_TESTING.md` for detailed test specifications and expected behaviors.

*Last Updated: 2025-11-16*
