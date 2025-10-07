#!/usr/bin/env python3
"""Scene validation script for LEGO Sorter project.

This script checks if the Blender scene is in the expected state after
running the simulation pipeline. It verifies that all required collections,
objects, and physics components exist and are properly configured.

Usage:
    # Via MCP
    from utils.blender_mcp_client import BlenderMCPClient
    client = BlenderMCPClient()
    client.execute_script_file('utils/validate_scene.py', 'Validate Scene')

    # Or directly in Blender
    import bpy
    exec(open('utils/validate_scene.py').read())

Returns:
    List of validation issues (empty if scene is valid)
"""

try:
    import bpy
    from typing import Any, Dict, List, Tuple
except ImportError:
    # Allow importing outside Blender for type checking
    # Type ignore: Fallback definition when bpy unavailable - see docs/TYPE_IGNORE_GUIDE.md
    bpy = None  # type: ignore[assignment]


def validate_collections() -> List[str]:
    """Verify required collections exist."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []
    required_collections = ["bucket", "conveyor_belt", "lego_parts"]

    for col_name in required_collections:
        col = bpy.data.collections.get(col_name)
        if not col:
            issues.append(f"Missing collection: '{col_name}'")
        elif len(col.objects) == 0:
            issues.append(f"Collection '{col_name}' is empty (no objects)")

    return issues


def validate_physics_world() -> List[str]:
    """Verify physics simulation is set up."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []
    scene = bpy.context.scene
    # Type narrowing: scene is guaranteed to exist in normal Blender runtime
    assert scene is not None, "Scene must exist"  # noqa: S101

    if scene.rigidbody_world is None:
        issues.append("No rigidbody world in scene (physics not initialized)")
    else:
        rbw = scene.rigidbody_world
        # Check reasonable physics settings
        if rbw.point_cache is None:
            issues.append("Rigidbody world missing point cache")

        # Verify substeps are reasonable (should be 5-20)
        if rbw.substeps_per_frame < 5:
            issues.append(
                f"Rigidbody substeps too low: {rbw.substeps_per_frame} "
                f"(recommended: 10+)"
            )

        # Verify solver iterations (should be 10+)
        if rbw.solver_iterations < 10:
            issues.append(
                f"Rigidbody solver iterations too low: {rbw.solver_iterations} "
                f"(recommended: 10+)"
            )

    return issues


def validate_bucket() -> List[str]:
    """Verify sorting bucket exists and is configured correctly."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []

    bucket_col = bpy.data.collections.get("bucket")
    if not bucket_col:
        issues.append("Bucket collection missing (run create_sorting_bucket.py)")
        return issues

    # Check for main bucket objects
    bucket_cylinder = None
    bucket_base = None

    for obj in bucket_col.objects:
        if "bucket" in obj.name.lower() and "cylinder" in obj.name.lower():
            bucket_cylinder = obj
        elif "bucket" in obj.name.lower() and "base" in obj.name.lower():
            bucket_base = obj

    if not bucket_cylinder:
        issues.append("Bucket cylinder not found in bucket collection")

    if not bucket_base:
        issues.append("Bucket base not found in bucket collection")

    # Verify bucket has physics (should be PASSIVE)
    if bucket_base and bucket_base.rigid_body:
        if bucket_base.rigid_body.type != "PASSIVE":
            issues.append(
                f"Bucket base should be PASSIVE rigidbody, "
                f"found: {bucket_base.rigid_body.type}"
            )
    elif bucket_base:
        issues.append("Bucket base missing rigidbody physics")

    return issues


def validate_conveyor() -> List[str]:
    """Verify conveyor belt exists and is configured correctly."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []

    conveyor_col = bpy.data.collections.get("conveyor_belt")
    if not conveyor_col:
        issues.append(
            "Conveyor belt collection missing (run create_conveyor_belt.py or use SKIP_CONVEYOR=1)"
        )
        return issues

    # Check for main conveyor object
    conveyor_belt = bpy.data.objects.get("Conveyor_Belt")
    if not conveyor_belt:
        issues.append("Conveyor_Belt object not found in scene")
    else:
        # Verify conveyor has reasonable position (should be elevated)
        if conveyor_belt.location.z < 0.1:
            issues.append(
                f"Conveyor belt Z position too low: {conveyor_belt.location.z:.3f} "
                f"(should be > 0.1)"
            )

        # Verify conveyor has physics
        if not conveyor_belt.rigid_body:
            issues.append("Conveyor belt missing rigidbody physics")
        elif conveyor_belt.rigid_body.type != "PASSIVE":
            issues.append(
                f"Conveyor belt should be PASSIVE rigidbody, "
                f"found: {conveyor_belt.rigid_body.type}"
            )

    return issues


