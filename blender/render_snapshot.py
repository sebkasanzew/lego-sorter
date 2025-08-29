"""
Render a snapshot of the current Blender scene to a PNG file.

Pattern: Auto-execute main() when imported.
Conventions: Matches project's Blender script style (main() and no __main__ guard).
"""

from __future__ import annotations

import os
import math
from typing import Any, Optional, Tuple, cast
from mathutils import Vector
import bpy
from bpy_extras.object_utils import world_to_camera_view


# Config
CAMERA_LENS_MM = 50.0
PADDING = 1.02  # 1.0 = tight fit, increase for margin
OFFSET_DIR = Vector((1.0, -1.0, 0.6))  # camera offset direction
TARGET_FILL = 0.75  # target fraction of frame to fill (0..1)
MAX_DOLLY_STEPS = 8
CLOSE_FACTOR = 0.45  # final multiplier to bring camera closer (0.0-1.0)

# Absolute output path to keep artifacts inside the repo
REPO_ROOT = "/Users/sebastian/Repos/private/lego-sorter"
RENDERS_DIR = os.path.join(REPO_ROOT, "renders")
# We'll organize outputs into per-frame subfolders: frame_01, frame_05, frame_10, frame_20
OUTPUT_PATH = os.path.join(RENDERS_DIR, "snapshot.png")
MULTI_ANGLES = [
    (Vector((1.0, -1.0, 0.6)), "diag"),
    (Vector((0.0, -1.0, 0.4)), "front"),
    (Vector((1.0, 0.0, 0.8)), "side"),
    (Vector((-1.0, -0.6, 0.7)), "diag_left"),
]

# Ortho technical views: direction vectors (camera looks from) and friendly tag
ORTHO_VIEWS = [
    (Vector((0, -1, 0)), "front"),
    (Vector((0, 1, 0)), "back"),
    (Vector((-1, 0, 0)), "right"),
    (Vector((1, 0, 0)), "left"),
    (Vector((0, 0, 1)), "top"),
    (Vector((0, 0, -1)), "bottom"),
    # 30/45 style iso (normalize at runtime to appease stubs)
    (Vector((1, -1, 1)), "iso_ne"),
    (Vector((-1, -1, 1)), "iso_nw"),
    (Vector((1, 1, 1)), "iso_se"),
    (Vector((-1, 1, 1)), "iso_sw"),
]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def clear_renders_dir(root: str) -> None:
    """Safely delete PNG files inside the renders directory and its subfolders.
    Only removes files with .png extension to avoid accidental deletions.
    """
    import fnmatch

    if not os.path.exists(root):
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if fnmatch.fnmatch(name.lower(), "*.png"):
                try:
                    path = os.path.join(dirpath, name)
                    os.remove(path)
                    print(f"[render_snapshot] Removed old render: {path}")
                except Exception:
                    print(f"[render_snapshot] Failed to remove {path} (continuing)")


# Lightweight vector math helpers to avoid stub attribute issues
def _length(v: Vector) -> float:
    try:
        # Some stubs expose .length at runtime, but not in typing
        return float((v.x * v.x + v.y * v.y + v.z * v.z) ** 0.5)
    except Exception:
        return 0.0


def _normalize_vec(v: Vector) -> Vector:
    length = _length(v)
    if length <= 1e-8:
        return Vector((0.0, 0.0, 0.0))
    return Vector((v.x / length, v.y / length, v.z / length))


def _dot(a: Vector, b: Vector) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def get_or_create_camera(name: str = "SorterCam") -> Any:
    cam_obj = bpy.data.objects.get(name)
    if cam_obj and cam_obj.type == "CAMERA":
        return cam_obj

    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("No active Blender scene found; cannot create camera")
    # Link to active collection
    if scene.collection is not None:
        try:
            scene.collection.objects.link(cam_obj)
        except Exception:
            pass
    else:
        view_layer = bpy.context.view_layer
        alc = None
        if view_layer is not None:
            alc = getattr(view_layer, "active_layer_collection", None)
        if alc is not None and getattr(alc, "collection", None) is not None:
            try:
                alc.collection.objects.link(cam_obj)
            except Exception:
                pass
        else:
            raise RuntimeError("No collection available to link new camera")
    return cam_obj


