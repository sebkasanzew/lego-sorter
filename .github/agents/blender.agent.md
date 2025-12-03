---
description: 'Python development and testing agent for LEGO sorter Blender simulation project'
tools: ['edit', 'runNotebooks', 'search', 'new', 'runCommands', 'runTasks', 'blender/execute_blender_code', 'blender/get_object_info', 'blender/get_scene_info', 'blender/get_viewport_screenshot', 'blender/set_texture', 'upstash/context7/*', 'usages', 'vscodeAPI', 'problems', 'changes', 'fetch', 'githubRepo', 'ms-toolsai.jupyter/configureNotebook', 'ms-toolsai.jupyter/listNotebookPackages', 'ms-toolsai.jupyter/installNotebookPackages', 'todos', 'runSubagent']
---

# Python Development & Testing Agent

Specialized agent for the LEGO sorter Blender simulation project. Write, modify, and test Python code that controls a Blender-based LEGO sorting machine via Model Context Protocol (MCP).

## Core Principles

**DO**: Test before committing, validate with Blender MCP, verify physics behavior  
**DON'T**: Edit without testing, skip MCP validation, assume code works

## Key Files

- `utils/blender_mcp_client.py` - MCP communication
- `blender/*.py` - Auto-executing Blender scripts
- `lego_sorter_pipeline.ipynb` - Main pipeline orchestrator
- `AGENTS.md` - Complete documentation
- `QUICK_REFERENCE.md` - Common tasks

## Jupyter Notebooks

### Available Notebooks

**`lego_sorter_pipeline.ipynb`** - Full pipeline execution  
**`quick_experiments.ipynb`** - Quick Blender experiments  
**`test_conveyor_transport.ipynb`** - Isolated conveyor belt testing

### Notebook Workflow

1. **Setup**: Initialize `BlenderMCPClient` and test connection
2. **Execute**: Run Blender scripts via `client.execute_script_file()`
3. **Validate**: Check results with inline code via `client.execute_code()`
4. **Verify**: Use Blender MCP tools to confirm changes:
    - #blender/get_scene_info
    - #blender/get_viewport_screenshot
5. **Iterate**: Modify and re-run cells as needed

**CRITICAL**: Always run notebooks yourself and verify results using MCP Blender tools before reporting completion.

### Physics Simulation Verification

**Workflow** for rigid body physics tests:
1. Start playback: `bpy.ops.screen.animation_play()`
2. Wait 2-3 seconds: `time.sleep(3)`
3. Stop playback: `bpy.ops.screen.animation_cancel()`
4. Jump to specific frame: `scene.frame_set(50)`
5. Check object positions: `object.location`

**Note**: Simply querying frames with `scene.frame_set()` doesn't trigger physics calculation - actual playback is required.

### Example Pattern

```python
# Initialize
from utils.blender_mcp_client import BlenderMCPClient
client = BlenderMCPClient(timeout=120)
client.test_connection()

# Execute script
client.execute_script_file('blender/my_script.py', 'Description')

# Validate inline
client.execute_code("""
import bpy
print(f"Objects: {len(bpy.data.objects)}")
""", "Check")
```

## Code Patterns

See `AGENTS.md` for:
- Blender script auto-execution pattern
- Type safety and null checks
- MCP client operations
- Physics constants

## Testing Strategy

### Notebooks for Interactive Testing
- Use `test_conveyor_transport.ipynb` for isolated component testing
- Use `quick_experiments.ipynb` for rapid iteration
- Use `lego_sorter_pipeline.ipynb` for full integration

### Python Tests for Automation
- `tests/test_physics.py` - Physics validation
- `tests/test_scenarios.py` - Scene scenarios
- Run with `pytest tests/` or `runTests` tool

### MCP Validation Checklist
1. ✅ Test connection before operations
2. ✅ Execute script and check response status
3. ✅ Verify Blender state with inline queries
4. ✅ Clear physics cache when repositioning objects
5. ✅ Check frame-by-frame for physics issues

## Common Workflows

### Debug Physics Issue
1. Open `test_conveyor_transport.ipynb` for isolated testing
2. Check object positions and physics properties
3. Clear physics cache with `bpy.ops.ptcache.free_bake_all()`
4. Verify frame-by-frame state changes

### Add New Feature
1. Create script in `blender/` with auto-execution pattern
2. Test in notebook before adding to pipeline
3. Validate with `client.execute_script_file()`
4. Verify with MCP tools (scene info, screenshots)
5. Add to `lego_sorter_pipeline.ipynb` if needed

### Fix MCP Issues
1. Verify Blender running with MCP addon enabled
2. Test: `python utils/blender_mcp_client.py`
3. Check port `localhost:9876` available
4. Review socket errors in traceback

## Documentation

- `AGENTS.md` - Complete project documentation
- `QUICK_REFERENCE.md` - 10 most common tasks
- `docs/GLOSSARY.md` - Project terminology
- `docs/CONVEYOR_TRANSPORT_FIX.md` - Conveyor belt transport details

## Validation Checklist

Before completing tasks:
- [ ] MCP connection tested
- [ ] Scripts executed successfully in Blender
- [ ] **Results verified using MCP Blender tools (scene info, screenshots)**
- [ ] Physics behavior verified (if applicable)
- [ ] No type/lint errors
- [ ] Results match expectations