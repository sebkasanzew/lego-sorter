"""
Bake rigid body physics simulation and verify transport.

This script:
1. Clears existing physics cache
2. Bakes rigid body simulation for all frames
3. Waits for baking to complete
4. Verifies objects moved as expected

Use this to validate physics-based transport in MCP/headless mode.
"""

import bpy
import time
import math
from typing import Optional


def clear_physics_cache() -> None:
    """Clear all physics caches to ensure fresh simulation."""
    print("🧹 Clearing physics cache...")
    bpy.ops.ptcache.free_bake_all()
    print("✓ Cache cleared")


def setup_frame_range(start: int = 1, end: int = 250) -> None:
    """
    Setup frame range for simulation.

    Args:
        start: First frame to simulate
        end: Last frame to simulate
    """
    scene = bpy.context.scene
    if not scene:
        print("❌ No active scene found")
        return

    scene.frame_start = start
    scene.frame_end = end
    scene.frame_current = start

    # Configure rigid body world cache
    rbw = scene.rigidbody_world
    if rbw and rbw.point_cache:
        rbw.point_cache.frame_start = start
        rbw.point_cache.frame_end = end

    print(f"✓ Frame range: {start}-{end}")


def bake_rigid_body_physics(timeout: int = 60) -> bool:
    """
    Bake rigid body physics simulation.

    Args:
        timeout: Maximum seconds to wait for baking

    Returns:
        True if baking succeeded, False if timed out
    """
    scene = bpy.context.scene
    if not scene:
        print("❌ No active scene found")
        return False

    rbw = scene.rigidbody_world

    if not rbw:
        print("❌ No rigid body world found!")
        return False

    print(f"\n⚙️ Baking rigid body physics (timeout: {timeout}s)...")
    print(f"   Frames: {scene.frame_start} to {scene.frame_end}")
    obj_count = len(rbw.collection.objects) if rbw.collection else 0
    print(f"   Objects in simulation: {obj_count}")

    # Start baking
    scene.frame_set(scene.frame_start)

    # Use override context for baking
    override = bpy.context.copy()
    if override is None:
        print("❌ Failed to copy context")
        return False

    override["point_cache"] = rbw.point_cache

    start_time = time.time()

    try:
        # Trigger bake operation
        bpy.ops.ptcache.bake(override, bake=True)

        # Wait for bake to complete
        print("   Baking in progress", end="", flush=True)

        while not rbw.point_cache.is_baked:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                print(f"\n⚠️ Baking timed out after {timeout}s")
                return False

            # Progress indicator
            if int(elapsed) % 2 == 0:
                print(".", end="", flush=True)

            time.sleep(0.5)

        elapsed = time.time() - start_time
        print(f"\n✅ Baking completed in {elapsed:.1f}s")

        return True

    except Exception as e:
        print(f"\n❌ Baking failed: {e}")
        return False


def verify_transport(
    collection_name: str = "lego_parts",
    min_distance: float = 0.2,
    check_frame: int = 100,
) -> dict:
    """
    Verify that objects moved during simulation.

    Args:
        collection_name: Collection containing objects to check
        min_distance: Minimum distance (units) objects should move
        check_frame: Frame number to check final positions

    Returns:
        Dictionary with verification results
    """
    print(f"\n🔍 Verifying transport at frame {check_frame}...")

    scene = bpy.context.scene
    if not scene:
        print("❌ No active scene found")
        return {"success": False, "error": "No active scene"}

    col = bpy.data.collections.get(collection_name)

    if not col:
        print(f"❌ Collection '{collection_name}' not found!")
        return {"success": False, "error": "Collection not found"}

    objects = list(col.objects)
    if not objects:
        print(f"❌ No objects in collection '{collection_name}'!")
        return {"success": False, "error": "No objects"}

    results = {
        "success": False,
        "total_objects": len(objects),
        "moved_objects": 0,
        "stationary_objects": 0,
        "objects": [],
    }

    # Get initial positions (frame 1)
    scene.frame_set(1)
    initial_positions = {}
    for obj in objects:
        initial_positions[obj.name] = obj.location.copy()

    # Get final positions
    scene.frame_set(check_frame)

    print(f"\n📊 Movement analysis:")
    print(
        f"{'Object':<20} {'Start X':<8} {'End X':<8} {'Start Z':<8} {'End Z':<8} {'Distance':<10} {'Status'}"
    )
    print("-" * 90)

    for obj in objects:
        start_pos = initial_positions[obj.name]
        end_pos = obj.location.copy()

        delta_x = end_pos.x - start_pos.x
        delta_z = end_pos.z - start_pos.z
        distance = (delta_x**2 + delta_z**2) ** 0.5

        moved = distance >= min_distance
        if moved:
            results["moved_objects"] += 1
            status = "✓ MOVED"
        else:
            results["stationary_objects"] += 1
            status = "✗ STUCK"

        results["objects"].append(
            {
                "name": obj.name,
                "start": start_pos,
                "end": end_pos,
                "distance": distance,
                "moved": moved,
            }
        )

        # Print first 5 objects
        if len(results["objects"]) <= 5:
            print(
                f"{obj.name:<20} {start_pos.x:>7.3f} {end_pos.x:>7.3f} {start_pos.z:>7.3f} {end_pos.z:>7.3f} {distance:>9.3f} {status}"
            )

    if len(objects) > 5:
        print(f"... and {len(objects) - 5} more objects")

    # Calculate success
    success_rate = results["moved_objects"] / results["total_objects"]
    results["success"] = success_rate >= 0.8  # 80% should move

    print(f"\n{'=' * 90}")
    print(
        f"Summary: {results['moved_objects']}/{results['total_objects']} objects moved"
    )
    print(f"Success rate: {success_rate * 100:.1f}%")

    if results["success"]:
        print("✅ TRANSPORT VERIFIED: Objects are moving down the ramp!")
    else:
        print("❌ TRANSPORT FAILED: Objects not moving as expected")
        print(f"   Expected: ≥{min_distance:.2f} units movement")
        print(f"   Actual: {results['moved_objects']} objects moved")

    return results


