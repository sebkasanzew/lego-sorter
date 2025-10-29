# Quick Reference - Most Common Tasks

## 1. Run Complete Pipeline

```bash
jupyter notebook
# Open lego_sorter_pipeline.ipynb
# Run cells sequentially (Shift+Enter)
```

---

## 2. Test MCP Connection

```bash
python utils/blender_mcp_client.py
```

Expected: `✅ Blender MCP server is running on localhost:9876`

**If fails**: Blender → Press `N` → BlenderMCP tab → "Connect to MCP server"

---

## 3. Quick Experiment

```bash
jupyter notebook
# Open quick_experiments.ipynb
# Run setup cell, then experiment cells
```

---

## 4. Custom Blender Code

In notebook cell:
```python
client.execute_code("""
import bpy
print(f"Objects: {len(bpy.data.objects)}")
""", "Description")
```

---

## 5. Check Scene State

In notebook:
```python
client.execute_code("""
import bpy
for col in bpy.data.collections:
    print(f"{col.name}: {len(col.objects)} objects")
""", "Scene Info")
```

---

## 6. Clear Scene

In notebook:
```python
client.execute_script_file('blender/clear_scene.py', 'Clear')
```

---

## 7. Create Specific Component

In notebook:
```python
client.execute_script_file('blender/create_sorting_bucket.py', 'Bucket')
client.execute_script_file('blender/create_conveyor_belt.py', 'Conveyor')
```

---

## 8. Import LEGO Parts

In notebook (takes 5-10 minutes):
```python
client.execute_script_file(
    'blender/import_lego_parts.py',
    'Import Parts',
    timeout=600
)
```

---

## 9. Setup Physics

In notebook:
```python
client.execute_script_file('blender/animate_lego_physics.py', 'Physics')
```

---

## 10. Validate Scene

In notebook:
```python
client.execute_script_file('utils/validate_scene.py', 'Validate')
```

---

## Troubleshooting

**MCP timeout**: `client = BlenderMCPClient(timeout=600)`  
**Connection refused**: Restart Blender MCP addon  
**Import errors**: Check LDraw path in `blender/import_lego_parts.py`  
**Physics debugging**: Run frame-specific checks in notebook

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
