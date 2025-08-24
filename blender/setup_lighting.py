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
from typing import Any


def get_or_create_collection(name: str) -> Any:
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def clear_collection_objects(col_name: str) -> None:
    col = bpy.data.collections.get(col_name)
    if not col:
        return
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def setup_world_ambient(strength: float = 0.2, color=(0.9, 0.95, 1.0)) -> None:
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    bg.inputs[1].default_value = strength
    out = nodes.new("ShaderNodeOutputWorld")
    links.new(bg.outputs[0], out.inputs[0])


def add_area_light(name: str, location: Vector, rotation: tuple[float, float, float],
                   size: float, power_watts: float, color=(1.0, 1.0, 1.0)) -> Any:
    light_data = bpy.data.lights.new(name=name, type='AREA')
    light_data.energy = power_watts
    light_data.color = color
    light_data.shape = 'SQUARE'
    light_data.size = size
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
        power_watts=800.0,
    )
    # Fill light (opposite side, softer)
    fill = add_area_light(
        name="Fill_Light",
        location=center + Vector((-0.9, 0.8, 0.9)),
        rotation=(1.3, 0.0, -2.2),
        size=1.0,
        power_watts=400.0,
        color=(0.95, 0.98, 1.0),
    )
    # Rim light (back light to add separation)
    rim = add_area_light(
        name="Rim_Light",
        location=center + Vector((0.0, -1.2, 1.3)),
        rotation=(1.5, 0.0, 0.0),
        size=0.6,
        power_watts=600.0,
    )

    for obj in (key, fill, rim):
        col.objects.link(obj)

    print("✅ Lighting setup complete")


main()
