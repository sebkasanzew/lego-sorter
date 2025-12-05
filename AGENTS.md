# LEGO Sorter AI Agent Instructions

> **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 10 most common tasks  
> **Glossary**: [docs/GLOSSARY.md](docs/GLOSSARY.md) - Terminology

## Project Overview

Blender simulation of LEGO sorting machine via Model Context Protocol (MCP). **Code-driven** (no .blend files). Pipeline: **collection → conveyor → separation → identification → sorting → output**.

## Architecture

```
Jupyter Notebook (lego_sorter_pipeline.ipynb)
         ↓
MCP Client (utils/blender_mcp_client.py)
         ↓ TCP Socket (localhost:9876)
Blender + MCP Addon
         ↓
Scene State (ephemeral)
```

**Critical**: Test MCP connection before operations.

## Setup

```bash
pip install -r requirements.txt
jupyter notebook
# Open lego_sorter_pipeline.ipynb
# Run cells sequentially
```

**Blender**: Press N → BlenderMCP → "Connect to MCP server"

## Core Components

### Jupyter Notebooks
- **`lego_sorter_pipeline.ipynb`** - Main pipeline (run cells sequentially)
- **`quick_experiments.ipynb`** - Quick tests/debugging

### Blender Scripts (`blender/`)

| Script | Purpose |
|--------|---------|
| `clear_scene.py` | Reset scene |
| `create_sorting_bucket.py` | Hollow bucket (boolean ops) |
| `create_conveyor_belt.py` | Inclined transport |
| `import_lego_parts.py` | 70+ LDraw parts |
| `animate_lego_physics.py` | Rigid body physics |

### Pipeline Execution Order
1. clear_scene → 2. bucket → 3. conveyor → 4. parts → 5. physics

## Code Patterns

### Blender Scripts (Auto-Execute)
```python
def main():
    """Main entry point."""
    # Implementation
    pass

main()  # Auto-execute
```

### Notebook Usage
```python
from utils.blender_mcp_client import BlenderMCPClient

client = BlenderMCPClient()
client.test_connection()
client.execute_script_file('blender/clear_scene.py', 'Clear')
client.execute_code("import bpy; print(bpy.data.objects)", "Info")
```

### Key Conventions
- **Collections**: `"bucket"`, `"lego_parts"`, `"conveyor_belt"`
- **Null checks**: Always verify `bpy.context.active_object` is not None
- **Type hints**: `Optional[Object]` with isinstance guards

### File Organization

```
lego-sorter/
├── lego_sorter_pipeline.ipynb  # Main pipeline
├── quick_experiments.ipynb     # Quick tests
├── blender/                    # Blender scripts (auto-executable)
├── utils/                      # MCP client, validation
├── tests/                      # Test scenarios
└── docs/                       # Architecture, guides, glossary
```

### Configuration Constants

```python
# Physics
LEGO_MASS = 0.002         # 2 grams per brick
LEGO_FRICTION = 0.9       # High friction
GRAVITY_SCALE = 9.81      # Standard gravity

# LDraw
LDRAW_PARTS_PATH = "/Applications/Studio 2.0/ldraw/parts/"

# Conveyor
CONVEYOR_LENGTH = 1.5     # Blender units
CONVEYOR_ANGLE = 0.15     # ~8.6°
BELT_FRICTION = 0.8
```

## Code-Driven Philosophy

**Zero Binary Dependencies**: No .blend files. Full Git version control. Complete reproducibility.

**Scene State**: Ephemeral - cleared and recreated each run.

## Testing

In notebook:
```python
# Validate scene
client.execute_script_file('utils/validate_scene.py', 'Validate')
```

CLI:
```bash
pytest tests/
```

## Visual Verification (MANDATORY)

**ALWAYS verify geometry changes using at least 2 camera angles.**

### Verification Cameras
Run `blender/setup_verification_cameras.py` to create standard cameras:
- `Camera_Side` - Verify slat angles, conveyor incline
- `Camera_Overview` - Overall geometry check  
- `Camera_Top` - Layout from above
- `Camera_Bucket_Detail` - Bucket floor attachment

### Verification Workflow
```python
# 1. Setup cameras (once per session)
exec(open('blender/setup_verification_cameras.py').read())

# 2. Switch to camera view
set_viewport_to_camera('Camera_Side')

# 3. Take screenshot via MCP
# mcp_blender_get_viewport_screenshot

# 4. Switch to second camera
set_viewport_to_camera('Camera_Overview')

# 5. Take second screenshot
# mcp_blender_get_viewport_screenshot
```

**Rule**: After ANY geometry modification, verify with minimum 2 camera views before reporting completion.

## Documentation Map

| Need | Document |
|------|----------|
| Quick tasks | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Terminology | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Project info | [README.md](README.md) |

## Communication

Be extremely concise. Sacrifice grammar for concision.

