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
- **Asset Import**: `import_lego_parts.py` - LDraw file import with vertical arrangement
- **Physics Animation**: `animate_lego_physics.py` - Realistic gravity simulation and collision detection
- **Pattern**: Scripts use `main()` function and auto-execute when imported (no `if __name__ == "__main__"` checks)

### 3. Workflow Orchestration (`run_lego_sorter.py`)

- **Standard Pipeline**: clear → create bucket → import parts → setup physics
- **Error Handling**: Checks file existence before execution
- **User Feedback**: Emoji-based progress indicators (🧱, 🔍, 🎯, 1️⃣, 2️⃣, 3️⃣, 🎉)
- **Path Management**: Uses `sys.path.insert()` to add utils directory dynamically

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

- `run_lego_sorter.py` - Main orchestration logic
- `utils/blender_mcp_client.py` - MCP communication patterns
- `blender/create_sorting_bucket.py` - Complex geometry creation with boolean operations
- `blender/import_lego_parts.py` - Asset import and arrangement logic
- `README.md` - Complete project context and real-world inspiration

## Testing & Debugging

### Quick Test Methods

1. **Direct Blender**: Copy script to Blender's script editor and run
2. **MCP Test**: Use `python utils/blender_mcp_client.py` to verify connection
3. **Individual Scripts**: Execute single scripts via MCP client

### Common Issues

- **MCP Connection**: Verify Blender addon is connected before script execution
- **LDraw Path**: Adjust path in `import_lego_parts.py` if parts not found
- **Collection Cleanup**: Run `clear_scene.py` if objects appear in wrong collections

## Physics Simulation Context

The project simulates a real sorting machine workflow - parts should fall through tubes, be identified by cameras, and sorted into buckets. Consider physics properties when adding new geometry or modifying existing objects.
