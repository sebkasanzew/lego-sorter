# Quick Reference - Most Common Tasks

**For detailed examples and edge cases, see [COMMON_TASKS.md](docs/COMMON_TASKS.md)**

---

## 1. Run Complete Pipeline

```bash
# Standard execution
python run_lego_sorter.py

# With debug mode (faster timeouts, more logging)
BLENDER_MCP_DEBUG=1 python run_lego_sorter.py
```

---

## 2. Test MCP Connection

```bash
python utils/blender_mcp_client.py
```

Expected: `✅ Blender MCP server is running on localhost:9876`

**If it fails**: Open Blender → Press `N` → BlenderMCP tab → "Connect to Claude"

---

## 3. Clear Scene and Rebuild

```python
from utils.blender_mcp_client import BlenderMCPClient

client = BlenderMCPClient()
client.execute_script_file('blender/clear_scene.py', 'Clear Scene')
client.execute_script_file('blender/create_sorting_bucket.py', 'Create Bucket')
```

---

## 4. Run Single Script

```python
from utils.blender_mcp_client import BlenderMCPClient

client = BlenderMCPClient()
client.execute_script_file('blender/SCRIPT_NAME.py', 'Description')
```

---

## 5. Validate Scene After Changes

```python
from utils.blender_mcp_client import BlenderMCPClient

client = BlenderMCPClient()
client.execute_script_file('utils/validate_scene.py', 'Validate Scene')
```

---

## 6. Debug Physics at Specific Frame

```python
import bpy

frame_number = 20
bpy.context.scene.frame_set(frame_number)

# Inspect LEGO parts
parts_col = bpy.data.collections.get("lego_parts")
if parts_col:
    for obj in parts_col.objects:
        print(f"{obj.name}: {obj.location}")
```

**Run via MCP**: Save as `blender/debug_frame.py` and execute

---

## 7. Add Visual Debug Marker

```python
from utils.blender_debug import add_debug_marker

# Add red marker at position
add_debug_marker((0, 0, 1), color=(1, 0, 0, 1), name="Debug_Point")
```

---

## 8. Check What Parts Are Imported

```bash
# List all parts in lego_parts collection
python -c "
from utils.blender_mcp_client import BlenderMCPClient
code = '''
import bpy
col = bpy.data.collections.get(\"lego_parts\")
if col:
    print(f\"Parts: {len(col.objects)}\")
    for obj in col.objects[:5]:
        print(f\"  - {obj.name}\")
'''
client = BlenderMCPClient()
client.execute_code(code, 'List Parts')
"
```

---

## 9. Modify Physics Properties

```python
import bpy

# Get object
obj = bpy.data.objects.get("Part_3001")
if obj and obj.rigid_body:
    obj.rigid_body.mass = 0.005  # 5 grams
    obj.rigid_body.friction = 0.95
    print(f"Updated {obj.name} physics")
```

---

## 10. Render Current Frame

```python
from utils.blender_mcp_client import BlenderMCPClient

client = BlenderMCPClient()
client.execute_script_file('blender/render_snapshot.py', 'Render', timeout=300)
```

Output: `renders/frame_XX/` directory with 10 orthographic views

---

## Common File Locations

| Purpose | File Path |
|---------|-----------|
| Scene clearing | `blender/clear_scene.py` |
| Bucket creation | `blender/create_sorting_bucket.py` |
| Conveyor belt | `blender/create_conveyor_belt.py` |
| LEGO import | `blender/import_lego_parts.py` |
| Physics setup | `blender/animate_lego_physics.py` |
| Lighting | `blender/setup_lighting.py` |
| Rendering | `blender/render_snapshot.py` |
| Validation | `utils/validate_scene.py` |
| Debug helpers | `utils/blender_debug.py` |

---

## Environment Variables

| Variable | Purpose | Values |
|----------|---------|--------|
| `BLENDER_MCP_DEBUG` | Enable debug mode | `1` (on) or unset (off) |
| `SKIP_CONVEYOR` | Skip conveyor creation | `1` (skip) or unset (create) |

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| MCP not connecting | Restart Blender, reconnect in BlenderMCP tab |
| Scripts timeout | Set `BLENDER_MCP_DEBUG=1` or increase timeout in code |
| Physics desync | Re-run from `clear_scene.py` |
| Parts fall through floor | Check rigidbody types (floor should be PASSIVE) |
| Import fails | Verify LDraw path in `import_lego_parts.py` |

---

**For More Details**:
- Full task examples: [docs/COMMON_TASKS.md](docs/COMMON_TASKS.md)
- Architecture understanding: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Terminology: [docs/GLOSSARY.md](docs/GLOSSARY.md)
- AI agent instructions: [AGENTS.md](AGENTS.md)