def world_bounds_of_object(obj: Any) -> Tuple[Any, Any]:
    # Compute world-space AABB from object's bound_box
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_v = Vector(
        (min(c.x for c in coords), min(c.y for c in coords), min(c.z for c in coords))
    )
    max_v = Vector(
        (max(c.x for c in coords), max(c.y for c in coords), max(c.z for c in coords))
    )
    return min_v, max_v


def _collect_scene_corners() -> list[Vector]:
    scene = bpy.context.scene
    if scene is None:
        return []
    meshes = [o for o in scene.objects if o.type == "MESH"]
    corners: list[Vector] = []
    for obj in meshes:
        try:
            for corner in obj.bound_box:
                corners.append(obj.matrix_world @ Vector(corner))
        except Exception as exc:  # Log and continue on errors reading bound_box
            print(
                f"⚠️  Skipping object {getattr(obj, 'name', '<unknown>')} when collecting corners: {exc}"
            )
            continue
    return corners


def compute_scene_bounds() -> Optional[Tuple[Any, Any]]:
    scene = bpy.context.scene
    if scene is None:
        return None
    meshes = [o for o in scene.objects if o.type == "MESH"]
    if not meshes:
        return None
    min_v = None
    max_v = None
    for obj in meshes:
        try:
            ob_min, ob_max = world_bounds_of_object(obj)
        except Exception as exc:  # Log and skip objects with problematic bounds
            print(
                f"⚠️  Skipping object {getattr(obj, 'name', '<unknown>')} when computing bounds: {exc}"
            )
            continue
        if min_v is None:
            # Some stubs lack Vector.copy, so assign directly
            min_v, max_v = ob_min, ob_max
        else:
            # At this point min_v and max_v are not None
            assert min_v is not None and max_v is not None
            min_v.x = min(min_v.x, ob_min.x)
            min_v.y = min(min_v.y, ob_min.y)
            min_v.z = min(min_v.z, ob_min.z)
            max_v.x = max(max_v.x, ob_max.x)
            max_v.y = max(max_v.y, ob_max.y)
            max_v.z = max(max_v.z, ob_max.z)
    return min_v, max_v


def look_at(obj: Any, target: Any) -> None:
    # Aim object local -Z toward the target, keeping +Y as up
    direction = target - obj.location
    if direction.length == 0:
        return
    quat = direction.normalized().to_track_quat("-Z", "Y")
    obj.rotation_euler = quat.to_euler()