def get_ramp_info() -> Optional[dict]:
    """Get information about the ramp for debugging."""
    ramp = bpy.data.objects.get("Inclined_Conveyor_Ramp")

    if not ramp:
        return None

    return {
        "location": ramp.location.copy(),
        "rotation_degrees": tuple(math.degrees(r) for r in ramp.rotation_euler),
        "dimensions": ramp.dimensions.copy(),
        "friction": ramp.rigid_body.friction if ramp.rigid_body else None,
    }


def main() -> None:
    """Main entry point for baking and verification."""
    print("\n" + "=" * 90)
    print("🎬 BAKE AND VERIFY RIGID BODY PHYSICS")
    print("=" * 90)

    # Check scene state
    scene = bpy.context.scene
    if not scene:
        print("❌ No active scene found")
        return

    rbw = scene.rigidbody_world

    if not rbw:
        print("\n❌ ERROR: No rigid body world in scene!")
        print("   Create rigid body world first")
        return

    print(f"\n📋 Scene info:")
    print(f"   Total objects: {len(bpy.data.objects)}")

    if rbw.collection:
        print(f"   Rigid body objects: {len(rbw.collection.objects)}")

        # Active/passive breakdown
        active = sum(
            1
            for obj in rbw.collection.objects
            if obj.rigid_body and obj.rigid_body.type == "ACTIVE"
        )
        passive = sum(
            1
            for obj in rbw.collection.objects
            if obj.rigid_body and obj.rigid_body.type == "PASSIVE"
        )
    else:
        print("   Rigid body objects: 0")
        active = 0
        passive = 0
    print(f"   Active bodies: {active}")
    print(f"   Passive bodies: {passive}")

    # Ramp info
    ramp_info = get_ramp_info()
    if ramp_info:
        print(f"\n🛤️ Ramp:")
        print(
            f"   Location: ({ramp_info['location'].x:.3f}, {ramp_info['location'].y:.3f}, {ramp_info['location'].z:.3f})"
        )
        print(f"   Angle: {ramp_info['rotation_degrees'][1]:.1f}°")
        print(f"   Friction: {ramp_info['friction']:.2f}")

    # Step 1: Clear cache
    clear_physics_cache()

    # Step 2: Setup frame range
    setup_frame_range(start=1, end=250)

    # Step 3: Bake physics
    bake_success = bake_rigid_body_physics(timeout=120)

    if not bake_success:
        print("\n❌ Cannot verify transport - baking failed")
        return

    # Step 4: Verify transport
    results = verify_transport(
        collection_name="lego_parts", min_distance=0.2, check_frame=100
    )

    # Step 5: Additional checks at multiple frames
    if results["success"]:
        print("\n📈 Frame-by-frame progression:")

        lego_col = bpy.data.collections.get("lego_parts")
        if lego_col and lego_col.objects:
            first_obj = list(lego_col.objects)[0]

            scene.frame_set(1)
            start_pos = first_obj.location.copy()

            for frame in [1, 50, 100, 150, 200]:
                scene.frame_set(frame)
                pos = first_obj.location.copy()
                delta_x = pos.x - start_pos.x
                delta_z = pos.z - start_pos.z
                dist = (delta_x**2 + delta_z**2) ** 0.5

                print(
                    f"   Frame {frame:3d}: X={pos.x:7.3f} Z={pos.z:7.3f} (moved {dist:.3f})"
                )

    print("\n" + "=" * 90)
    print("🏁 VERIFICATION COMPLETE")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
else:
    # Auto-execute when loaded as script
    main()
