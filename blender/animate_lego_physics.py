#!/usr/bin/env python3
"""
Blender script to animate LEGO parts with realistic physics simulation.

This script applies physics properties to LEGO parts and the sorting bucket,
enabling realistic gravity simulation and collision detection for the
sorting machine workflow.

Usage:
- Run this script in Blender after importing LEGO parts and creating the bucket
- Parts will fall under gravity and interact with the bucket and each other
- Physics simulation will start automatically after setup
"""

import bpy
from typing import Optional, List, Any, cast
from mathutils import Vector

# MCP-only: avoid UI-dependent baking operators
BAKE_TO_KEYFRAMES: bool = False


def ensure_material(
    name: str,
    color_rgba=(1.0, 1.0, 1.0, 1.0),
    roughness: float = 0.4,
    metallic: float = 0.0,
) -> Any:
    """Get or create a simple Principled BSDF material with the given color."""
    data = bpy.data
    mat = data.materials.get(name)
    if mat:
        return mat
    mat = data.materials.new(name=name)
    mat.use_nodes = True

    if mat.node_tree is None:
        return mat

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)

    base_color = bsdf.inputs.get("Base Color")
    if base_color is None:
        raise RuntimeError("Material node missing Base Color input")
    # Cast to NodeSocket so static checkers know `default_value` exists
    base_color_socket = cast(Any, base_color)
    base_color_socket.default_value = color_rgba

    rough_socket = bsdf.inputs.get("Roughness")
    if rough_socket is None:
        raise RuntimeError("Material node missing Roughness input")
    rough_socket_socket = cast(Any, rough_socket)
    rough_socket_socket.default_value = roughness

    metallic_socket = bsdf.inputs.get("Metallic")
    if metallic_socket is None:
        raise RuntimeError("Material node missing Metallic input")
    metallic_socket_socket = cast(Any, metallic_socket)
    metallic_socket_socket.default_value = metallic

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (200, 0)
    links.new(bsdf.outputs[0], out.inputs[0])
    return mat


# TODO: add proper typings for parameters
def assign_material(obj: Any, mat: Any) -> None:
    """Assign a material to an object (replace first slot or append)."""
    try:
        if not obj.data:
            return
        mats = obj.data.materials
        if len(mats) == 0:
            mats.append(mat)
        else:
            mats[0] = mat
    except Exception:
        pass


def hsv_to_rgba(h: float, s: float, v: float) -> tuple[float, float, float, float]:
    import colorsys

    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (r, g, b, 1.0)


def _ensure_rigidbody_world(scene: bpy.types.Scene) -> None:
    """Create a Rigid Body World if missing, using context overrides when needed.

    Some operators require an area/region context. We try VIEW_3D first, then
    PROPERTIES. If all attempts fail, raise a clear error.
    """
    if scene.rigidbody_world is not None:
        return

    wm = bpy.context.window_manager
    tried = False
    if wm is not None:
        for window in wm.windows:
            screen = window.screen
            if screen is None:
                continue
            for area in screen.areas:
                if area.type not in {"VIEW_3D", "PROPERTIES"}:
                    continue
                for region in area.regions:
                    if region.type != "WINDOW":
                        continue

                    try:
                        # Pylance can think temp_override may be None; guard and cast for the context manager
                        temp_override_fn = getattr(bpy.context, "temp_override", None)
                        if callable(temp_override_fn):
                            ctx_mgr = cast(
                                Any,
                                temp_override_fn(
                                    window=window,
                                    area=area,
                                    region=region,
                                    scene=scene,
                                    view_layer=bpy.context.view_layer,
                                ),
                            )
                            with ctx_mgr:
                                bpy.ops.rigidbody.world_add()
                                tried = True
                        else:
                            # Fallback: cannot override context here; we'll try without override later
                            pass
                    except Exception as exc:
                        print(
                            f"⚠️  rigidbody.world_add failed in area={area.type} region={region.type}: {exc}"
                        )
                        continue
                    if scene.rigidbody_world is not None:
                        break
                if scene.rigidbody_world is not None:
                    break
            if scene.rigidbody_world is not None:
                break

    # Last attempt without override (may work in some contexts)
    if scene.rigidbody_world is None:
        try:
            bpy.ops.rigidbody.world_add()
            tried = True
        except Exception:
            pass

    if scene.rigidbody_world is None:
        ctx_msg = " after trying VIEW_3D/PROPERTIES overrides" if tried else ""
        raise RuntimeError(
            "Operator rigidbody.world_add failed due to context. "
            "Open a 3D View in Blender and ensure MCP executes with UI context"
            + ctx_msg
        )