def position_camera_to_fit_bounds(cam: Any, bounds: Tuple[Any, Any]) -> None:
    min_v, max_v = bounds
    center = (min_v + max_v) * 0.5
    dims = max_v - min_v

    # Configure camera lens and sensor fit before computing FOV
    cam_data = cam.data
    cam_data.lens = CAMERA_LENS_MM  # mm
    try:
        cam_data.sensor_fit = "AUTO"
    except Exception:
        pass

    # Determine a conservative FOV (use smaller of angle_x/angle_y)
    angle_x = getattr(cam_data, "angle_x", None)
    angle_y = getattr(cam_data, "angle_y", None)
    if not isinstance(angle_x, (int, float)) or angle_x <= 0:
        angle_x = 0.9  # fallback ~51°
    if not isinstance(angle_y, (int, float)) or angle_y <= 0:
        angle_y = 0.9
    fov = min(angle_x, angle_y)

    max_dim = max(dims.x, dims.y, dims.z)
    distance = (max_dim * 0.5) / max(1e-4, math.tan(fov * 0.5)) * PADDING

    # Place camera on a diagonal offset, and look at center
    offset_dir = _normalize_vec(OFFSET_DIR)
    cam.location = center + offset_dir * distance
    look_at(cam, center)
    # Ensure lens value stays as configured
    cam_data.lens = CAMERA_LENS_MM

    # Improve framing by iteratively dollying-in based on projected coverage
    corners = _collect_scene_corners()
    if corners:
        for _ in range(MAX_DOLLY_STEPS):
            xs, ys = [], []
            scene = bpy.context.scene
            if scene is None:
                break
            for co in corners:
                try:
                    v = world_to_camera_view(scene, cam, co)
                except Exception as exc:  # Log and skip points not visible to camera
                    print(f"⚠️  world_to_camera_view failed for a corner point: {exc}")
                    continue
                xs.append(float(v.x))
                ys.append(float(v.y))
            if not xs or not ys:
                break
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max_x - min_x
            height = max_y - min_y
            fill = max(width, height)
            if fill >= TARGET_FILL:
                break
            # Move closer: image size ~ 1/distance, so scale distance by fill/target
            ratio = max(fill, 1e-3) / max(TARGET_FILL, 1e-3)
            step_scale = max(ratio, 0.5)  # avoid huge jumps
            distance = max(distance * step_scale, 0.05)
            cam.location = center + offset_dir * distance
            look_at(cam, center)
    # After dolly steps (or if no corners), bring camera even closer for a tighter shot
    distance *= CLOSE_FACTOR
    cam.location = center + offset_dir * distance
    look_at(cam, center)


def configure_render(output_path: str) -> None:
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("No active scene found; cannot configure render")
    ensure_dir(os.path.dirname(output_path))

    # Use Eevee Next explicitly for latest Blender versions
    try:
        cast(Any, scene.render).engine = "BLENDER_EEVEE_NEXT"
        print("[render_snapshot] Using render engine: BLENDER_EEVEE_NEXT")
    except Exception as exc:
        raise RuntimeError(
            "Failed to set render engine to BLENDER_EEVEE_NEXT. "
            "Ensure you're on a Blender version that supports Eevee Next."
        ) from exc

    if scene.camera is None:
        raise RuntimeError("No camera set in the scene; cannot render")

    # Check if the scene.camera.data is of type Camera
    if not isinstance(scene.camera.data, bpy.types.Camera):
        raise RuntimeError("Scene camera is not of type Camera")

    # Reliability tweaks
    scene.camera.data.clip_start = 0.01
    scene.camera.data.clip_end = 2000.0
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = output_path


def _project_bounds_onto_plane(dims: Vector, view_dir: Vector) -> tuple[float, float]:
    """Given AABB dims (x,y,z) and a view direction, return width/height of the
    bounding rectangle when looking along view_dir, assuming up is world +Z for
    axis-aligned views. For iso, we still approximate using components.
    """
    vx, vy, vz = abs(view_dir.x), abs(view_dir.y), abs(view_dir.z)
    # Width seen on screen approximates combination of dims orthogonal to up vector.
    # We'll use world-up=(0,0,1) and screen-up aligning with it for axis views.
    width = dims.x * (1 - vx) + dims.y * (1 - vy) + dims.z * 0.0
    height = dims.z  # with up=Z, height is Z extent
    # For pure axis views, prefer exact components
    if vx > 0.99:  # looking along +X/-X
        width = dims.y
        height = dims.z
    elif vy > 0.99:  # along Y
        width = dims.x
        height = dims.z
    elif vz > 0.99:  # along Z (top/bottom)
        width = dims.x
        height = dims.y
    return float(width), float(height)


