"""Inspect LEGO parts physics state and bucket collider top Z.

Run via MCP to print per-part physics properties at frames 1 and 20.
"""

import bpy
from mathutils import Vector


def inspect_frame(frame: int):
    scene = bpy.context.scene
    if scene is None:
        print("No active scene; skipping inspection")
        return
    try:
        scene.frame_set(frame)
    except Exception:
        pass
    deps = bpy.context.evaluated_depsgraph_get()

    collider = bpy.data.objects.get("Sorting_Bucket_Collider")
    bucket = bpy.data.objects.get("Sorting_Bucket")
    top_z = None
    if collider:
        bbox = [collider.matrix_world @ Vector(c) for c in collider.bound_box]
        top_z = max(p.z for p in bbox)
    elif bucket:
        bbox = [bucket.matrix_world @ Vector(c) for c in bucket.bound_box]
        top_z = max(p.z for p in bbox)

    print(f"--- Frame {frame} ---")
    print(f"Bucket top Z: {top_z}")

    parts_coll = bpy.data.collections.get("lego_parts")
    if not parts_coll:
        print("No lego_parts collection")
        return

    for obj in parts_coll.objects:
        rb = obj.rigid_body
        eval_obj = obj.evaluated_get(deps)
        loc = eval_obj.location
        mass = None
        shape = None
        margin = None
        if rb is not None:
            mass = getattr(rb, "mass", None)
            shape = getattr(rb, "collision_shape", None)
            margin = getattr(rb, "collision_margin", None)
        print(
            f"{obj.name}: loc=({loc.x:.3f},{loc.y:.3f},{loc.z:.3f}), rb={bool(rb)}, mass={mass}, shape={shape}, margin={margin}"
        )


def main():
    inspect_frame(1)
    inspect_frame(20)


if __name__ == "__main__":
    main()
