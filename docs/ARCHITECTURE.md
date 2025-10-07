# System Architecture

## Overview

The LEGO Sorter is a physics-based simulation that models a complete automated sorting system. The architecture separates script generation (Python), scene control (MCP protocol), and rendering (Blender) to enable reproducible, code-driven scene generation.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Development Machine                      │
│                                                               │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │  VSCode/Editor  │◄───────►│  Python Scripts  │          │
│  │                 │         │  (blender/*.py)  │          │
│  └─────────────────┘         └────────┬─────────┘          │
│           │                            │                     │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           BlenderMCPClient (utils/)                  │   │
│  │  • Socket connection (localhost:9876)                │   │
│  │  • JSON command protocol                             │   │
│  │  • Script execution & result handling                │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│                         │ TCP Socket                         │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              Blender (with MCP Addon)                │   │
│  │  • Scene state (collections, objects)                │   │
│  │  • Physics simulation (rigidbody world)              │   │
│  │  • Rendering engine (Eevee/Cycles)                   │   │
│  │  • LDraw import (external geometry)                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Scene Generation Pipeline

```
Start
  │
  ▼
┌──────────────────┐
│ clear_scene.py   │  Remove all objects, collections, physics
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ create_bucket.py │  Boolean operations for hollow geometry
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ create_conveyor  │  Inclined belt with friction physics
│     _belt.py     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ import_lego      │  LDraw file import (external geometry)
│    _parts.py     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ animate_lego     │  Rigid body simulation, collision detection
│   _physics.py    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ setup_lighting   │  Three-point lighting system
│      .py         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ render_snapshot  │  Camera creation, multi-view renders
│      .py         │
└────────┬─────────┘
         │
         ▼
       End
```

### 2. MCP Communication Flow

```
Python Script                  MCP Client                    Blender
     │                             │                            │
     ├─execute_script_file()──────►│                            │
     │                             ├─connect(localhost:9876)────►│
     │                             │                            │
     │                             ├─send(JSON command)────────►│
     │                             │                            │
     │                             │                  ┌─────────▼──────┐
     │                             │                  │ Execute Python │
     │                             │                  │ in bpy context │
     │                             │                  └─────────┬──────┘
     │                             │                            │
     │                             │◄──────(JSON response)──────┤
     │                             │                            │
     │◄──────return result─────────┤                            │
     │                             │                            │
```

### 3. Physics Simulation Timeline

```
Frame 1          Frame 10         Frame 20         Frame 50+
   │                │                │                │
   │   Parts in     │   Parts        │   Parts on     │   Parts
   │   bucket       │   falling      │   conveyor     │   sorted
   │   (at rest)    │   (gravity)    │   (transport)  │   (complete)
   │                │                │                │
   └────────────────┴────────────────┴────────────────┘
        Static          Dynamic          Transport       Settling
```

## Key Design Decisions

### 1. Code-Driven Scene Generation

**Decision**: No binary .blend files; everything generated from Python scripts

**Rationale**:
- **Version Control**: All changes trackable in Git (no binary diffs)
- **Reproducibility**: Anyone can recreate exact scene from source
- **Modularity**: Components developed/tested independently
- **CI/CD**: Automated testing and rendering possible
- **Collaboration**: No merge conflicts on binary files

**Implementation**:
- Each script is self-contained with `main()` function
- Scripts auto-execute when imported (no `if __name__ == "__main__"` checks)
- Scene state is ephemeral (cleared on each run)

### 2. MCP Over Direct bpy Imports

**Decision**: Remote execution via MCP instead of direct bpy imports

**Rationale**:
- **Process Isolation**: Blender crashes don't affect main process
- **State Management**: Clean separation between control and execution
- **Debugging**: Can inspect Blender state while scripts run
- **Flexibility**: Same scripts work from command line or IDE
- **Timeout Control**: Can abort long-running operations

**Trade-offs**:
- Adds latency (~100-500ms per command)
- Requires MCP server to be running
- More complex error handling (network + execution errors)

### 3. Collection-Based Organization

**Decision**: Objects grouped in named collections (`bucket`, `conveyor_belt`, `lego_parts`)

**Rationale**:
- **Namespace Isolation**: Prevents object name conflicts
- **Lifecycle Management**: Easy to clear/recreate specific components
- **Visual Organization**: Blender outliner shows logical grouping
- **Batch Operations**: Can operate on entire collection at once

**Pattern**:
```python
# Create collection
collection = bpy.data.collections.new("my_component")
bpy.context.scene.collection.children.link(collection)

# Add objects to collection
collection.objects.link(obj)
```

### 4. Boolean Operations for Complex Geometry

**Decision**: Use DIFFERENCE modifier for hollow bucket instead of manual modeling

**Rationale**:
- **Parametric**: Can adjust dimensions programmatically
- **Reproducible**: Same code always produces same geometry
- **Maintainable**: Easier to modify than vertex-level editing
- **Physics-Friendly**: Clean manifold geometry for collisions

**Example**: Bucket with hole in bottom created by subtracting cylinder from base

### 5. Realistic Physics Constants

**Decision**: Use measured LEGO properties (2g mass, 0.9 friction)

**Rationale**:
- **Validation**: Simulation matches real-world behavior
- **Predictability**: Physics behaves as expected
- **Debugging**: Anomalies indicate code issues, not parameter tuning
- **Documentation**: Properties are self-documenting

**Constants**:
```python
LEGO_MASS = 0.002         # 2 grams (measured)
LEGO_FRICTION = 0.9       # High friction (LEGO grips well)
CONVEYOR_ANGLE = 0.15     # ~8.6° (tested for reliable transport)
```

## State Management

### Scene State (Ephemeral)

**Storage**: Blender's internal data structures (`bpy.data.*`)

**Lifecycle**: Created fresh on each run, destroyed on clear

**Components**:
- Objects: meshes, empties, cameras, lights
- Collections: logical groupings
- Materials: Principled BSDF shaders
- Physics: rigidbody world, constraints

**Access Pattern**:
```python
# Creation
obj = bpy.data.objects.new("MyObject", mesh)
collection.objects.link(obj)

# Access
obj = bpy.data.objects.get("MyObject")
if obj is None:
    # Handle missing object
```

### Physics State (Keyframes)

**Storage**: Animation keyframes on transform channels

**Lifecycle**: Generated during physics simulation, persists until scene cleared

**Components**:
- Location keyframes: object positions per frame
- Rotation keyframes: object orientations per frame
- Rigidbody cache: collision detection results

**Note**: Physics state is NOT currently baked to keyframes (see `BAKE_TO_KEYFRAMES = False` in `animate_lego_physics.py`). This is intentional for MCP compatibility.

### Render Outputs (Persistent)

**Storage**: PNG files in `renders/` directory

**Lifecycle**: Created by `render_snapshot.py`, persists across runs

**Organization**:
```
renders/
  frame_01/
    snapshot_ortho_top.png
    snapshot_ortho_front.png
    snapshot_ortho_iso_ne.png
    ...
  frame_05/
    ...
```

## Extension Points

### Adding a New Scene Component

1. **Create script**: `blender/create_<component>.py`
2. **Define collection**: `bpy.data.collections.new("<component>")`
3. **Create geometry**: Use primitives or boolean operations
4. **Set physics**: Add rigidbody if needed
5. **Add materials**: Use `ensure_material()` pattern
6. **Integrate**: Add to `run_lego_sorter.py` pipeline

### Adding a New Physics Behavior

1. **Identify frame range**: When should behavior occur?
2. **Set properties**: Mass, friction, collision groups
3. **Add constraints**: Hinge, slider, etc.
4. **Keyframe animation**: If scripted movement needed
5. **Test timing**: Ensure no race conditions with other physics

### Adding a New Render Output

1. **Position camera**: Set location and rotation
2. **Configure render**: Resolution, samples, file format
3. **Set output path**: Use `renders/` directory structure
4. **Trigger render**: `bpy.ops.render.render(write_still=True)`
5. **Verify output**: Check file was created

## Performance Characteristics

### Script Execution Time

| Operation              | Typical Duration | Notes                          |
|------------------------|------------------|--------------------------------|
| Clear scene            | 1-2 seconds      | Fast, minimal geometry         |
| Create bucket          | 2-5 seconds      | Boolean operations slow        |
| Create conveyor        | 5-10 seconds     | Complex support structures     |
| Import LEGO parts      | 30-60 seconds    | LDraw parsing overhead         |
| Setup physics          | 5-10 seconds     | Rigidbody world creation       |
| Render snapshot (1 view)| 10-30 seconds   | Depends on samples/resolution  |

### Optimization Strategies

1. **Skip optional steps**: Use `SKIP_CONVEYOR=1` environment variable
2. **Reduce part count**: Modify `COMMON_PARTS` list in `import_lego_parts.py`
3. **Lower render samples**: Faster iterations during development
4. **Debug mode**: `BLENDER_MCP_DEBUG=1` for shorter timeouts
5. **Parallel rendering**: Multiple views can be rendered in sequence

## Error Handling Strategy

### Levels of Errors

1. **Connection Errors**: MCP server not running or unreachable
   - **Recovery**: Prompt user to start Blender MCP addon
   - **Tools**: `test_connection()` before operations

2. **Execution Errors**: Python exceptions in Blender context
   - **Recovery**: Print detailed error message with context
   - **Tools**: Try/except blocks with object state logging

3. **Physics Errors**: Simulation produces unexpected results
   - **Recovery**: Diagnostic scripts (e.g., `diagnose_raycast_frame20.py`)
   - **Tools**: Frame-by-frame inspection, state validation

4. **Timeout Errors**: Operation takes too long
   - **Recovery**: Retry with exponential backoff
   - **Tools**: Configurable timeouts via environment variables

### Error Context Pattern

```python
try:
    bpy.ops.rigidbody.world_add()
except Exception as e:
    print(f"❌ Failed to add rigidbody world")
    print(f"   Scene: {bpy.context.scene.name}")
    print(f"   Active object: {bpy.context.active_object}")
    print(f"   Collections: {[c.name for c in bpy.data.collections]}")
    print(f"   Error: {e}")
    raise
```

This provides AI assistants with enough context to diagnose issues.

## Testing Strategy

### Manual Testing

1. **Complete workflow**: Run `python run_lego_sorter.py`
2. **Individual scripts**: Execute single script via MCP
3. **Direct Blender**: Copy script to Blender's script editor
4. **Scene validation**: Use inspection scripts after each step

### Automated Testing (Future)

1. **Unit tests**: Test individual functions with mocked bpy
2. **Integration tests**: Test full pipeline with headless Blender
3. **Visual regression**: Compare renders to baseline images
4. **Physics validation**: Check object positions at key frames

## Security Considerations

**MCP Connection**: Localhost only (not exposed to network)

**Script Execution**: Arbitrary Python code execution in Blender context
- Only execute trusted scripts
- Review code before running via MCP

**File Access**: Scripts have full filesystem access
- LDraw path is user-configurable
- Render outputs go to project directory

## Future Architecture Improvements

1. **Camera Identification System**
   - Add raycast-based part detection
   - Integrate color/shape classification
   - Store identification results in custom properties

2. **Sorting Logic**
   - Implement tube splitting mechanism
   - Add sorting decision tree
   - Multiple output buckets

3. **Performance Optimization**
   - Cache LDraw part imports
   - Parallel physics simulation
   - GPU-accelerated rendering

4. **Robustness**
   - Better retry logic with jitter
   - Graceful degradation on errors
   - Automatic scene recovery

5. **Observability**
   - Structured logging to file
   - Telemetry for operation timing
   - Scene state snapshots for debugging
