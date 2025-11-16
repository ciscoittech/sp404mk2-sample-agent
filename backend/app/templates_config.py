"""
Jinja2 templates configuration - shared across endpoints to avoid circular imports
"""
import os
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader, Environment, ChoiceLoader

# Determine paths based on environment (Docker vs local)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Build list of valid template directories
template_dirs = []

# Local paths (development)
local_backend = os.path.join(base_dir, "backend", "templates")
local_frontend = os.path.join(base_dir, "frontend")

# Docker paths
docker_backend = "/app/backend/templates"
docker_frontend = "/app/frontend"

# Add all paths that exist
for path in [local_backend, docker_backend, local_frontend, docker_frontend]:
    if os.path.exists(path) and path not in template_dirs:
        template_dirs.append(path)
        print(f"✓ Template path: {path}")

if not template_dirs:
    raise RuntimeError("No template directories found!")

# Configure Jinja2 with all available template directories
jinja_env = Environment(loader=FileSystemLoader(template_dirs))
templates = Jinja2Templates(env=jinja_env)

# Export frontend_dir for static file mounting
frontend_dir = local_frontend if os.path.exists(local_frontend) else docker_frontend
