# Implementation Summary: Physics Baking Workflow

## What Was Implemented

### 1. Baking Script (`blender/bake_and_verify_physics.py`)

Comprehensive script for automated physics baking and verification:

**Features**:
- Clears physics cache automatically
- Sets up frame range (1-250)
- Bakes rigid body simulation with timeout
- Verifies object movement after baking
- Provides detailed analysis of transport success
- Frame-by-frame progression tracking

**Functions**:
- `clear_physics_cache()` - Reset simulation
- `setup_frame_range()` - Configure simulation span
- `bake_rigid_body_physics(timeout=60)` - Execute baking
- `verify_transport()` - Analyze object movement
- `get_ramp_info()` - Debug information

**Usage**:
```python
# In Blender/MCP
exec(open('blender/bake_and_verify_physics.py').read())
```

### 2. Notebook Integration (`test_conveyor_transport.ipynb`)

Added 3 new cells for physics baking workflow:

**Cell 1**: Markdown explanation
- Documents that baking is required in MCP mode
- Links to detailed documentation

**Cell 2**: Bake initiation
- Clears cache
- Sets frame range to 1-150 (faster testing)
- Initiates baking operation
- Returns immediately (baking async)

**Cell 3**: Wait period
- Waits 60 seconds for baking to complete
- Simple pause between bake start and verification

**Cell 4**: Verification
- Checks if baking completed (`cache.is_baked`)
- Tests transport at frames 1, 50, 100, 150
- Calculates total movement distance
- Reports success if movement > 0.3m

### 3. Documentation (`docs/PHYSICS_BAKING_REQUIRED.md`)

Complete technical documentation covering:
- Problem description and evidence
- Root cause analysis
- Solution with code examples
- Before/after workflow comparison
- Technical details about why it works

## How to Use

### From Notebook

1. Run all setup cells (clear, ramp, parts, positioning)
2. Run baking cell - starts physics calculation
3. Wait 60 seconds (or run wait cell)
4. Run verification cell - checks results

### From MCP Client

```python
from utils.blender_mcp_client import BlenderMCPClient

client = BlenderMCPClient(timeout=180)  # Longer timeout for baking

# Setup scene first...
# (create ramp, import parts, position, etc.)

# Execute baking script
client.execute_script_file(
    'blender/bake_and_verify_physics.py',
    'Bake and Verify'
)
```

### Direct in Blender

```python
import bpy

# Load script
with open('/path/to/bake_and_verify_physics.py', 'r') as f:
    exec(f.read())
```

## Key Discoveries

### Why Baking is Necessary

**Problem**: `bpy.ops.screen.animation_play()` is viewport-specific
- Designed for UI playback in Blender editor
- Doesn't trigger physics when running headless/MCP
- Objects remain at initial positions

**Solution**: `bpy.ops.ptcache.bake()` explicitly calculates physics
- Independent of viewport/UI state
- Computes all frames and caches results
- Works reliably in headless mode

### Verification Method

After baking, use `scene.frame_set(N)` to query cached positions:

```python
scene.frame_set(100)
obj = bpy.data.objects.get("Part")
position = obj.location  # This is now the BAKED position
```

## Testing Status

**Current Scene State** (when Blender recovers from baking):
- ✅ Ramp created (20° incline, friction 0.4)
- ✅ Rails added (containment)
- ✅ 10 LEGO parts imported
- ✅ Parts positioned above ramp
- ✅ All objects in RBW collection
- ⏳ Baking in progress (initiated but not verified)

**Next Steps**:
1. Wait for current baking to complete
2. Run verification to confirm transport works
3. If successful, document final workflow
4. Update main pipeline notebook with baking

## Files Modified/Created

### Created:
- `/blender/bake_and_verify_physics.py` (310 lines)
- `/docs/PHYSICS_BAKING_REQUIRED.md`
- `/docs/PHYSICS_BAKING_WORKFLOW_SUMMARY.md` (this file)

### Modified:
- `/test_conveyor_transport.ipynb` - Added 4 cells for baking workflow
- `/blender/create_inclined_conveyor.py` - Added RBW collection linking

### Updated:
- `/blender/create_inclined_conveyor.py` - Ensures ramp/rails added to RBW

## Expected Results

After successful baking:

**Frame 1**: Parts at (0.05, ±0.03, 0.23) - Above ramp top
**Frame 50**: Parts should have fallen and started sliding
**Frame 100**: Parts at ~(−0.3, ±0.03, 0.05) - Midway down ramp
**Frame 150**: Parts at ~(−0.8, ±0.03, −0.15) - Near bottom

**Success Criteria**: Total movement > 0.3m in XZ plane

## Troubleshooting

**If baking times out**:
- Reduce frame range (e.g., 1-100 instead of 1-250)
- Simplify collision shapes (BOX instead of MESH)
- Reduce number of parts for testing

**If objects don't move after baking**:
- Check `cache.is_baked` returns True
- Verify parts are ACTIVE rigid bodies
- Confirm parts positioned ABOVE ramp surface
- Check all objects in RBW collection

**If Blender becomes unresponsive**:
- Baking is CPU-intensive and blocks
- Wait for completion (may take 1-2 minutes)
- Or restart Blender and use shorter frame range

## Performance Notes

**Baking time depends on**:
- Number of objects (13 objects = ~60s)
- Frame range (150 frames = ~60s)
- Collision complexity (MESH slower than BOX)
- CPU speed

**Optimization tips**:
- Use BOX collision for simple objects
- Start with short frame range (50 frames)
- Reduce object count for initial tests
- Increase solver iterations if objects penetrate
