# LEGO Sorter AI Agent Instructions

## Project Overview

This is a Blender-based simulation for a LEGO sorting machine that uses the Model Context Protocol (MCP) to remotely control Blender. The project simulates the complete sorting pipeline: collection → conveyor → separation → identification → sorting → output.

## Architecture & Key Components

### 1. MCP-Blender Bridge (`utils/blender_mcp_client.py`)

- **Critical**: All Blender operations go through MCP server on `localhost:9876`
- Use `BlenderMCPClient` class for remote script execution
- Always test connection with `test_connection()` before operations
- Scripts must be executed via `execute_script_file()` or `execute_code()`
- **Socket Communication**: JSON commands over TCP with 8KB response buffer

### 2. Blender Script Structure (`blender/` directory)

- **Scene Management**: `clear_scene.py` - Always run first to reset state
- **Object Creation**: `create_sorting_bucket.py` - Boolean operations for hollow geometry
- **Conveyor System**: `create_conveyor_belt.py` - Inclined belt with friction-based transport
- **Asset Import**: `import_lego_parts.py` - LDraw file import with vertical arrangement
- **Physics Animation**: `animate_lego_physics.py` - Realistic gravity simulation and collision detection
- **Pattern**: Scripts use `main()` function and auto-execute when imported (no `if __name__ == "__main__"` checks)

### 3. Workflow Orchestration (`run_lego_sorter.py`)

- **Standard Pipeline**: clear → create bucket → create conveyor → import parts → setup physics
- **Error Handling**: Checks file existence before execution
- **User Feedback**: Emoji-based progress indicators (🧱, 🔍, 🎯, 1️⃣, 2️⃣, 3️⃣, 🎉)
- **Path Management**: Uses `sys.path.insert()` to add utils directory dynamically
- **Code-Driven Scene**: Complete scene recreation from Python scripts only

## Critical Developer Workflows

### Essential Setup Commands

```bash
# Install dependencies (includes fake-bpy-module for type hints)
pip install -r requirements.txt

# Run complete simulation
python run_lego_sorter.py

# Test MCP connection only
python utils/blender_mcp_client.py
```

### Blender MCP Server Setup (Required for ALL operations)

1. Open Blender → 3D View sidebar (N key) → BlenderMCP tab → "Connect to Claude"
2. Verify connection on `localhost:9876` before any script execution
3. **Never execute bpy commands without MCP connection**

### VSCode Configuration

- **Type Hints**: `fake-bpy-module-latest` provides bpy API stubs
- **Path Configuration**: `.vscode/settings.json` adds `blender/` and `utils/` to analysis paths
- **Linting**: Flake8 enabled with E501, W503, F401 ignored for Blender compatibility

### Typing & Pylance setup (recommended)

To avoid scattering `# type: ignore` and to get solid IntelliSense:

- Prefer versioned Blender stubs from PyPI that match your Blender version exactly:
   - macOS example: install one of `fake-bpy-module-4.2`, `fake-bpy-module-4.3`, or the exact version you use. Use `fake-bpy-module-latest` only when you are on the latest daily build.
- Ensure VS Code uses a Python interpreter where the package is installed (see Command Palette: Python: Select Interpreter).
- Keep `.vscode/settings.json` simple and rely on site-packages for stubs:
   - Use `python.analysis.extraPaths` only for project source roots (e.g., `blender/`, `utils/`).
   - If you have a local `typings/` folder, only keep project-specific additions there; avoid shipping full `bpy` or `mathutils` copies that may shadow the PyPI stubs. If you don’t need local additions, remove `typings/` or point `python.analysis.stubPath` elsewhere.
- Suggested Pylance knobs:
   - `python.analysis.typeCheckingMode`: `basic` (current) or `standard` if you want more coverage.
   - Optionally set `python.analysis.useLibraryCodeForTypes` to `false` to rely on stubs only.
- Prefer real types over `Any`:
   - `from bpy.types import Object, Material, Collection, Operator` and annotate function parameters/returns accordingly.
   - Use `mathutils.Vector` directly (provided by the stubs) instead of custom vector stubs.
  
Important note about VS Code / Pylance and Blender typings
- Use the `fake-bpy-module` (installed into your Python environment) for accurate Blender type stubs instead of the workspace `typings/` folder. Local `typings/` can shadow the site-package stubs and cause confusing diagnostics.
- Set Pylance's stub path to an empty project folder (we use `./typings-project`) to ensure Pylance picks up the `fake-bpy-module` from site-packages. Example `.vscode/settings.json` snippet:

   "python.analysis.stubPath": ["./typings-project"]