def validate_lego_parts() -> List[str]:
    """Verify LEGO parts are imported and configured correctly."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []

    parts_col = bpy.data.collections.get("lego_parts")
    if not parts_col:
        issues.append("LEGO parts collection missing (run import_lego_parts.py)")
        return issues

    part_count = len(parts_col.objects)
    if part_count == 0:
        issues.append("No LEGO parts in collection (import may have failed)")
    elif part_count < 5:
        issues.append(f"Only {part_count} LEGO parts imported (expected 5+ parts)")

    # Check first few parts for proper configuration
    parts_to_check = min(5, part_count)
    for obj in list(parts_col.objects)[:parts_to_check]:
        # Verify physics
        if not obj.rigid_body:
            issues.append(f"LEGO part '{obj.name}' missing rigidbody physics")
        else:
            # Verify ACTIVE type
            if obj.rigid_body.type != "ACTIVE":
                issues.append(
                    f"LEGO part '{obj.name}' should be ACTIVE rigidbody, "
                    f"found: {obj.rigid_body.type}"
                )

            # Verify reasonable mass (LEGO bricks are ~2g = 0.002 kg)
            if obj.rigid_body.mass < 0.0001 or obj.rigid_body.mass > 0.1:
                issues.append(
                    f"LEGO part '{obj.name}' has unrealistic mass: "
                    f"{obj.rigid_body.mass:.6f} kg (expected ~0.002 kg)"
                )

    return issues


def validate_camera() -> List[str]:
    """Verify camera is properly set up for rendering."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []

    # Check for specific camera
    camera = bpy.data.objects.get("SorterCam")
    if not camera:
        issues.append("SorterCam not found (run setup_lighting.py)")
    elif camera.type != "CAMERA":
        issues.append(f"SorterCam is {camera.type}, should be CAMERA")

    # Check for any camera at all
    cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]
    if len(cameras) == 0:
        issues.append("No cameras in scene")

    return issues


def validate_lighting() -> List[str]:
    """Verify lighting setup is adequate for rendering."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []

    lights = [obj for obj in bpy.data.objects if obj.type == "LIGHT"]
    if len(lights) == 0:
        issues.append("No lights in scene (run setup_lighting.py)")
    elif len(lights) < 2:
        issues.append("Only one light in scene (recommend at least 2-3 lights)")

    return issues


def validate_timeline() -> List[str]:
    """Verify timeline is properly configured for animation."""
    if bpy is None:
        return ["bpy module not available"]

    issues = []

    scene = bpy.context.scene
    # Type narrowing: scene is guaranteed to exist in normal Blender runtime
    assert scene is not None, "Scene must exist"  # noqa: S101

    if scene.frame_start > 1:
        issues.append(f"Frame start is {scene.frame_start}, should typically be 1")

    if scene.frame_end < 50:
        issues.append(
            f"Frame end is {scene.frame_end}, should be at least 50 for physics"
        )

    return issues


def get_scene_statistics() -> Dict[str, Any]:
    """Get statistics about the current scene."""
    if bpy is None:
        return {"error": "bpy module not available"}

    scene = bpy.context.scene
    # Type narrowing: scene is guaranteed to exist in normal Blender runtime
    assert scene is not None, "Scene must exist"  # noqa: S101

    return {
        "collections": len(bpy.data.collections),
        "objects": len(bpy.data.objects),
        "meshes": len(bpy.data.meshes),
        "materials": len(bpy.data.materials),
        "cameras": len([o for o in bpy.data.objects if o.type == "CAMERA"]),
        "lights": len([o for o in bpy.data.objects if o.type == "LIGHT"]),
        "rigidbodies": len([o for o in bpy.data.objects if o.rigid_body]),
        "frame_range": f"{scene.frame_start}-{scene.frame_end}",
    }


def validate_scene() -> Tuple[List[str], dict]:
    """Run all validation checks on the scene.

    Returns:
        Tuple of (issues_list, statistics_dict)
    """
    issues = []

    # Run all validation checks
    issues.extend(validate_collections())
    issues.extend(validate_physics_world())
    issues.extend(validate_bucket())
    issues.extend(validate_conveyor())
    issues.extend(validate_lego_parts())
    issues.extend(validate_camera())
    issues.extend(validate_lighting())
    issues.extend(validate_timeline())

    # Gather statistics
    stats = get_scene_statistics()

    return issues, stats


def main():
    """Main function for MCP execution."""
    print("\n" + "=" * 60)
    print("LEGO Sorter Scene Validation")
    print("=" * 60 + "\n")

    issues, stats = validate_scene()

    # Print statistics
    print("Scene Statistics:")
    print("-" * 40)
    for key, value in stats.items():
        print(f"  {key:20s}: {value}")
    print()

    # Print validation results
    if not issues:
        print("✅ Scene validation passed!")
        print("   All required components are present and properly configured.")
    else:
        print(f"❌ Scene validation failed with {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n💡 Tip: Run the full pipeline with 'python run_lego_sorter.py'")

    print("\n" + "=" * 60 + "\n")

    return issues


if __name__ == "__main__" or bpy is not None:
    # Auto-execute when imported via MCP or run in Blender
    if bpy is not None:
        main()
