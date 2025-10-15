# Common Development Tasks

> **Quick Start**: For the 10 most common operations, see [QUICK_REFERENCE.md](../QUICK_REFERENCE.md)  
> **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions  
> **Terminology**: See [GLOSSARY.md](GLOSSARY.md) for definitions

Quick reference guide for frequent operations in the LEGO Sorter project.

## Table of Contents

- [Scene Management](#scene-management)
- [Adding New Components](#adding-new-components)
- [Debugging Physics](#debugging-physics)
- [Modifying Materials](#modifying-materials)
- [Testing Without Full Pipeline](#testing-without-full-pipeline)
- [Working with LDraw Parts](#working-with-ldraw-parts)
- [MCP Connection Issues](#mcp-connection-issues)
- [Rendering and Visualization](#rendering-and-visualization)

---

## Scene Management

### Clear and Rebuild Scene

```bash
# Full pipeline (recommended)
python run_lego_sorter.py

# With debug mode (faster timeouts)
BLENDER_MCP_DEBUG=1 python run_lego_sorter.py

# Skip conveyor belt
SKIP_CONVEYOR=1 python run_lego_sorter.py
```

### Run Individual Script via MCP

```python
from utils.blender_mcp_client import BlenderMCPClient

client = BlenderMCPClient()
client.execute_script_file('blender/clear_scene.py', 'Clear Scene')
```

### Test MCP Connection

```bash
python utils/blender_mcp_client.py
```

Expected output: `✅ Blender MCP server is running on localhost:9876`

---

## Adding New Components

### 1. Create New Blender Script

**Template**: `blender/create_my_component.py`

```python
import bpy
from typing import Optional
from bpy.types import Object


def clear_existing_component() -> None:
    """Remove any existing component objects and collection."""
    collection = bpy.data.collections.get("my_component")
    if collection:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
    print("✓ Cleared existing component")


def create_my_component() -> Optional[Object]:
    """Create the component geometry."""
    # Create collection
    collection = bpy.data.collections.new("my_component")
    bpy.context.scene.collection.children.link(collection)
    
    # Create geometry
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    if obj is None:
        print("❌ Failed to create component")
        return None
    
    obj.name = "MyComponent"
    
    # Move to collection
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)
    
    # Add physics if needed
    if obj.rigid_body is None:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.object_add()
        obj.rigid_body.type = 'PASSIVE'
        obj.rigid_body.mass = 10.0
    
    print(f"✓ Created component: {obj.name}")
    return obj


def main():
    """Main function to create component."""
    print("Creating my component...")
    clear_existing_component()
    obj = create_my_component()
    if obj:
        print("✅ Component creation complete")
    else:
        print("❌ Component creation failed")


# Auto-execute when imported via MCP
main()
```

### 2. Add to Pipeline

**Edit**: `run_lego_sorter.py`

```python
# Add after step 2 or 3
print("\n4️⃣ Creating my component...")
my_component_script = os.path.join(blender_dir, "create_my_component.py")
if os.path.exists(my_component_script):
    if not run_with_retries(
        client,
        my_component_script,
        "My Component",
        attempts=(1 if is_debug else 2),
        timeout=default_timeout,
    ):
        print("❌ Component creation failed")
        return
```

### 3. Test Component Alone

```bash
# Create test script
cat > test_component.py << 'EOF'
from utils.blender_mcp_client import BlenderMCPClient
import os

client = BlenderMCPClient()
if client.test_connection():
    # Clear first
    client.execute_script_file('blender/clear_scene.py', 'Clear')
    # Create component
    client.execute_script_file('blender/create_my_component.py', 'My Component')
EOF

python test_component.py
```

---

## Debugging Physics

### Inspect Object State at Specific Frame

**Create**: `blender/debug_frame.py`

```python
import bpy

frame = 20  # Frame to inspect
bpy.context.scene.frame_set(frame)

print(f"\n=== Scene State at Frame {frame} ===")

# Inspect all LEGO parts
parts_col = bpy.data.collections.get("lego_parts")
if parts_col:
    for obj in parts_col.objects:
        print(f"\nObject: {obj.name}")
        print(f"  Location: {obj.location}")
        print(f"  Rotation: {obj.rotation_euler}")
        if obj.rigid_body:
            # Note: Can't access velocity/angular_velocity in cached simulation
            print(f"  Mass: {obj.rigid_body.mass}")
            print(f"  Type: {obj.rigid_body.type}")

# Check conveyor
conveyor = bpy.data.objects.get("Conveyor_Belt")
if conveyor:
    print(f"\nConveyor: {conveyor.location}")
```

**Run**: `client.execute_script_file('blender/debug_frame.py', 'Debug')`

### Common Physics Issues

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| Parts fall through floor | Missing rigidbody on floor | Set floor to PASSIVE rigidbody |
| Parts slide backward on conveyor | Friction too low | Increase `BELT_FRICTION` to 0.8-0.9 |
| Parts don't move at all | Static rigidbody type | Set to ACTIVE type |
| Simulation explodes | Mass too high or collision margin too small | Reduce mass or increase margin |
| Parts jitter/vibrate | Substeps too low | Increase substeps in rigidbody world |

### Enable Debug Logging

```python
# Add to top of your Blender script
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Modifying Materials

### Pattern: Ensure Material Exists

```python
def ensure_material(
    name: str,
    rgba: tuple[float, float, float, float],
    roughness: float = 0.6,
    metallic: float = 0.05,
) -> Any:
    """Get or create a Principled BSDF material."""
    mat = bpy.data.materials.get(name)
    
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        out = nodes.new(type="ShaderNodeOutputMaterial")
        bsdf.location = (-200, 0)
        out.location = (0, 0)
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    
    # Update properties
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    
    return mat
```

### Apply Material to Object

```python
def assign_material(obj: Any, mat: Any) -> None:
    """Assign material to object."""
    if not obj or getattr(obj, "data", None) is None:
        return
    
    mats = obj.data.materials
    if mats and len(mats) > 0:
        mats[0] = mat
    else:
        mats.append(mat)
```

### Common Material Colors

```python
# Red plastic LEGO
mat_red = ensure_material("LEGORed", (0.8, 0.1, 0.1, 1.0), roughness=0.4)

# Blue plastic LEGO
mat_blue = ensure_material("LEGOBlue", (0.1, 0.3, 0.8, 1.0), roughness=0.4)

# Gray conveyor belt (rubber)
mat_belt = ensure_material("BeltRubber", (0.2, 0.2, 0.2, 1.0), roughness=0.8)

# Metallic support (aluminum)
mat_metal = ensure_material("Aluminum", (0.8, 0.8, 0.8, 1.0), roughness=0.3, metallic=0.9)
```

---

## Testing Without Full Pipeline

### Test Just Bucket

```bash
cat > test_bucket_only.py << 'EOF'
from utils.blender_mcp_client import BlenderMCPClient
import os

client = BlenderMCPClient()
if client.test_connection():
    client.execute_script_file('blender/clear_scene.py', 'Clear')
    client.execute_script_file('blender/create_sorting_bucket.py', 'Bucket')
    print("✅ Check Blender for bucket")
EOF

python test_bucket_only.py
```

### Test Bucket + Conveyor

```bash
SKIP_CONVEYOR=0 python run_lego_sorter.py
# Then Ctrl+C after conveyor creation
```

### Test Single LEGO Part Import

**Edit**: `blender/import_lego_parts.py`

```python
# Temporarily change COMMON_PARTS to just one part
COMMON_PARTS = ["3001"]  # Just 2x4 brick

# Run normally
python run_lego_sorter.py
```

### Skip Slow Operations

```bash
# Skip LEGO import (takes 30-60s)
# Edit run_lego_sorter.py to comment out step 3

# Skip rendering (takes 10-30s per view)
# Edit run_lego_sorter.py to comment out step 6
```

---

## Working with LDraw Parts

### Find LDraw Installation Path

```bash
# macOS (BrickLink Studio)
ls /Applications/Studio\ 2.0/ldraw/parts/

# macOS (LDraw official)
ls ~/Library/ldraw/parts/

# Linux
ls ~/.ldraw/parts/

# Windows
dir "C:\Users\YourName\Documents\LDraw\parts"
```

### Change LDraw Path

**Edit**: `blender/import_lego_parts.py`

```python
# Line ~20
LDRAW_PARTS_PATH = "/path/to/your/ldraw/parts/"
```

### Find Part Numbers

1. Go to [Rebrickable](https://rebrickable.com/parts/)
2. Search for part (e.g., "2x4 brick")
3. Note the part number (e.g., "3001")
4. Add to `COMMON_PARTS` list

### Test If Part Exists

```bash
# Check if part file exists
ls "/Applications/Studio 2.0/ldraw/parts/3001.dat"

# If missing, part won't import
```

### Common Part Numbers

```python
COMMON_PARTS = [
    "3001",   # 2x4 brick
    "3003",   # 2x2 brick  
    "3004",   # 1x2 brick
    "3005",   # 1x1 brick
    "3010",   # 1x4 brick
    "3020",   # 2x4 plate
    "3023",   # 1x2 plate
    "3024",   # 1x1 plate
    "3622",   # 1x3 brick
    "3710",   # 1x4 plate
]
```

---

## MCP Connection Issues

### Symptom: "Cannot connect to Blender MCP server"

**Checklist**:

1. **Is Blender running?**
   ```bash
   ps aux | grep -i blender
   ```

2. **Is MCP addon enabled?**
   - Open Blender → Edit → Preferences → Add-ons
   - Search "MCP"
   - Ensure checkbox is checked

3. **Is MCP server started?**
   - Press `N` in 3D viewport
   - Click "BlenderMCP" tab
   - Click "Connect to Claude"
   - Status should show "Connected"

4. **Is port 9876 available?**
   ```bash
   lsof -i :9876
   ```
   Should show Blender process

5. **Firewall blocking?**
   - Check macOS firewall settings
   - Allow Blender to accept incoming connections

### Symptom: "Connection timeout"

**Causes**:
- Operation taking longer than timeout value
- Blender unresponsive (busy with heavy operation)

**Solutions**:
```bash
# Increase timeout
BLENDER_MCP_TIMEOUT=600 python run_lego_sorter.py

# Or edit script
client = BlenderMCPClient(timeout=600)  # 10 minutes
```

### Symptom: Scripts execute but Blender shows nothing

**Likely cause**: Wrong scene context

**Fix**: Add explicit scene context
```python
# At top of Blender script
scene = bpy.context.scene
view_layer = bpy.context.view_layer
```

---

## Rendering and Visualization

### Render Single Frame

**Create**: `blender/render_current_frame.py`

```python
import bpy

scene = bpy.context.scene
scene.render.filepath = "/tmp/test_render.png"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
print(f"✓ Rendered to {scene.render.filepath}")
```

### Change Camera Position

```python
camera = bpy.data.objects.get("SorterCam")
if camera:
    camera.location = (2.0, -3.0, 2.0)  # Move camera
    camera.rotation_euler = (1.1, 0, 0.785)  # Point at origin
```

### Render from Multiple Angles

Already implemented in `render_snapshot.py`:

```bash
python run_lego_sorter.py
# Check renders/ directory for outputs
ls renders/frame_01/
```

**Views generated**:
- Top, Bottom, Front, Back, Left, Right (orthographic)
- 4 isometric corners (NE, NW, SE, SW)

### Quick Preview in Blender

1. **Set frame**: Timeline → Frame 20
2. **Viewport shading**: Press `Z` → Material Preview
3. **Render preview**: Press `F12`

---

## Tips for AI Assistants

### When Suggesting Code Changes

✅ **Good**: Provide complete code blocks with context
```python
# In create_conveyor_belt.py, around line 95
def create_conveyor_belt() -> Optional[Object]:
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0.6, 0, 0.18),  # <-- Changed from (0.5, 0, 0.15)
    )
```

❌ **Bad**: Vague instructions
```
Change the conveyor location to be higher
```

### When Debugging Physics

✅ **Good**: Request specific frame inspection
```
At frame 20, check the Z position and velocity of parts in lego_parts collection
```

❌ **Bad**: Generic descriptions
```
The physics looks weird
```

### When Asking for Features

✅ **Good**: Provide context and constraints
```
Add a camera at (1.5, 0, 0.5) pointing at the conveyor belt, with a 50mm lens.
The camera should be in a collection called "cameras" and named "ConveyorCam".
```

❌ **Bad**: Ambiguous requests
```
Add a camera somewhere
```

---

## Quick Reference: File Locations

| Purpose | Location |
|---------|----------|
| Main runner | `run_lego_sorter.py` |
| MCP client | `utils/blender_mcp_client.py` |
| Scene clearing | `blender/clear_scene.py` |
| Bucket creation | `blender/create_sorting_bucket.py` |
| Conveyor system | `blender/create_conveyor_belt.py` |
| LEGO import | `blender/import_lego_parts.py` |
| Physics setup | `blender/animate_lego_physics.py` |
| Lighting | `blender/setup_lighting.py` |
| Rendering | `blender/render_snapshot.py` |
| Render outputs | `renders/frame_XX/*.png` |

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BLENDER_MCP_DEBUG` | `0` | Enable debug mode (shorter timeouts) |
| `BLENDER_MCP_TIMEOUT` | `300` | Default timeout in seconds |
| `SKIP_CONVEYOR` | `0` | Skip conveyor belt creation |

---

## Next Steps

- See `ARCHITECTURE.md` for system design details
- See `GLOSSARY.md` for terminology
- See `CHANGELOG.md` for recent changes
- See `tests/test_scenarios.py` for validation patterns