def setup_physics_world() -> None:
    """Configure the physics world settings for realistic LEGO simulation"""
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("No active scene found; cannot setup physics world")

    # Enable physics simulation
    scene.frame_set(1)

    # Ensure rigid body world exists (create when missing)
    _ensure_rigidbody_world(scene)

    # Set up gravity (standard Earth gravity: -9.81 m/s²)
    scene.gravity = (0, 0, -9.81)

    # Set simulation quality settings using correct Blender API
    rbw = scene.rigidbody_world
    if rbw is not None:
        rbw.time_scale = 1.0
        rbw.substeps_per_frame = 60
        rbw.solver_iterations = 120

    print("✅ Physics world configured with realistic gravity")


def setup_bucket_physics() -> Optional[Any]:
    """Setup physics properties for the sorting bucket"""

    bucket = bpy.data.objects.get("Sorting_Bucket")
    if not bucket:
        print("❌ Sorting bucket not found. Create bucket first.")
        return None

    # Select the bucket (ensure view layer exists)
    view_layer = bpy.context.view_layer

    if view_layer is None or view_layer.objects is None:
        raise RuntimeError("No view layer available to select bucket")

    view_layer.objects.active = bucket

    bucket.select_set(True)

    # Add rigid body physics (passive - doesn't move)
    bpy.ops.rigidbody.object_add(type="PASSIVE")

    # Set collision shape and other rigid body properties defensively
    rb = bucket.rigid_body
    if rb is None:
        # No rigid body present on bucket; nothing more to configure
        print(
            f"ℹ️ Bucket '{bucket.name}' has no rigid_body; added rigid body operator may have failed or been deferred."
        )
        return bucket

    # Directly assign known rigid body properties now that rb is typed
    rb.collision_shape = "MESH"
    rb.mass = 50.0
    rb.friction = 0.8
    rb.restitution = 0.3

    # Tolerances: enable small collision margin and margin usage to avoid floating
    rb.use_margin = True
    rb.collision_margin = 0.0

    print(f"✅ Physics setup for bucket: {bucket.name}")
    return bucket


# TODO: add proper types for parameter
def setup_lego_part_physics(obj: Any) -> None:
    """Setup physics properties for a single LEGO part"""
    if not obj:
        return

    # Select the object (ensure view layer exists)
    view_layer = bpy.context.view_layer
    if view_layer is None or view_layer.objects is None:
        pass
    else:
        view_layer.objects.active = obj
    obj.select_set(True)

    # Add rigid body physics (active - can move)
    bpy.ops.rigidbody.object_add(type="ACTIVE")

    # Guarded access to rigid_body attributes
    rb = obj.rigid_body
    if rb is None:
        raise RuntimeError(
            "No rigid body present (operator may have failed); nothing to configure"
        )

    # Collision shape: prefer MESH; if it's not supported this will raise at runtime
    rb.collision_shape = "MESH"

    # Set realistic LEGO properties
    rb.mass = 0.002
    rb.friction = 0.9
    rb.restitution = 0.4

    # Set damping to prevent eternal bouncing
    rb.linear_damping = 0.1
    rb.angular_damping = 0.1

    # Enable the object for physics simulation
    rb.enabled = True

    # Reduce collision margin for small parts to avoid floating above surfaces
    rb.use_margin = True
    rb.collision_margin = 0.0

    print(f"✅ Physics setup for LEGO part: {obj.name}")


def get_lego_parts() -> List[bpy.types.Object]:
    """Get all LEGO parts from the lego_parts collection"""
    lego_parts = []

    # Find the lego_parts collection using cast to handle dynamic API
    lego_collection = bpy.data.collections.get("lego_parts")
    if not lego_collection:
        print("❌ LEGO parts collection not found. Import LEGO parts first.")
        return []

    # Get all objects in the collection
    for obj in lego_collection.objects:
        if obj.type == "MESH":
            lego_parts.append(obj)

    print(f"📦 Found {len(lego_parts)} LEGO parts for physics simulation")
    return lego_parts


