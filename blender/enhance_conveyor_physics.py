"""
Enhanced conveyor belt physics setup for reliable LEGO part transport.

This script applies additional physics optimizations to ensure LEGO parts
are properly transported by the moving conveyor slats.
"""

import bpy


def enhance_slat_physics() -> None:
    """Increase friction on conveyor slats for better grip on LEGO parts."""
    conveyor_col = bpy.data.collections.get("conveyor_belt")
    if not conveyor_col:
        print("❌ Conveyor belt collection not found")
        return

    slats = [obj for obj in conveyor_col.objects if "Slat" in obj.name]

    if not slats:
        print("❌ No conveyor slats found")
        return

    print(f"✓ Found {len(slats)} conveyor slats")

    enhanced_count = 0
    for slat in slats:
        rb = slat.rigid_body
        if rb:
            # Increase friction significantly
            rb.friction = 2.5  # Very high friction for grip
            rb.restitution = 0.0  # No bounce
            rb.collision_margin = 0.0  # Tight contact
            rb.use_margin = True
            enhanced_count += 1

    print(f"✓ Enhanced physics on {enhanced_count} slats (friction=2.5)")


def enhance_lego_part_physics() -> None:
    """Increase friction on LEGO parts for better grip."""
    lego_col = bpy.data.collections.get("lego_parts")
    if not lego_col:
        print("❌ LEGO parts collection not found")
        return

    parts = list(lego_col.objects)
    if not parts:
        print("❌ No LEGO parts found")
        return

    print(f"✓ Found {len(parts)} LEGO parts")

    enhanced_count = 0
    for part in parts:
        rb = part.rigid_body
        if rb:
            # Increase friction to match slats
            rb.friction = 1.5  # High friction for grip
            rb.restitution = 0.2  # Minimal bounce
            rb.collision_margin = 0.0  # Tight contact
            rb.use_margin = True

            # Reduce damping so parts respond better to conveyor motion
            rb.linear_damping = 0.05
            rb.angular_damping = 0.05

            enhanced_count += 1

    print(f"✓ Enhanced physics on {enhanced_count} parts (friction=1.5)")


def optimize_rigid_body_world() -> None:
    """Optimize rigid body world settings for accurate conveyor simulation."""
    scene = bpy.context.scene
    if not scene or not scene.rigidbody_world:
        print("❌ No rigid body world found")
        return

    rbw = scene.rigidbody_world

    # Increase solver iterations for better accuracy
    rbw.solver_iterations = 20  # More iterations = better friction/contact

    # Use smaller time step for more accurate physics
    rbw.time_scale = 1.0

    print("✓ Optimized rigid body world (solver_iterations=20)")


def add_invisible_side_guards() -> None:
    """Add invisible side barriers to prevent parts from falling off the belt."""
    conveyor = bpy.data.objects.get("Conveyor_Belt")

    # If conveyor was deleted, use a slat as reference
    if not conveyor:
        slats = [obj for obj in bpy.data.objects if "Slat" in obj.name]
        if slats:
            conveyor = slats[0]

    if not conveyor:
        print("⚠️ No conveyor reference found, skipping side guards")
        return

    conveyor_col = bpy.data.collections.get("conveyor_belt")
    if not conveyor_col:
        print("❌ Conveyor collection not found")
        return

    # Get conveyor dimensions (approximate from slat if needed)
    width = 0.25  # Approximate belt width
    length = 1.2  # Approximate belt length

    # Create left and right guard barriers
    for side_name, y_offset in [("Left", width * 0.5), ("Right", -width * 0.5)]:
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(
                conveyor.location.x,
                conveyor.location.y + y_offset,
                conveyor.location.z,
            ),
        )

        guard = bpy.context.active_object
        if not guard:
            continue

        guard.name = f"Conveyor_Guard_{side_name}"
        guard.scale = (length, 0.01, 0.1)  # Thin wall
        guard.rotation_euler = conveyor.rotation_euler.copy()

        # Apply transforms
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # Make invisible
        guard.hide_render = True
        guard.hide_viewport = True

        # Add passive rigid body
        bpy.ops.rigidbody.object_add(type="PASSIVE")
        rb = guard.rigid_body
        if rb:
            rb.collision_shape = "BOX"
            rb.friction = 0.8
            rb.kinematic = False

        # Add to conveyor collection
        conveyor_col.objects.link(guard)
        scene = bpy.context.scene
        if scene and scene.collection:
            try:
                scene.collection.objects.unlink(guard)
            except Exception:
                pass

    print("✓ Added invisible side guards to prevent parts falling off")


def verify_enhancements() -> None:
    """Verify all physics enhancements are applied."""
    print("\n=== Physics Enhancement Verification ===")

    # Check slats
    slats = [obj for obj in bpy.data.objects if "Slat" in obj.name]
    if slats:
        slat = slats[0]
        rb = slat.rigid_body
        if rb:
            print(f"✓ Slat friction: {rb.friction}")

    # Check parts
    lego_col = bpy.data.collections.get("lego_parts")
    if lego_col and len(lego_col.objects) > 0:
        part = list(lego_col.objects)[0]
        rb = part.rigid_body
        if rb:
            print(f"✓ Part friction: {rb.friction}")

    # Check solver
    scene = bpy.context.scene
    if scene and scene.rigidbody_world:
        print(f"✓ Solver iterations: {scene.rigidbody_world.solver_iterations}")


def main():
    """Main entry point for Blender execution."""
    print("\n=== Enhancing Conveyor Belt Physics ===\n")

    enhance_slat_physics()
    enhance_lego_part_physics()
    optimize_rigid_body_world()
    # Removed side guards as they may interfere with bucket-to-belt flow
    verify_enhancements()

    print(
        "\n✓ Physics enhancements complete. Friction increased for reliable transport."
    )


main()
