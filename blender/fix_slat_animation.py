"""
Fix conveyor slat animation by manually animating them along the belt path.

This script creates proper keyframed animation for the conveyor slats
to move along the belt, transporting LEGO parts via friction.
"""

import bpy
from mathutils import Vector


def animate_slat_manually(
    slat_name: str,
    start_x: float,
    end_x: float,
    z_height: float,
    y_pos: float = 0.0,
    frame_offset: int = 0,
) -> None:
    """Animate a single slat moving along the conveyor belt path."""
    slat = bpy.data.objects.get(slat_name)
    if not slat:
        return

    start_frame = 1
    end_frame = 100

    # Clear existing animation
    if slat.animation_data:
        slat.animation_data_clear()

    # Calculate position for this slat based on offset
    total_frames = end_frame - start_frame

    # Animate slat moving from start to end
    for frame in range(start_frame, end_frame + 1):
        # Calculate progress (0 to 1 over the animation)
        progress = (
            (frame - start_frame + frame_offset * 5) % total_frames
        ) / total_frames

        # Position along X axis (belt direction)
        x = start_x + (end_x - start_x) * progress

        # Set location
        slat.location = Vector((x, y_pos, z_height))
        slat.keyframe_insert(data_path="location", frame=frame)

    # Make animation loop
    if slat.animation_data and slat.animation_data.action:
        for fcurve in slat.animation_data.action.fcurves:
            fcurve.modifiers.new(type="CYCLES")
            for kp in fcurve.keyframe_points:
                kp.interpolation = "LINEAR"


def animate_all_slats() -> None:
    """Animate all conveyor slats to move along the belt."""
    print("\n=== Animating Conveyor Slats ===\n")

    # Get conveyor parameters
    # Belt goes from left (negative X) to right (positive X), slightly upward
    start_x = -0.2
    end_x = 0.8
    z_height = 0.09  # Slat height
    y_pos = 0.0

    # Get all slats
    slats = [obj for obj in bpy.data.objects if "Slat" in obj.name]
    slats.sort(key=lambda x: x.name)

    if not slats:
        print("❌ No slats found")
        return

    print(f"✓ Found {len(slats)} slats")
    print(f"  Animation: X from {start_x:.2f} to {end_x:.2f}")

    # Animate each slat with a different offset for staggered motion
    for i, slat in enumerate(slats):
        animate_slat_manually(
            slat.name, start_x, end_x, z_height, y_pos, frame_offset=i
        )
        print(f"  ✓ Animated {slat.name} (offset={i})")

    print(f"\n✓ Animated {len(slats)} slats for continuous transport")


def main():
    """Main entry point for Blender execution."""
    animate_all_slats()

    # Verify animation
    test_slat = bpy.data.objects.get("Conveyor_Slat_01")
    if test_slat and test_slat.animation_data:
        print("\n=== Verification ===")
        pos1 = 0.0
        pos50 = 0.0

        scene = bpy.context.scene
        if scene:
            scene.frame_set(1)
            pos1 = test_slat.location.x
            scene.frame_set(50)
            view_layer = bpy.context.view_layer
            if view_layer:
                view_layer.update()
            pos50 = test_slat.location.x

        print(f"  Slat X at frame 1: {pos1:.3f}")
        print(f"  Slat X at frame 50: {pos50:.3f}")
        print(f"  Movement: {pos50 - pos1:+.3f} units")

        if abs(pos50 - pos1) > 0.1:
            print("\n✅ Slats are now animated and moving!")
        else:
            print("\n⚠️ Slats may still not be moving properly")


main()