def position_parts_above_bucket(lego_parts: List[Any]) -> None:
    """Position LEGO parts above the bucket so they fall down"""
    if not lego_parts:
        return

    # Get the bucket to position parts above it
    # Prefer using an internal collider to compute safe spawn height
    collider = bpy.data.objects.get("Sorting_Bucket_Collider")
    bucket = bpy.data.objects.get("Sorting_Bucket")
    if collider:
        # compute top Z from collider bounding box
        bbox = [collider.matrix_world @ Vector(c) for c in collider.bound_box]
        max_z = max(v.z for v in bbox)
        bucket_top_z = (
            max_z + 0.10
        )  # 10cm above internal collider (increase spawn buffer)
    elif bucket:
        # fallback: use bucket location and a heuristic height
        bbox = [bucket.matrix_world @ Vector(c) for c in bucket.bound_box]
        max_z = max(v.z for v in bbox)
        bucket_top_z = max_z + 0.05
    else:
        print("❌ No bucket found - positioning parts at default height")
        bucket_top_z = 0.5  # Default height

    # Position parts in a grid above the bucket
    import math

    grid_size = math.ceil(math.sqrt(len(lego_parts)))
    spacing = 0.05  # 5cm spacing between parts
    start_x = -(grid_size - 1) * spacing / 2
    start_y = -(grid_size - 1) * spacing / 2

    for i, part in enumerate(lego_parts):
        if not part:
            continue

        # Calculate grid position
        row = i // grid_size
        col = i % grid_size

        # Set position above the bucket
        part.location.x = start_x + col * spacing
        part.location.y = start_y + row * spacing
        part.location.z = bucket_top_z + (i * 0.02)  # Stack with 2cm between each part

        # Clear any existing keyframes (only if they exist)
        try:
            if part.animation_data and part.animation_data.action:
                part.keyframe_delete("location")
                part.keyframe_delete("rotation_euler")
        except Exception:
            pass  # No keyframes to delete, which is fine

    print(
        f"✅ Positioned {len(lego_parts)} parts above the bucket at height {bucket_top_z:.2f}m"
    )


def randomize_starting_positions(lego_parts: List[Any]) -> None:
    """Add slight randomization to starting positions to prevent perfect stacking"""
    import random

    for _i, part in enumerate(lego_parts):
        if not part:
            continue

        # Add small random offset to prevent perfect alignment
        random_x = random.uniform(-0.01, 0.01)  # ±1cm  # noqa: S311
        random_y = random.uniform(-0.01, 0.01)  # ±1cm  # noqa: S311
        random_z = random.uniform(0, 0.005)  # 0-5mm upward  # noqa: S311

        # Apply random offset
        part.location.x += random_x
        part.location.y += random_y
        part.location.z += random_z

        # Add slight random rotation
        part.rotation_euler.x += random.uniform(-0.1, 0.1)  # noqa: S311
        part.rotation_euler.y += random.uniform(-0.1, 0.1)  # noqa: S311
        part.rotation_euler.z += random.uniform(-0.1, 0.1)  # noqa: S311

    print("✅ Added random variation to starting positions")


def create_physics_ground_plane() -> Optional[Any]:
    """Create an invisible ground plane to catch falling parts"""
    # Create a large plane at the new ground level
    bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))
    ground_plane = bpy.context.active_object

    if ground_plane:
        ground_plane.name = "Physics_Ground"

        # Make it transparent but keep collision
        ground_plane.hide_render = True
        ground_plane.display_type = "WIRE"

        # Add passive rigid body
        bpy.ops.rigidbody.object_add(type="PASSIVE")
        rb = ground_plane.rigid_body

        if rb is None:
            raise RuntimeError(
                "No rigid body present (operator may have failed); nothing to configure"
            )

        rb.collision_shape = "BOX"
        rb.friction = 0.8
        rb.restitution = 0.2

        print("✅ Created physics ground plane")
        return ground_plane

    return None


def manual_per_frame_sampling(start: int, end: int) -> None:
    """Manually sample evaluated transforms for rigid-body objects and keyframe them.

    This is a robust fallback for headless/MCP runs where bpy.ops.rigidbody baking
    operators are unavailable. It evaluates the depsgraph each frame and writes
    the evaluated world transform back to the original objects as keyframes.
    """
    try:
        deps = bpy.context.evaluated_depsgraph_get()

        # Collect active rigid body objects (lego_parts, conveyor_belt, bucket)
        objs = []
        lego_col = bpy.data.collections.get("lego_parts")

        if lego_col:
            objs.extend([o for o in lego_col.objects if o.rigid_body is not None])
        conv_col = bpy.data.collections.get("conveyor_belt")

        if conv_col:
            objs.extend([o for o in conv_col.objects if o.rigid_body is not None])
        bucket = bpy.data.objects.get("Sorting_Bucket")

        if bucket and bucket.rigid_body is not None:
            objs.append(bucket)

        # Deduplicate
        objs = list(dict.fromkeys(objs))

        scene = bpy.context.scene

        if scene is None:
            raise RuntimeError("No active scene found; cannot perform manual sampling")

        for f in range(start, end + 1):
            scene.frame_set(f)
            deps.update()

            for o in objs:
                try:
                    eo = o.evaluated_get(deps)
                    wm = eo.matrix_world.copy()
                    # Write location/rotation back to object and keyframe
                    o.location = wm.to_translation()
                    try:
                        o.rotation_euler = wm.to_euler()
                    except Exception:
                        # Some objects may use quaternion rotation; skip if necessary
                        pass
                    o.keyframe_insert(data_path="location", frame=f)
                    try:
                        o.keyframe_insert(data_path="rotation_euler", frame=f)
                    except Exception:
                        pass
                except Exception:
                    pass
    except Exception:
        pass


