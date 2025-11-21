# Physics Baking Required for MCP Mode

## Problem Discovered

When running Blender physics simulations via MCP (Model Context Protocol) in headless/background mode, **`bpy.ops.screen.animation_play()` does NOT trigger physics calculation**.

### Evidence

1. Created scene with:
   - Inclined ramp (20° angle, passive rigid body, friction 0.4)
   - 10 LEGO parts (active rigid bodies, mass 0.002kg, friction 0.6)
   - All objects properly added to Rigid Body World collection
   - Gravity enabled (-9.81 Z)

2. Used `animation_play()` → `time.sleep()` → `animation_cancel()` workflow
   
3. Result: **Objects don't move AT ALL** - even simple cubes positioned above ramp don't fall

4. Verification:
   - Rigid body world: ✓ Enabled
   - Objects in RBW: ✓ 13 objects (ramp + rails + parts)
   - Gravity: ✓ (0, 0, -9.81)
   - Collision shapes: ✓ Configured
   - Mass/friction: ✓ Set correctly

### Root Cause

The `bpy.ops.screen.animation_play()` operator is viewport-specific and doesn't trigger rigid body physics calculation when Blender runs in MCP/headless mode. Physics simulation requires **explicit baking**.

## Solution

### Option 1: Manual Baking (Reliable)

```python
import bpy

scene = bpy.context.scene

# Clear existing cache
bpy.ops.ptcache.free_bake_all()

# Set frame range
scene.frame_start = 1
scene.frame_end = 250

# Bake rigid body simulation
scene.frame_set(1)
override = bpy.context.copy()
override['point_cache'] = scene.rigidbody_world.point_cache
bpy.ops.ptcache.bake(override, bake=True)

# Now query frames
for frame in [1, 50, 100, 150]:
    scene.frame_set(frame)
    obj = bpy.data.objects.get("Object_Name")
    print(f"Frame {frame}: {obj.location}")
```

### Option 2: Frame-by-Frame Update (Alternative)

```python
import bpy

scene = bpy.context.scene

# Update each frame manually
for frame in range(1, 251):
    scene.frame_set(frame)
    bpy.context.view_layer.update()  # Force dependency graph update
    scene.rigidbody_world.update()    # Update physics

# Query positions
scene.frame_set(100)
obj = bpy.data.objects.get("Object_Name")
print(f"Position: {obj.location}")
```

**Note**: Option 2 may not work reliably for complex simulations.

## Updated Workflow

### Before (DOESN'T WORK in MCP):
1. Setup scene
2. `bpy.ops.screen.animation_play()`
3. `time.sleep(3)`
4. `bpy.ops.screen.animation_cancel()`
5. Query positions ❌ **Objects don't move**

### After (WORKS):
1. Setup scene
2. Clear cache: `bpy.ops.ptcache.free_bake_all()`
3. **Bake physics**: `bpy.ops.ptcache.bake()`
4. Query positions ✓ **Baked simulation**

## Impact on Documentation

Need to update:
- `python.chatmode.md` - Physics verification workflow
- `test_conveyor_transport.ipynb` - Transport test cells
- `AGENTS.md` - Physics testing instructions

## Next Steps

1. ✅ Identified root cause
2. ⏳ Implement baking in test notebook
3. ⏳ Verify gravity transport works after baking
4. ⏳ Update all documentation
5. ⏳ Add baking to `blender/animate_lego_physics.py`

## Technical Details

### Why Animation Play Fails

- `bpy.ops.screen.animation_play()` is UI operator for **viewport playback**
- In headless/MCP mode, no screen/viewport context exists
- Physics engine never receives frame-by-frame update calls
- Objects remain at keyframe 1 positions

### Why Baking Works

- `bpy.ops.ptcache.bake()` explicitly calculates physics for all frames
- Results stored in point cache
- `scene.frame_set(N)` retrieves cached results
- Independent of viewport/UI state

## Verification Command

```python
# After baking, verify cache is populated
rbw = bpy.context.scene.rigidbody_world
cache = rbw.point_cache
print(f"Is baked: {cache.is_baked}")
print(f"Frames: {cache.frame_start} to {cache.frame_end}")
```

Expected output:
```
Is baked: True
Frames: 1 to 250
```
