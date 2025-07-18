# Tests Directory

This directory contains test scripts for the LEGO Sorter project.

## Available Tests

### `test_physics.py`

Comprehensive test suite for the physics simulation system.

**Features:**

- Tests MCP connection to Blender
- Verifies physics world creation
- Tests rigid body setup
- Checks LEGO parts detection
- Validates sorting bucket creation

**Usage:**

```bash
# From project root
python tests/test_physics.py

# Or from tests directory
cd tests
python test_physics.py
```

## Running Tests

All tests require:

1. Blender running with BlenderMCP addon connected
2. MCP server running on `localhost:9876`
3. Python environment with required dependencies

## Test Structure

Tests are organized into logical groups:

- **Connection Tests**: Verify MCP communication
- **Physics Tests**: Test rigid body simulation setup
- **Scene Tests**: Validate scene objects and collections
- **Integration Tests**: End-to-end workflow testing