def start_physics_simulation() -> None:
    """Start the physics simulation"""
    scene = bpy.context.scene

    # Set frame range for simulation
    if scene is None:
        raise RuntimeError("No active scene found; cannot start physics simulation")

    scene.frame_start = 1
    scene.frame_end = 100  # limit animation to 100 frames
    scene.frame_set(1)

    # Ensure rigid body world exists (use context-aware helper)
    if not scene.rigidbody_world:
        _ensure_rigidbody_world(scene)

    # Update the scene to ensure physics is ready
    view_layer = bpy.context.view_layer

    if view_layer is None:
        raise RuntimeError(
            "No active view layer found; cannot start physics simulation"
        )

    view_layer.update()

    if BAKE_TO_KEYFRAMES:
        # Kept for completeness, but disabled in MCP runs
        try:
            print(f"🔁 Baking rigid-body simulation to keyframes (1..100)...")
            bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=100)
            print(
                "✅ Rigid-body baked to keyframes (bpy.ops.rigidbody.bake_to_keyframes)"
            )
        except Exception as err:
            print(
                f"⚠️  Bake to keyframes unavailable or failed ({err!s}); using manual per-frame sampling instead"
            )
            manual_per_frame_sampling(start=1, end=100)
    else:
        print("ℹ️  Skipping bake (MCP mode); using manual per-frame sampling…")
        manual_per_frame_sampling(start=1, end=100)


def setup_collision_collections() -> None:
    """Setup collision collections for better organization"""
    # No longer needed - using functional collections instead
    print(
        "ℹ️  Using simplified functional organization (bucket, conveyor_belt, lego_parts)"
    )


def main() -> None:
    """Main function to setup physics simulation for LEGO parts"""
    print("🔬 Setting up LEGO physics simulation...")

    # Clear any existing physics settings
    bpy.ops.object.select_all(action="SELECT")

    # Check if rigid body world exists, if not create it
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("No active scene found; cannot setup physics simulation")

    if not scene.rigidbody_world:
        _ensure_rigidbody_world(scene)

    # Setup physics world
    setup_physics_world()

    # Setup collision collections
    setup_collision_collections()

    # Create ground plane
    _ = create_physics_ground_plane()

    # Setup bucket physics
    bucket = setup_bucket_physics()
    if not bucket:
        print("❌ Cannot proceed without sorting bucket")
        return

    # Get LEGO parts
    lego_parts = get_lego_parts()
    if not lego_parts:
        print("❌ Cannot proceed without LEGO parts")
        return

    # Setup physics for each LEGO part
    for part in lego_parts:
        setup_lego_part_physics(part)

    # Assign unique, deterministic colors to each LEGO part to aid debugging
    try:
        total = max(1, len(lego_parts))
        for i, part in enumerate(lego_parts):
            h = float(i) / float(total)
            rgba = hsv_to_rgba(h, 0.7, 0.9)
            mat = ensure_material(
                f"LEGO_Part_Mat_{i:03d}", color_rgba=rgba, roughness=0.35
            )
            assign_material(part, mat)
        print(f"\u2705 Assigned unique colors to {len(lego_parts)} LEGO parts")
    except Exception:
        print("\u26a0\ufe0f Failed to assign per-part colors (continuing)")

        # Position parts above the bucket so they can fall
        position_parts_above_bucket(lego_parts)

        # Clear any animation data on parts to avoid pre-existing keyframes freezing transforms
        for p in lego_parts:
            if p.animation_data:
                p.animation_data_clear()

    # Add randomization to prevent perfect stacking
    randomize_starting_positions(lego_parts)

    # Start the simulation
    start_physics_simulation()

    print("🎉 Physics simulation setup complete!")
    print(f"📊 Simulating {len(lego_parts)} LEGO parts with realistic physics")
    print("🎯 Parts are positioned above the bucket and ready to fall")
    print("⚡ Go to frame 1 in Blender and press SPACE to start the simulation!")


# Always run main when script is executed
main()