def position_camera_orthographic(
    cam: Any,
    bounds: tuple[Any, Any],
    view_dir: Vector,
    up_hint: Optional[Vector] = None,
    pad: float = 1.05,
) -> None:
    """Place cam as orthographic technical view aimed at bounds center.
    - view_dir: direction from object toward camera (camera looks from center+view_dir)
    - up_hint: preferred up vector; defaults to world +Z with adjustments
    - pad: scale margin
    Sets cam to ORTHO and adjusts orthographic_scale to fit the bbox.
    """
    min_v, max_v = bounds
    center = (min_v + max_v) * 0.5
    dims = max_v - min_v

    # Determine up vector: avoid parallel to view_dir
    up = up_hint or Vector((0, 0, 1))
    vdir = _normalize_vec(view_dir)
    if abs(_dot(vdir, up)) > 0.99:
        up = Vector((0, 1, 0))

    # Position camera a fixed distance along view_dir
    distance = max(dims.length, 0.5) * 2.0
    vstep = _normalize_vec(view_dir)
    cam.location = center + vstep * distance
    # Aim
    look_at(cam, center)

    # Switch to ORTHO
    cam_data = cam.data
    cam_data.type = "ORTHO"

    # Compute required ortho scale from projected width/height and render aspect
    scene = bpy.context.scene
    if scene is None or getattr(scene, "render", None) is None:
        aspect = 16 / 9
    else:
        aspect = scene.render.resolution_x / max(1, scene.render.resolution_y)
    width, height = _project_bounds_onto_plane(dims, view_dir)
    # Ortho scale is camera half-width in Blender units
    half_width = 0.5 * width * pad
    half_height = 0.5 * height * pad
    # Fit based on aspect: full width must fit in half_width, height in half_height/aspect
    if aspect >= 1.0:
        scale = max(half_width, half_height * aspect)
    else:
        scale = max(half_height, half_width / aspect)
    cam_data.ortho_scale = float(scale * 2.0)


def render_once(output_path: str, offset_dir_override: Optional[Vector] = None) -> None:
    print("[render_snapshot] Starting snapshot render…")
    bounds = compute_scene_bounds()
    cam_obj = get_or_create_camera()
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("No active scene found; cannot render")
    scene.camera = cam_obj
    if bounds is None:
        cam_obj.location = Vector((0.0, -3.0, 2.0))
        look_at(cam_obj, Vector((0.0, 0.0, 0.0)))
    else:
        if offset_dir_override is not None:
            global OFFSET_DIR
            prev = OFFSET_DIR
            try:
                OFFSET_DIR = offset_dir_override
                position_camera_to_fit_bounds(cam_obj, bounds)
            finally:
                OFFSET_DIR = prev
        else:
            position_camera_to_fit_bounds(cam_obj, bounds)

    configure_render(output_path)
    bpy.ops.render.render(write_still=True)
    print(f"[render_snapshot] Render complete -> {output_path}")


def main() -> None:
    # Remove previous renders to ensure fresh outputs
    clear_renders_dir(RENDERS_DIR)
    ensure_dir(RENDERS_DIR)
    # Frames to capture
    frames = [1, 5, 10, 20]
    # Only produce orthographic technical views per requested frames
    bounds = compute_scene_bounds()
    if bounds is None:
        print("[render_snapshot] No meshes found; skipping orthographic renders")
        return

    cam_obj = get_or_create_camera()
    scene = bpy.context.scene
    if scene is None:
        print("[render_snapshot] No active scene found; aborting")
        return
    scene.camera = cam_obj

    for frame in frames:
        try:
            scene.frame_set(frame)
        except Exception:
            pass
        subdir = os.path.join(RENDERS_DIR, f"frame_{frame:02d}")
        ensure_dir(subdir)
        for view_dir, tag in ORTHO_VIEWS:
            out = os.path.join(subdir, f"snapshot_ortho_{tag}.png")
            position_camera_orthographic(cam_obj, bounds, view_dir=view_dir)
            configure_render(out)
            bpy.ops.render.render(write_still=True)
            print(f"[render_snapshot] Ortho render complete -> {out}")


# Auto-execute
main()
