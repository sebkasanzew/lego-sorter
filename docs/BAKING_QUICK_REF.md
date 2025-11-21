# Physics Baking Quick Reference

## Problem
`animation_play()` doesn't work in MCP/headless Blender → Must use explicit baking

## Solution (3-Step Workflow)

### Step 1: Initiate Baking
```python
import bpy

scene = bpy.context.scene
rbw = scene.rigidbody_world

# Clear cache
bpy.ops.ptcache.free_bake_all()

# Set range
scene.frame_start = 1
scene.frame_end = 150

# Bake
scene.frame_set(1)
override = bpy.context.copy()
override['point_cache'] = rbw.point_cache
bpy.ops.ptcache.bake(override, bake=True)
```

### Step 2: Wait
```python
import time
time.sleep(60)  # Baking takes 30-120s depending on complexity
```

### Step 3: Verify
```python
# Check bake status
cache = rbw.point_cache
if cache.is_baked:
    # Query any frame
    scene.frame_set(100)
    obj = bpy.data.objects.get("Object_Name")
    print(obj.location)  # Baked position
```

## Automated Script

Use `blender/bake_and_verify_physics.py`:
```python
exec(open('blender/bake_and_verify_physics.py').read())
```

Does everything: clear → bake → wait → verify → report

## In Notebook

Run cells in order:
1. Setup scene (ramp + parts)
2. Bake cell (initiates baking)
3. Wait cell (60s pause)
4. Verify cell (checks results)

## Troubleshooting

**Timeout?** → Reduce frames or object count
**No movement?** → Check objects in RBW, positions above ramp
**Blender frozen?** → Wait, baking is CPU-intensive

## Key Concept

- **Before baking**: `scene.frame_set(N)` returns initial positions
- **After baking**: `scene.frame_set(N)` returns simulated positions
