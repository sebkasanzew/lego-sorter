#!/usr/bin/env python3
"""
Blender script to create verification cameras for AI agent visual checks.

These cameras provide consistent viewpoints for verifying:
- Slat angle and overlap
- Bucket floor attachment
- Overall scene geometry

Usage:
    Run this script in Blender to add cameras to a 'verification_cameras' collection.
    Use get_camera_view() to switch viewport to a specific camera.
"""

import bpy
import math
from mathutils import Vector, Euler
from typing import Any, Optional, cast


def ensure_collection(name: str) -> Any:
    """Get or create a collection by name."""
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        scene = bpy.context.scene
        if scene and scene.collection:
            scene.collection.children.link(collection)
    return collection


def create_camera(
    name: str,
    location: tuple,
    rotation_euler: tuple,
    lens: float = 35.0,
) -> Optional[Any]:
    """Create a camera at specified location and rotation.

    Args:
        name: Camera object name
        location: (x, y, z) world position
        rotation_euler: (rx, ry, rz) rotation in radians
        lens: Focal length in mm

    Returns:
        The created camera object
    """
    # Create camera data
    cam_data = bpy.data.cameras.new(name=f"{name}_data")
    cam_data.lens = lens

    # Create camera object
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = Vector(location)
    cam_obj.rotation_euler = Euler(rotation_euler)

    return cam_obj


def setup_verification_cameras() -> list:
    """Create all verification cameras for AI agent checks.

    Camera positions:
    - Camera_Side: Side view showing slat angles and conveyor incline
    - Camera_Front: Front view showing bucket and slat width
    - Camera_Top: Top-down view showing overall layout
    - Camera_Detail_Bucket: Close-up of bucket bottom/floor

    Returns:
        List of created camera objects
    """
    # Clear existing verification cameras
    collection = bpy.data.collections.get("verification_cameras")
    if collection:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)

    # Create fresh collection
    collection = ensure_collection("verification_cameras")

    cameras = []

    # Camera 1: Side view - shows slat angles clearly
    cam_side = create_camera(
        name="Camera_Side",
        location=(0.3, -0.5, 0.15),
        rotation_euler=(math.radians(75), 0, 0),
        lens=35.0,
    )
    if cam_side:
        cameras.append(cam_side)

    # Camera 2: 3/4 view - overview of entire setup
    cam_overview = create_camera(
        name="Camera_Overview",
        location=(0.6, -0.4, 0.35),
        rotation_euler=(math.radians(60), 0, math.radians(35)),
        lens=28.0,
    )
    if cam_overview:
        cameras.append(cam_overview)

    # Camera 3: Top-down view - layout verification
    cam_top = create_camera(
        name="Camera_Top",
        location=(0.3, 0, 0.6),
        rotation_euler=(0, 0, 0),
        lens=35.0,
    )
    if cam_top:
        cameras.append(cam_top)

    # Camera 4: Bucket detail - floor attachment check
    cam_bucket = create_camera(
        name="Camera_Bucket_Detail",
        location=(0.15, -0.25, 0.05),
        rotation_euler=(math.radians(80), 0, math.radians(20)),
        lens=50.0,
    )
    if cam_bucket:
        cameras.append(cam_bucket)

    # Add all cameras to collection
    for cam in cameras:
        for coll in list(cam.users_collection):
            coll.objects.unlink(cam)
        collection.objects.link(cam)

    print(f"✅ Created {len(cameras)} verification cameras:")
    for cam in cameras:
        print(f"   - {cam.name}")

    return cameras


def set_viewport_to_camera(camera_name: str) -> bool:
    """Set the 3D viewport to look through a specific camera.

    Args:
        camera_name: Name of the camera to use

    Returns:
        True if successful, False otherwise
    """
    cam = bpy.data.objects.get(camera_name)
    if not cam or cam.type != "CAMERA":
        print(f"❌ Camera '{camera_name}' not found")
        return False

    scene = bpy.context.scene
    screen = bpy.context.screen
    if scene is None or screen is None:
        print(f"❌ No active scene or screen")
        return False

    # Set as active camera
    scene.camera = cam

    # Switch viewport to camera view
    for area in screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    # Use cast to handle type checker limitation
                    override = cast(Any, bpy.context.temp_override)(
                        area=area, region=region
                    )
                    with override:
                        bpy.ops.view3d.view_camera()
                    break
            break

    print(f"✅ Viewport set to {camera_name}")
    return True


def get_camera_screenshot(camera_name: str) -> bool:
    """Switch viewport to camera and prepare for screenshot.

    For AI agent verification workflow:
    1. Call this function to switch to camera view
    2. Use mcp_blender_get_viewport_screenshot to capture

    Args:
        camera_name: Name of verification camera

    Returns:
        True if ready for screenshot
    """
    return set_viewport_to_camera(camera_name)


def main() -> None:
    """Main function to setup verification cameras."""
    print("=" * 60)
    print("📷 Setting up Verification Cameras")
    print("=" * 60)

    _cameras = setup_verification_cameras()

    print("\n" + "=" * 60)
    print("✅ Verification cameras ready!")
    print("=" * 60)
    print("\nUsage for AI agent verification:")
    print("  1. Camera_Side - Check slat angles")
    print("  2. Camera_Overview - Check overall geometry")
    print("  3. Camera_Top - Check layout from above")
    print("  4. Camera_Bucket_Detail - Check bucket floor")
    print("\nTo switch view:")
    print("  set_viewport_to_camera('Camera_Side')")
    print("=" * 60)


# Execute
main()
