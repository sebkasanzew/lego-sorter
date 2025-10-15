# LEGO Sorter AI Agent Instructions

> **Quick Start**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for the 10 most common tasks  
> **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for complete system design  
> **Terminology**: See [docs/GLOSSARY.md](docs/GLOSSARY.md) for definitions  
> **Type Hints**: See [docs/TYPE_IGNORE_GUIDE.md](docs/TYPE_IGNORE_GUIDE.md) for Pylance setup

## Project Overview

Blender-based simulation of a LEGO sorting machine using Model Context Protocol (MCP) for remote Blender control. The simulation models the complete pipeline: **collection → conveyor → separation → identification → sorting → output**.

**Key Principle**: Code-driven scene generation with **zero binary dependencies** (no .blend files). Everything is reproducible from Python scripts.

## Architecture Overview

```
Python Scripts (blender/*.py)
         ↓
MCP Client (utils/blender_mcp_client.py)
         ↓ TCP Socket (localhost:9876)
Blender + MCP Addon
         ↓
Scene State (ephemeral, recreated each run)
```

**Critical**: All Blender operations go through MCP server. Always test connection before operations.

## Essential Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start Blender MCP Server (REQUIRED)
# 1. Open Blender
# 2. Press N → BlenderMCP tab → "Connect to Claude"

# Run complete pipeline
python run_lego_sorter.py

# Test MCP connection
python utils/blender_mcp_client.py
```

**For detailed setup**: See [README.md](README.md)

## Core Components

### MCP-Blender Bridge (`utils/blender_mcp_client.py`)
- JSON over TCP socket communication
- Execute scripts: `client.execute_script_file('blender/script.py')`
- Always check connection: `client.test_connection()`

### Blender Scripts (`blender/` directory)

| Script | Purpose |
|--------|---------|
| `clear_scene.py` | Reset scene (always run first) |
| `create_sorting_bucket.py` | Hollow bucket with boolean operations |
| `create_conveyor_belt.py` | Inclined transport with physics |
| `import_lego_parts.py` | LDraw part import (70+ parts) |
| `animate_lego_physics.py` | Rigid body simulation setup |
| `setup_lighting.py` | Three-point lighting |
| `render_snapshot.py` | Multi-view orthographic renders |

### Standard Pipeline (`run_lego_sorter.py`)

```python
# Execution order (critical)
1. clear_scene.py          # Reset
2. create_sorting_bucket.py # Geometry
3. create_conveyor_belt.py  # Transport
4. import_lego_parts.py     # Assets
5. animate_lego_physics.py  # Physics
```

## Project-Specific Conventions

### Blender Script Patterns

```python
# All scripts follow this pattern:
def main():
    """Main entry point."""
    # Implementation
    pass

# Auto-execute (no if __name__ check)
main()
```

**Key Patterns**:
- **Auto-execution**: Scripts end with `main()` call
- **Collection Management**: Objects in named collections (`"bucket"`, `"lego_parts"`, `"conveyor_belt"`)
- **Null Checks**: Always check `bpy.context.active_object` for None
- **Boolean Operations**: Use DIFFERENCE modifier for hollow geometry
- **Type Hints**: Use `Optional[Object]` and guard with isinstance/None checks (see [TYPE_IGNORE_GUIDE.md](docs/TYPE_IGNORE_GUIDE.md))

### File Organization

```
lego-sorter/
├── blender/          # Blender scripts (auto-executable)
├── utils/            # MCP client, validation, debug helpers
├── docs/             # Architecture, guides, glossary
├── tests/            # Test scenarios
├── renders/          # Output images (not in git)
└── AGENTS.md         # This file
```

### Configuration Constants

```python
# Physics (from import_lego_parts.py, animate_lego_physics.py)
LEGO_MASS = 0.002         # 2 grams per typical brick
LEGO_FRICTION = 0.9       # High friction coefficient
GRAVITY_SCALE = 9.81      # Standard Earth gravity

# LDraw (from import_lego_parts.py)
LDRAW_PARTS_PATH = "/Applications/Studio 2.0/ldraw/parts/"  # macOS

# Conveyor (from create_conveyor_belt.py)
CONVEYOR_LENGTH = 1.5     # Blender units
CONVEYOR_ANGLE = 0.15     # Radians (~8.6°)
BELT_FRICTION = 0.8       # Physics coefficient
```

## Code-Driven Scene Philosophy

**Zero Binary Dependencies**: No .blend files saved or required.

**Benefits**:
- Full Git version control (no binary diffs)
- Complete reproducibility from source
- Independent component development
- Automated testing possible

**Scene State**: Ephemeral - cleared and recreated on each run.

## Key Integration Points

### MCP Communication
- Protocol: JSON over TCP socket
- Port: `localhost:9876`
- Command: `{"type": "execute_code", "params": {"code": "..."}}`
- Response: `{"status": "success/error", "result": "...", "message": "..."}`

### Blender API Patterns
- Operations: `bpy.ops.*` for scene manipulation
- Data access: `bpy.data.objects.get()` with None checks
- Collections: `bpy.data.collections.new()` + link to scene
- Physics: Rigid body with ACTIVE (dynamic) or PASSIVE (static) types

### External Dependencies
- **LDraw Library**: LEGO part geometry (must be installed)
- **BlenderMCP Addon**: Remote control (must be enabled in Blender)
- **fake-bpy-module**: Type hints for IDE (PyPI package)

## Testing & Validation

```bash
# Full pipeline test
python run_lego_sorter.py

# Validate scene state
python -c "from utils.blender_mcp_client import BlenderMCPClient; \
BlenderMCPClient().execute_script_file('utils/validate_scene.py')"

# Debug helpers (visual markers, state inspection)
# See utils/blender_debug.py for add_debug_marker(), etc.
```

**Common Issues**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#troubleshooting-quick-fixes)

## Documentation Map

| Need | Document |
|------|----------|
| Quick task reference | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| System design | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Common operations | [docs/COMMON_TASKS.md](docs/COMMON_TASKS.md) |
| Terminology | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Type hints setup | [docs/TYPE_IGNORE_GUIDE.md](docs/TYPE_IGNORE_GUIDE.md) |
| Project context | [README.md](README.md) |
| Version history | [CHANGELOG.md](CHANGELOG.md) |
| Session state | [CONTEXT.md](CONTEXT.md) |

## Physics Simulation Notes

The simulation models real sorting machine physics:
- Parts fall through bucket hole (0.24 unit diameter)
- Conveyor belt transports parts upward (friction-based)
- Physics validated at key frames (see `blender/diagnose_raycast_frame20.py`)
- Known issue: Occasional desync at frame 20 (under investigation)

**For detailed physics debugging**: See [docs/COMMON_TASKS.md](docs/COMMON_TASKS.md#debugging-physics)

