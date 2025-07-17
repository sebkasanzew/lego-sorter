# LEGO Sorter - Blender Simulation

A Blender-based simulation for sorting LEGO parts using the Model Context Protocol (MCP) server.

## Project Structure

```
lego-sorter/
├── blender/                    # Blender-specific scripts
│   ├── clear_scene.py             # Clears the Blender scene
│   ├── create_sorting_bucket.py   # Creates a sorting bucket in Blender
│   ├── import_lego_parts.py       # Imports LEGO parts from LDraw files
│   └── lego_parts.blend           # Blender scene file
├── utils/                      # Utility scripts
│   └── blender_mcp_client.py      # MCP client for Blender communication
├── docs/                       # Documentation
│   └── TESTING_GUIDE.md           # Testing guide
├── run_lego_sorter.py             # Main script to run the simulation
└── README.md                   # This file
```

## Scripts Overview

### Main Scripts

- **`run_lego_sorter.py`** - Main entry point to run the complete LEGO sorter simulation
- **`utils/blender_mcp_client.py`** - MCP client utility for communicating with Blender

### Blender Scripts

- **`blender/clear_scene.py`** - Clears the Blender scene (removes all objects and collections)
- **`blender/create_sorting_bucket.py`** - Creates a hollow bucket for sorting LEGO parts
- **`blender/import_lego_parts.py`** - Imports common LEGO parts from LDraw files

### Legacy Files (for reference)

- **`create_bucket.py`** - Original bucket creation script
- **`import_lego_parts.py`** - Original LEGO parts import script
- **`test_blender_mcp.py`** - Original MCP test script

## Requirements

1. **Blender** with BlenderMCP addon installed and enabled
2. **LDraw Library** (typically installed with LEGO CAD software)
3. **Python 3.x** for running the scripts

## Setup Instructions

### 1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 2. **Install Blender MCP Server**:

- Open Blender
- Go to 3D View sidebar (press N)
- Find 'BlenderMCP' tab
- Click 'Connect to Claude'

### 3. **Verify LDraw Path**:

- Ensure LDraw library is installed (usually at `/Applications/Studio 2.0/ldraw/parts/`)
- Modify the path in `blender/import_lego_parts.py` if needed

### 4. **VSCode Setup (Optional)**:

- The project includes VSCode settings to handle Blender imports
- Install the Python extension for better IntelliSense
- The `fake-bpy-module-latest` package provides type hints for Blender APIs

## Usage

### Quick Start

```bash
python run_lego_sorter.py
```

````

### Individual Scripts

```bash
# Test MCP connection
python utils/blender_mcp_client.py

# Or run individual Blender scripts (requires MCP server)
python -c "from utils.blender_mcp_client import BlenderMCPClient; client = BlenderMCPClient(); client.execute_script_file('blender/create_sorting_bucket.py')"
````

## Features

- **Scene Clearing**: Automatically clears the Blender scene before starting
- **Sorting Bucket Creation**: Creates a hollow cylindrical bucket with a base
- **LEGO Parts Import**: Imports 100+ common LEGO parts from LDraw files
- **Automatic Arrangement**: Parts are arranged vertically with proper spacing
- **Collection Management**: Objects are organized into collections for easy management
- **MCP Integration**: All scripts can be executed remotely via MCP server

## File Descriptions

### `run_lego_sorter.py`

Main entry point that orchestrates the entire simulation:

- Tests MCP connection
- Clears the Blender scene
- Creates sorting bucket
- Imports LEGO parts
- Provides user feedback

### `utils/blender_mcp_client.py`

Utility class for MCP communication:

- Connection testing
- Code execution
- Script file execution
- Error handling

### `blender/clear_scene.py`

Scene clearing utility:

- Removes all objects from the scene
- Cleans up empty collections
- Provides feedback on clearing operations
- Can be run independently or as part of the workflow

### `blender/create_sorting_bucket.py`

Creates a sorting bucket:

- Hollow cylinder with base
- Boolean operations for hollow interior
- Collection management
- Proper naming conventions

### `blender/import_lego_parts.py`

Imports LEGO parts from LDraw:

- Filters for common parts
- Vertical arrangement
- Bounding box calculations
- Progress feedback

## Troubleshooting

1. **MCP Connection Issues**:

   - Ensure Blender is running
   - Check BlenderMCP addon is enabled
   - Verify MCP server is connected

2. **LDraw Import Issues**:

   - Verify LDraw library path
   - Check LDraw importer addon is enabled
   - Ensure .dat files exist in the specified directory

3. **Script Execution Issues**:
   - Check Python path configuration
   - Verify all required files are present
   - Review error messages for specific issues

## Contributing

When adding new scripts:

1. Place Blender-specific scripts in `blender/` directory
2. Add utility scripts to `utils/` directory
3. Update this README with new functionality
4. Follow the existing naming conventions
