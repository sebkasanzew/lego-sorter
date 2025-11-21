# Conveyor Belt Transport Improvements

## Problem Statement

LEGO parts were not being transported on the conveyor belt. Parts remained stationary despite the animated conveyor slats moving beneath them.

## Root Cause Analysis

1. **Initial Positioning**: LEGO parts were spawned in the bucket collection at origin, not positioned on the conveyor belt surface
2. **Contact Issues**: Parts had no guaranteed contact with the moving slats
3. **Friction Values**: Default friction values (slats: 1.5, parts: 0.9) were insufficient for reliable transport
4. **Solver Settings**: Default rigid body solver iterations (10) provided inadequate accuracy for friction-based transport

## Solutions Implemented

### 1. Part Positioning Script (`place_parts_on_conveyor.py`)

**Purpose**: Positions LEGO parts directly on the conveyor belt surface in an organized grid.

**Key Features**:
- Calculates conveyor surface position in world space
- Arranges parts in 3-column grid with proper spacing
- Places parts slightly above surface (0.02 units) to avoid initial penetration
- Resets part rotations to ensure flat seating
- Verifies physics setup after positioning

**Algorithm**:
```
1. Get conveyor world transform and dimensions
2. Calculate starting position at belt surface
3. For each part:
   - Calculate grid position (row, column)
   - Set location on belt surface
   - Reset rotation
   - Ensure active rigid body
```

### 2. Physics Enhancement Script (`enhance_conveyor_physics.py`)

**Purpose**: Optimizes friction and solver settings for reliable transport.

**Improvements**:

#### Slat Physics
- **Friction**: Increased from 1.5 → 2.5 (167% increase)
- **Restitution**: Set to 0.0 (no bounce)
- **Collision Margin**: 0.0 (tight contact)

#### Part Physics
- **Friction**: Increased from 0.9 → 1.5 (67% increase)
- **Restitution**: Reduced to 0.2 (minimal bounce)
- **Linear Damping**: Reduced to 0.05 (more responsive)
- **Angular Damping**: Reduced to 0.05 (more responsive)
- **Collision Margin**: 0.0 (tight contact)

#### Rigid Body World
- **Solver Iterations**: Increased from 10 → 20 (100% increase)
  - More iterations = better friction/contact resolution
  - Critical for kinematic-driven transport

### 3. Validation Script (`tests/test_conveyor_transport.py`)

**Purpose**: Automated testing of conveyor transport functionality.

**Test Method**:
1. Track single part position over frames 1, 20, 40
2. Calculate X-axis displacement (conveyor direction)
3. Pass criteria: Movement > 0.1 units
4. Reports detailed movement analysis

## Physics Principles

### Friction-Based Transport

The conveyor uses **kinematic passive rigid bodies** (slats) to transport **active rigid bodies** (LEGO parts) via friction:

```
Force_transport = Friction_coefficient × Normal_force
```

**Key Parameters**:
- Higher friction coefficient → stronger grip
- Zero collision margin → better contact
- More solver iterations → accurate friction simulation

### Contact Resolution

Blender's rigid body solver uses iterative constraint resolution:

```
For each iteration:
    1. Calculate constraint violations (penetration, friction)
    2. Apply corrective impulses
    3. Update velocities
```

**20 iterations** provides sufficient accuracy for the friction forces between moving slats and resting parts to properly transfer momentum.

## Integration with Pipeline

### Updated Pipeline Order

```
1. clear_scene.py          → Reset scene
2. create_sorting_bucket.py → Create bucket with hole
3. create_conveyor_belt.py  → Create belt + animated slats
4. import_lego_parts.py     → Load LEGO geometries
5. animate_lego_physics.py  → Configure base physics
6. place_parts_on_conveyor.py → ✨ NEW: Position on belt
7. enhance_conveyor_physics.py → ✨ NEW: Optimize physics
```

### Notebook Integration

Added to `quick_experiments.ipynb`:
- **Section**: "Conveyor Belt Transport Testing"
- **Cell 1**: Full scene build (steps 1-5)
- **Cell 2**: Positioning + enhancement (steps 6-7)
- **Cell 3**: Initial state verification
- **Cell 4**: Movement analysis over 50 frames
- **Cell 5**: Viewport visualization

## Expected Results

### Quantitative Metrics
- **Part displacement**: > 0.1 units along X-axis in 40 frames
- **Transport velocity**: ~0.003-0.005 units/frame (depends on slat speed)
- **Contact stability**: Parts remain on belt (no falling off)

### Visual Indicators
- Parts positioned in grid on belt at frame 1
- Gradual upward motion along inclined belt
- Parts follow slat movement direction
- Minimal bouncing or sliding

## Testing Instructions

### Method 1: Notebook (Interactive)
```python
# In quick_experiments.ipynb
# Run cells in "Conveyor Belt Transport Testing" section
# Observe movement analysis output
```

### Method 2: Validation Script (Automated)
```bash
python tests/test_conveyor_transport.py
```

### Method 3: Manual Blender
```
1. Run full pipeline
2. Set frame to 1 → Observe parts on belt
3. Press Space → Run simulation
4. Scrub timeline → Verify upward motion
```

## Troubleshooting

### Parts Not Moving
- **Check**: Slat animation (verify keyframes exist)
- **Check**: Part positions (ensure on belt surface)
- **Check**: Rigid body world exists

### Parts Fall Through Belt
- **Fix**: Reduce collision margin to 0.0
- **Fix**: Increase solver iterations to 20+

### Parts Slide Off Belt
- **Fix**: Increase friction on slats/parts
- **Fix**: Add invisible side guard walls

### Parts Bounce Excessively
- **Fix**: Reduce restitution values
- **Fix**: Increase damping values

## Performance Notes

- **Solver iterations**: 20 iterations = ~2x compute time vs. default (10)
- **Acceptable trade-off**: Physics accuracy >> render speed for simulation
- **Optimization**: Consider reducing iterations for preview, increase for final render

## Future Enhancements

1. **Adaptive friction**: Adjust friction based on part mass
2. **Belt speed control**: Parameterize slat animation speed
3. **Vibration**: Add subtle vertical motion for part separation
4. **Sensors**: Detect when parts reach end of belt
5. **Side guards**: Add invisible walls to prevent parts falling off

## References

- Blender Rigid Body Docs: https://docs.blender.org/manual/en/latest/physics/rigid_body/
- Project docs: `docs/GLOSSARY.md`, `AGENTS.md`
- Related scripts: `blender/create_conveyor_belt.py`, `blender/animate_lego_physics.py`

---

**Status**: ✅ Implemented and ready for testing  
**Date**: 2025-10-29  
**Files Modified**: 3 new scripts, 1 notebook updated
