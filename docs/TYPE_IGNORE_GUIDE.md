# Type Ignore Guide for Blender Code

This document explains when and why we use `# type: ignore` comments in this codebase.

## Philosophy

We avoid `# type: ignore` whenever possible and prefer:
1. Proper type annotations with `Optional[Type]`
2. Runtime checks with `isinstance()`
3. Type narrowing with assertions

However, Blender's type stubs (fake-bpy-module) have limitations that require targeted type ignores in specific cases.

## Known Blender Type Stub Limitations

### 0. Import Error Fallbacks (Exception Handler)

**Problem**: When importing outside Blender (e.g., for type checking, testing, or documentation generation), bpy modules aren't available. We set fallback None values to allow the module to import.

**Pattern**:
```python
try:
    import bpy
    from bpy.types import Material, Mesh
    from mathutils import Vector
except ImportError:
    # Type ignore: Fallback definitions for when bpy is unavailable
    # These are replaced at runtime in Blender
    bpy = None  # type: ignore[assignment]
    Material = None  # type: ignore[assignment,misc]
    Mesh = None  # type: ignore[assignment,misc]
    Vector = None  # type: ignore[assignment,misc]
    
    def cast(typ, val):  # type: ignore[no-untyped-def]
        """Fallback cast mock for when typing.cast is unavailable."""
        return val
```

**Why Safe**:
- Only used when imports fail (outside Blender context)
- Each function checks `if bpy is None: return` before use
- Real Blender runtime uses actual imported types
- Type checkers can analyze the module without Blender installed

**Type Ignore Tags**:
- `[assignment]` - Assigning None to typed variable
- `[misc]` - Type variable assignment to None (for types like Material, Mesh)
- `[no-untyped-def]` - Function without type annotations (intentional for fallback)

**Files**: `blender_debug.py`, `validate_scene.py`

### 1. Object.data Polymorphism

**Problem**: `Object.data` is typed as `Union[Mesh, Curve, Camera, Light, ...]` in stubs. The stubs cannot express the runtime constraint: "when `obj.type == 'MESH'`, then `obj.data` is guaranteed to be `Mesh`".

**Pattern**:
```python
if obj.type == 'MESH' and obj.data and hasattr(obj.data, 'materials'):
    # Type ignore: obj.type == 'MESH' guarantees obj.data is Mesh at runtime
    # Stubs can't express this constraint, but hasattr provides safety
    materials = obj.data.materials  # type: ignore[union-attr]
```

**Why Safe**: 
- Runtime check `obj.type == 'MESH'` guarantees type
- `hasattr()` check provides additional safety
- This is the recommended pattern per AGENTS.md

**Files**: `blender_debug.py`, `validate_scene.py`

### 2. Shader Node Socket Dynamic Attributes

**Problem**: Blender shader nodes have socket types (`NodeSocketColor`, `NodeSocketFloat`) that inherit from `NodeSocket`, but the base class doesn't define `default_value`. The stubs can't capture this dynamic typing.

**Pattern**:
```python
color_input = emission.inputs.get("Color")
if color_input and hasattr(color_input, 'default_value'):
    # Type ignore: NodeSocketColor has default_value at runtime
    # Base NodeSocket doesn't, but hasattr check ensures safety
    color_input.default_value = color  # type: ignore[union-attr]
```

**Why Safe**:
- `hasattr()` check guarantees attribute exists
- Runtime behavior is correct
- Stubs use base `NodeSocket` type which lacks `default_value`

**Files**: `blender_debug.py`

### 3. Vector Constructor Type Signature

**Problem**: `Vector()` constructor accepts tuples at runtime, but stubs expect `Sequence[float]`. The stubs are overly strict - tuples ARE sequences.

**Pattern**:
```python
# Type ignore: Vector constructor accepts tuple but stubs expect Sequence[float]
# Tuple is a valid sequence type, this is overly strict typing in stubs
min_corner = Vector((x, y, z))  # type: ignore[arg-type]
```

**Why Safe**:
- `tuple` is a `Sequence[float]`
- Runtime behavior is correct
- This is standard mathutils usage

**Files**: `blender_debug.py`

### 4. Scene Context Assertion

**Problem**: `bpy.context.scene` is typed as `Optional[Scene]`, but in normal Blender runtime it's guaranteed to exist (only None during shutdown or errors).

**Pattern**:
```python
scene = bpy.context.scene
# Type ignore: bpy.context.scene can be None in stubs but is guaranteed
# in normal Blender runtime; assertion provides type narrowing
assert scene is not None, "Scene must exist"  # noqa: S101
```

**Why Safe**:
- Scene always exists during normal operations
- Assertion provides type narrowing for Pylance
- `noqa: S101` suppresses assert warning (assert is intentional for types)

**Files**: `blender_debug.py`, `validate_scene.py`

## Type Ignore Tags Used

We use specific type ignore tags (not just bare `# type: ignore`) for clarity:

- `# type: ignore[union-attr]` - Accessing attribute on union type (obj.data, node sockets)
- `# type: ignore[arg-type]` - Argument type mismatch (Vector constructor)
- `# noqa: S101` - Suppress "assert detected" linting warning

## When NOT to Use Type Ignore

Do NOT use type ignore for:

1. **Missing imports** - Add proper try/except with fallback
2. **Optional types** - Use `Optional[Type]` and check with `isinstance()`
3. **Any types** - Import specific types from `bpy.types`
4. **Lazy type checking** - Fix the actual type issue

## Example: Proper isinstance() Pattern

For regular Blender objects (not the special cases above), use isinstance:

```python
from bpy.types import Object

obj: Optional[Object] = None
if isinstance(bpy.context.active_object, Object):
    obj = bpy.context.active_object
    # Now obj is properly typed as Object, not Optional[Object]
```

## References

- See `AGENTS.md` for full typing guidance
- Blender type stubs: https://github.com/nutti/fake-bpy-module
- Type narrowing: https://mypy.readthedocs.io/en/stable/type_narrowing.html
