"""Diagnostics: raycast parts at frame 20 and report hit objects and gaps.

Run via MCP: execute this script after scene setup and physics baking.
"""

import bpy
import os
from mathutils import Vector


def main():
    scene = bpy.context.scene
    if scene is None:
        print("No active scene found; aborting diagnostic")
        return
    deps = bpy.context.evaluated_depsgraph_get()

    parts_coll = bpy.data.collections.get("lego_parts")
    out_path = (
        "/Users/sebastian/Repos/private/lego-sorter/renders/diagnostic_frame20.csv"
    )
    # ensure directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w") as fh:
        fh.write("PART_NAME,TOP_Z,HIT_OBJECT,GAP_m\n")

        if not parts_coll:
            fh.write("NO_PARTS,0,None,\n")
            print(f"Wrote diagnostic to {out_path} (no lego_parts collection found)")
            return

        # set frame safely
        try:
            scene.frame_set(20)
        except Exception:
            pass

        for obj in parts_coll.objects:
            try:
                eval_obj = obj.evaluated_get(deps)
                # compute world-space bbox corners
                bbox = [
                    eval_obj.matrix_world @ Vector(corner)
                    for corner in eval_obj.bound_box
                ]
                max_z = max(p.z for p in bbox)
                origin = Vector(
                    (eval_obj.location.x, eval_obj.location.y, max_z + 0.01)
                )
                direction = Vector((0.0, 0.0, -1.0))

                # Use a small helper to call ray_cast with different signatures
                def _safe_ray_cast(scene_obj, depsgraph, orig, dir_vec):
                    # Try modern signature (deps, origin, direction)
                    try:
                        res = scene_obj.ray_cast(depsgraph, orig, dir_vec)
                        return res
                    except Exception:
                        pass
                    # Try older signature (origin, direction)
                    try:
                        res = scene_obj.ray_cast(orig, dir_vec)
                        return res
                    except Exception:
                        return (False, None, None, None, None, None)

                hit_res = _safe_ray_cast(scene, deps, origin, direction)
                if hit_res and isinstance(hit_res, tuple):
                    hit = bool(hit_res[0])
                    loc = hit_res[1]
                    hit_obj = hit_res[4] if len(hit_res) > 4 else None
                else:
                    hit = False
                    loc = None
                    hit_obj = None

                gap = ""
                hit_name = ""
                if hit and loc is not None:
                    gap = f"{(origin.z - loc.z):.6f}"
                    hit_name = hit_obj.name if hit_obj else ""
                fh.write(f"{obj.name},{max_z:.6f},{hit_name},{gap}\n")
            except Exception as e:
                fh.write(f"{obj.name},ERROR,,{e}\n")

    print(f"Wrote diagnostic to {out_path}")


if __name__ == "__main__":
    main()
