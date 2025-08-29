"""
Create realistic room lighting:
- Key, fill, rim area lights
- Soft ambient via world color and strength
- Organized under 'lighting' collection

Auto-executes main() when run.
"""

from __future__ import annotations

import bpy
from mathutils import Vector
from typing import Any, cast


def get_or_create_collection(name: str) -> Any:
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        scene = bpy.context.scene
        if scene is None:
            raise RuntimeError("No active scene found; cannot create collection")

        # Prefer linking into the scene's top-level collection when available
        if scene.collection is not None:
            try:
                scene.collection.children.link(col)
            except Exception:
                # Non-fatal: linking may fail if collection already linked
                pass
        else:
            view_layer = bpy.context.view_layer
            if view_layer is None:
                raise RuntimeError("No collection available to link new collection")
            try:
                alc = view_layer.active_layer_collection
            except Exception:
                alc = None

            if alc is not None and getattr(alc, "collection", None) is not None:
                try:
                    alc.collection.children.link(col)
                except Exception:
                    pass
            else:
                raise RuntimeError("No collection available to link new collection")
    return col


def clear_collection_objects(col_name: str) -> None:
    col = bpy.data.collections.get(col_name)
    if not col:
        return
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def setup_world_ambient(strength: float = 0.12, color=(0.9, 0.95, 1.0)) -> None:
    scene = bpy.context.scene
    if scene is None:
        raise RuntimeError("No active scene found; cannot setup world ambient")
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    if nt is None:
        return
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    bg = nodes.new("ShaderNodeBackground")
    # Guard socket access; some Blender stubs omit NodeSocket.default_value
    if bg.inputs and len(bg.inputs) >= 2:
        try:
            # cast to Any so static analyzers do not complain about `default_value`
            socket_color = cast(Any, bg.inputs[0])
            socket_color.default_value = (color[0], color[1], color[2], 1.0)
        except Exception:
            # Stubs may not show default_value but runtime typically supports it
            pass
        try:
            socket_strength = cast(Any, bg.inputs[1])
            socket_strength.default_value = float(strength)
        except Exception:
            pass
    out = nodes.new("ShaderNodeOutputWorld")
    try:
        links.new(bg.outputs[0], out.inputs[0])
    except Exception:
        pass


def add_area_light(
    name: str,
    location: Vector,
    rotation: tuple[float, float, float],
    size: float,
    power_watts: float,
    color=(1.0, 1.0, 1.0),
) -> Any:
    light_data = bpy.data.lights.new(name=name, type="AREA")
    # Some stub versions may not expose these attributes in typing; set defensively
    try:
        # cast to Any so static analyzers do not complain about unknown attributes
        cast(Any, light_data).energy = power_watts
    except Exception:
        pass
    try:
        cast(Any, light_data).color = color
    except Exception:
        pass
    try:
        cast(Any, light_data).shape = "SQUARE"
    except Exception:
        pass
    try:
        cast(Any, light_data).size = size
    except Exception:
        pass
    light_obj = bpy.data.objects.new(name, light_data)
    light_obj.location = location
    light_obj.rotation_euler = rotation
    return light_obj


def main() -> None:
    print("💡 Setting up realistic room lighting…")
    col = get_or_create_collection("lighting")
    clear_collection_objects("lighting")

    setup_world_ambient(strength=0.2, color=(0.9, 0.95, 1.0))

    # Estimate scene center and scale from known objects if available
    bucket = bpy.data.objects.get("Sorting_Bucket")
    center = Vector((0.0, 0.0, 0.2))
    if bucket:
        center = bucket.location.copy()
        center.z += 0.2

    # Key light (overhead, angled)
    key = add_area_light(
        name="Key_Light",
        location=center + Vector((0.8, -0.8, 1.2)),
        rotation=(1.2, 0.0, 0.8),
        size=0.8,
        power_watts=220.0,
    )
    # Fill light (opposite side, softer)
    fill = add_area_light(
        name="Fill_Light",
        location=center + Vector((-0.9, 0.8, 0.9)),
        rotation=(1.3, 0.0, -2.2),
        size=1.0,
        power_watts=120.0,
        color=(0.95, 0.98, 1.0),
    )
    # Rim light (back light to add separation)
    rim = add_area_light(
        name="Rim_Light",
        location=center + Vector((0.0, -1.2, 1.3)),
        rotation=(1.5, 0.0, 0.0),
        size=0.6,
        power_watts=120.0,
    )

    for obj in (key, fill, rim):
        col.objects.link(obj)

    print("✅ Lighting setup complete")


main()