- If you currently have a `typings/` folder in the repo, archive or remove it (or move the useful bits into proper stubs) — do not keep it in the workspace root while relying on the PyPI stubs.
- If you must keep custom stubs, place them in a different folder and document that in `.vscode/settings.json` explicitly; avoid naming it `typings` at the project root.
- When you must downcast dynamic Blender attributes, prefer `typing.cast[...]` around the narrowest `bpy.types.*` type instead of `# type: ignore`.

Minimal example
- Before:
   - `import bpy  # type: ignore`
   - `obj: Any = bpy.context.active_object  # type: ignore`
- After (preferred pattern without cast):
   - `import bpy`
   - `from typing import Optional`
   - `from bpy.types import Object`
   - `obj: Optional[Object] = None`
   - `if isinstance(bpy.context.active_object, Object):`
         - `obj = bpy.context.active_object`
   - `# Now `obj` is either an Object or None; guard before use`

This keeps type-checkers happy without silencing them globally.

## Project-Specific Conventions

### Blender Script Patterns

- **Auto-execution**: All scripts end with `main()` call - no conditional `if __name__ == "__main__"`
- **Collection Management**: Objects organized in named collections (`"bucket"`, `"lego_parts"`)
- **Error Handling**: Extensive null checks for `bpy.context.active_object`
- **Geometry Creation**: Boolean operations for complex shapes (see bucket creation)
- **Function Signatures**: Use type hints with `Optional[Any]` and `Tuple` for Blender objects

### File Organization

- `blender/` - Blender-specific scripts (auto-executable)
- `utils/` - MCP client utilities
- `docs/` - Testing and setup guides
- `typings/` - Custom type stubs for bpy and mathutils
- **Pattern**: Scripts reference each other via relative paths from project root

### LDraw Integration

- **Path Convention**: `/Applications/Studio 2.0/ldraw/parts/` (macOS default)
- **Common Parts List**: 70+ curated LEGO parts by popularity in `import_lego_parts.py`
- **Vertical Arrangement**: Parts stacked with calculated spacing for physics simulation
- **Part Naming**: Uses official LDraw part numbers (e.g., "4073", "3023", "3024")

## Complete Workflow & Code-Driven Scene Configuration

### Philosophy: Zero Binary Dependencies

The entire Blender scene is generated through Python scripts - **no .blend files are saved or required**. This ensures:

- **Reproducibility**: Anyone can recreate the exact scene from code
- **Version Control**: All scene changes are trackable through Git
- **Modularity**: Individual components can be developed and tested independently
- **Automation**: Complete CI/CD pipeline possible for scene generation

### Standard Execution Workflow

1. **Scene Reset** (`clear_scene.py`)

   - Removes all mesh objects, lights, cameras
   - Clears all collections except default scene collection
   - Resets physics world and animation data
   - Provides clean slate for scene generation

2. **Geometry Creation** (Various scripts)

   - `create_sorting_bucket.py`: Main collection bucket with hollow interior
   - `create_conveyor_belt.py`: Inclined transport system with friction physics
   - Each script handles its own collection management and object naming

3. **Asset Import** (`import_lego_parts.py`)

   - Imports real LEGO parts from LDraw library
   - Arranges parts vertically for realistic drop physics
   - Assigns physics properties (mass: 2g, friction: 0.9)

4. **Physics & Animation Setup** (`animate_lego_physics.py`)
   - Configures rigid body simulation
   - Sets up realistic collision detection
   - Animates conveyor belt movement through material displacement

### Script Execution Patterns

**Sequential Execution**: Scripts run in specific order through `run_lego_sorter.py`

```python
# Standard pipeline
scripts = [
    "clear_scene.py",
    "create_sorting_bucket.py",
    "create_conveyor_belt.py",
    "import_lego_parts.py",
    "animate_lego_physics.py"
]
```

**Independent Execution**: Each script can run standalone for development/testing

```bash
# Test individual components
python -c "from utils.blender_mcp_client import BlenderMCPClient; client = BlenderMCPClient(); client.execute_script_file('blender/create_conveyor_belt.py')"
```

**MCP Remote Execution**: All scripts execute through MCP bridge for remote Blender control

### Scene Configuration Philosophy

**Declarative Geometry**: Objects defined through code parameters, not manual modeling

- Bucket dimensions, conveyor length/angle, part spacing all configurable
- Boolean operations create complex shapes (hollow bucket via DIFFERENCE modifier)
- Physics properties embedded in object creation functions

**Collection-Based Organization**: Logical grouping prevents object conflicts

- `"bucket"`: Sorting container and related geometry
- `"conveyor_belt"`: Transport system components and supports
- `"lego_parts"`: Imported LEGO pieces with physics
- Each script manages its own collection lifecycle

**Material & Animation Integration**: Visual and physics properties unified

- Conveyor belt materials include animated texture displacement
- LEGO parts receive realistic PBR materials during import
- Animation keyframes set programmatically for belt movement

### Configuration Management

**Parameter Centralization**: Key values configurable at script level

```python
# In create_conveyor_belt.py
CONVEYOR_LENGTH = 1.5      # Belt length in Blender units
CONVEYOR_ANGLE = 0.15      # Incline angle in radians
BELT_FRICTION = 0.8        # Physics friction coefficient
```

**LDraw Path Configuration**: External asset paths centralized

```python
# In import_lego_parts.py
LDRAW_PARTS_PATH = "/Applications/Studio 2.0/ldraw/parts/"
COMMON_PARTS = ["3001", "3003", "3004", ...]  # Popular LEGO parts
```

**Physics Constants**: Realistic LEGO simulation parameters

```python
LEGO_MASS = 0.002         # 2 grams per typical LEGO brick
LEGO_FRICTION = 0.9       # High friction for realistic stacking
GRAVITY_SCALE = 9.81      # Standard Earth gravity
```

## Integration Points

### MCP Communication Protocol

- **Socket-based**: JSON commands over TCP connection
- **Command Structure**: `{"type": "execute_code", "params": {"code": "..."}}`
- **Response Format**: `{"status": "success/error", "result": "...", "message": "..."}`
- **Buffer Size**: 8KB response buffer for large script outputs

### Blender API Usage

- **Operations**: Prefer `bpy.ops` for scene manipulation
- **Object Access**: Always check `bpy.context.active_object` for null
- **Collections**: Use `bpy.data.collections.new()` and link to scene
- **Geometry**: bmesh operations for complex mesh modifications
- **Boolean Operations**: Create hollow objects using DIFFERENCE modifier
- **Physics**: Rigid body simulation with realistic LEGO properties (mass: 2g, friction: 0.9)

### External Dependencies

- **LDraw Library**: Required for LEGO part geometry
- **BlenderMCP Addon**: Must be enabled in Blender
- **fake-bpy-module**: Provides type hints for development
- **Development Tools**: Black, Flake8, MyPy for code quality

## Key Files for Understanding

- `run_lego_sorter.py` - Main orchestration logic and workflow execution
- `utils/blender_mcp_client.py` - MCP communication patterns and remote script execution
- `blender/clear_scene.py` - Scene reset and cleanup procedures
- `blender/create_sorting_bucket.py` - Complex geometry creation with boolean operations
- `blender/create_conveyor_belt.py` - Transport system with physics and animation
- `blender/import_lego_parts.py` - Asset import and physics configuration logic
- `blender/animate_lego_physics.py` - Physics simulation and animation setup
- `README.md` - Complete project context and real-world inspiration

## Testing & Debugging

### Quick Test Methods

1. **Complete Workflow**: Run `python run_lego_sorter.py` for full scene generation
2. **Direct Blender**: Copy script to Blender's script editor and run for immediate testing
3. **MCP Test**: Use `python utils/blender_mcp_client.py` to verify connection
4. **Individual Scripts**: Execute single scripts via MCP client for component testing
5. **Scene Validation**: Use `clear_scene.py` followed by specific script to test in isolation

### Common Issues

- **MCP Connection**: Verify Blender addon is connected before script execution
- **LDraw Path**: Adjust path in `import_lego_parts.py` if parts not found
- **Collection Cleanup**: Run `clear_scene.py` if objects appear in wrong collections
- **Script Order**: Always run `clear_scene.py` first to ensure clean state
- **Physics Setup**: Ensure conveyor and bucket are created before physics animation

## Physics Simulation Context

The project simulates a real sorting machine workflow - parts should fall through tubes, be identified by cameras, and sorted into buckets. Consider physics properties when adding new geometry or modifying existing objects.
