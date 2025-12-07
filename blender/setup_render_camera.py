"""
Setup Render Camera and Scene Lighting

Creates a render camera positioned to frame the entire LEGO sorter scene,
sets up pleasant studio lighting, and configures materials.

Run this after creating the bucket and conveyor to prepare for rendering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

import bpy
from mathutils import Vector

if TYPE_CHECKING:
    from bpy.types import Material, Object


def create_render_camera() -> Optional["Object"]:
    """Create render camera at position that frames the whole scene."""
    # Remove existing render camera if present
    old_cam = bpy.data.objects.get("Render_Camera")
    if old_cam:
        bpy.data.objects.remove(old_cam, do_unlink=True)

    # Create new camera
    cam_data = bpy.data.cameras.new(name="Render_Camera")
    cam_data.lens = 35  # Wide angle to capture full scene

    cam_obj = bpy.data.objects.new("Render_Camera", cam_data)

    collection = bpy.context.collection
    if collection is None:
        print("❌ No active collection")
        return None
    collection.objects.link(cam_obj)

    # Position camera to frame entire scene
    cam_obj.location = (0.2, -0.8, 0.9)

    # Point at scene center
    target = Vector((0.2, 0.15, 0.1))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()

    # Set as active scene camera
    scene = bpy.context.scene
    if scene is not None:
        scene.camera = cam_obj

    print(f"✅ Created Render_Camera at {cam_obj.location[:]}")
    return cam_obj


def setup_studio_lighting() -> None:
    """Create three-point studio lighting."""
    # Remove existing studio lights
    for obj in list(bpy.data.objects):
        if obj.type == "LIGHT" and obj.name in ["Key_Light", "Fill_Light", "Rim_Light"]:
            bpy.data.objects.remove(obj, do_unlink=True)

    collection = bpy.context.collection
    if collection is None:
        print("❌ No active collection for lights")
        return

    # Key light - warm main light
    key_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    if hasattr(key_data, "energy"):
        key_data.energy = 10  # type: ignore[attr-defined]
    if hasattr(key_data, "color"):
        key_data.color = (1.0, 0.95, 0.9)  # type: ignore[attr-defined]
    if hasattr(key_data, "size"):
        key_data.size = 1.0  # type: ignore[attr-defined]
    key_light = bpy.data.objects.new("Key_Light", key_data)
    collection.objects.link(key_light)
    key_light.location = (0.5, -0.5, 1.2)
    key_light.rotation_euler = (0.8, 0.3, 0.2)

    # Fill light - cool softer light
    fill_data = bpy.data.lights.new(name="Fill_Light", type="AREA")
    if hasattr(fill_data, "energy"):
        fill_data.energy = 15  # type: ignore[attr-defined]
    if hasattr(fill_data, "color"):
        fill_data.color = (0.85, 0.9, 1.0)  # type: ignore[attr-defined]
    if hasattr(fill_data, "size"):
        fill_data.size = 1.5  # type: ignore[attr-defined]
    fill_light = bpy.data.objects.new("Fill_Light", fill_data)
    collection.objects.link(fill_light)
    fill_light.location = (-0.8, 0.5, 0.8)
    fill_light.rotation_euler = (1.0, -0.3, -0.5)

    # Rim light - back light for depth
    rim_data = bpy.data.lights.new(name="Rim_Light", type="SPOT")
    if hasattr(rim_data, "energy"):
        rim_data.energy = 150  # type: ignore[attr-defined]
    if hasattr(rim_data, "color"):
        rim_data.color = (1.0, 0.9, 0.8)  # type: ignore[attr-defined]
    if hasattr(rim_data, "spot_size"):
        rim_data.spot_size = 1.2  # type: ignore[attr-defined]
    rim_light = bpy.data.objects.new("Rim_Light", rim_data)
    collection.objects.link(rim_light)
    rim_light.location = (0.3, 1.0, 0.6)
    rim_light.rotation_euler = (1.8, 0, 2.5)

    print("✅ Studio lighting created (Key, Fill, Rim)")


def setup_dark_world() -> None:
    """Configure dark studio background."""
    scene = bpy.context.scene
    if scene is None:
        print("❌ No active scene")
        return

    # Remove old world
    if scene.world is not None:
        bpy.data.worlds.remove(scene.world)

    # Create dark world
    world = bpy.data.worlds.new("Dark_World")
    scene.world = world
    world.use_nodes = True

    node_tree = world.node_tree
    if node_tree is None:
        print("❌ World node tree not available")
        return

    nodes = node_tree.nodes
    links = node_tree.links
    nodes.clear()

    # Dark background
    bg = nodes.new("ShaderNodeBackground")
    color_input = bg.inputs.get("Color")
    strength_input = bg.inputs.get("Strength")
    if color_input is not None and hasattr(color_input, "default_value"):
        color_input.default_value = (0.01, 0.012, 0.015, 1.0)  # type: ignore[attr-defined]
    if strength_input is not None and hasattr(strength_input, "default_value"):
        strength_input.default_value = 0.5  # type: ignore[attr-defined]

    output = nodes.new("ShaderNodeOutputWorld")
    bg_output = bg.outputs.get("Background")
    surface_input = output.inputs.get("Surface")
    if bg_output is not None and surface_input is not None:
        links.new(bg_output, surface_input)

    print("✅ Dark world background configured")


def create_material(
    name: str,
    base_color: Tuple[float, float, float, float],
    metallic: float = 0.0,
    roughness: float = 0.5,
) -> "Material":
    """Create or update a principled BSDF material."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    node_tree = mat.node_tree
    if node_tree is None:
        return mat

    principled = None
    for node in node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            principled = node
            break
    if principled is None:
        principled = node_tree.nodes.new("ShaderNodeBsdfPrincipled")

    # Set material properties with guards
    base_color_input = principled.inputs.get("Base Color")
    metallic_input = principled.inputs.get("Metallic")
    roughness_input = principled.inputs.get("Roughness")

    if base_color_input is not None and hasattr(base_color_input, "default_value"):
        base_color_input.default_value = base_color  # type: ignore[attr-defined]
    if metallic_input is not None and hasattr(metallic_input, "default_value"):
        metallic_input.default_value = metallic  # type: ignore[attr-defined]
    if roughness_input is not None and hasattr(roughness_input, "default_value"):
        roughness_input.default_value = roughness  # type: ignore[attr-defined]

    return mat


def is_lego_part(obj: "Object") -> bool:
    """Check if object belongs to lego_parts collection (directly or via parent)."""
    # Check all collections the object belongs to
    for col in obj.users_collection:
        if col.name == "lego_parts":
            return True
    # Check parent hierarchy (LEGO parts often have child meshes)
    parent = obj.parent
    while parent is not None:
        for col in parent.users_collection:
            if col.name == "lego_parts":
                return True
        parent = parent.parent
    return False


def setup_scene_materials() -> None:
    """Apply dark materials to scene objects for better contrast with LEGO parts."""
    # Create materials - all darker for contrast
    bucket_mat = create_material(
        "Bucket_Material", (0.35, 0.35, 0.38, 1.0), metallic=0.1, roughness=0.6
    )
    conveyor_mat = create_material(
        "Conveyor_Material", (0.20, 0.20, 0.22, 1.0), metallic=0.1, roughness=0.7
    )
    slat_mat = create_material(
        "Slat_Material", (0.18, 0.18, 0.20, 1.0), metallic=0.0, roughness=0.7
    )
    ramp_mat = create_material(
        "Ramp_Material", (0.25, 0.25, 0.28, 1.0), metallic=0.1, roughness=0.6
    )
    backdrop_mat = create_material(
        "Backdrop_Material", (0.08, 0.08, 0.10, 1.0), metallic=0.0, roughness=0.95
    )

    # Apply to objects (skip LEGO parts - they have their own colors)
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue

        # Skip LEGO parts - preserve their assigned colors
        if is_lego_part(obj):
            continue

        mesh_data = obj.data
        if mesh_data is None or not hasattr(mesh_data, "materials"):
            continue

        name_lower = obj.name.lower()
        mesh_data.materials.clear()  # type: ignore[union-attr]

        if "bucket" in name_lower or "funnel" in name_lower or "floor" in name_lower:
            mesh_data.materials.append(bucket_mat)  # type: ignore[union-attr]
        elif "slat" in name_lower:
            mesh_data.materials.append(slat_mat)  # type: ignore[union-attr]
        elif (
            "conveyor" in name_lower
            or "belt" in name_lower
            or "wall" in name_lower
            or "base" in name_lower
        ):
            mesh_data.materials.append(conveyor_mat)  # type: ignore[union-attr]
        elif "ramp" in name_lower or "exit" in name_lower:
            mesh_data.materials.append(ramp_mat)  # type: ignore[union-attr]
        elif (
            "ground" in name_lower or "backdrop" in name_lower or "studio" in name_lower
        ):
            mesh_data.materials.append(backdrop_mat)  # type: ignore[union-attr]

    print("✅ Scene materials applied")


def setup_studio_backdrop() -> None:
    """Create dark studio floor and backdrop."""
    backdrop_mat = create_material(
        "Backdrop_Material", (0.03, 0.035, 0.04, 1.0), metallic=0.0, roughness=1.0
    )

    # Check for existing backdrop
    if not bpy.data.objects.get("Studio_Backdrop"):
        bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 2, 0))
        backdrop = bpy.context.active_object
        if backdrop is not None:
            backdrop.name = "Studio_Backdrop"
            backdrop.rotation_euler = (1.5708, 0, 0)
            mesh_data = backdrop.data
            if mesh_data is not None and hasattr(mesh_data, "materials"):
                mesh_data.materials.append(backdrop_mat)  # type: ignore[union-attr]

    if not bpy.data.objects.get("Studio_Floor"):
        bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, -0.05))
        floor = bpy.context.active_object
        if floor is not None:
            floor.name = "Studio_Floor"
            mesh_data = floor.data
            if mesh_data is not None and hasattr(mesh_data, "materials"):
                mesh_data.materials.append(backdrop_mat)  # type: ignore[union-attr]

    # Also darken Physics_Ground if it exists
    ground = bpy.data.objects.get("Physics_Ground")
    if ground is not None:
        mesh_data = ground.data
        if mesh_data is not None and hasattr(mesh_data, "materials"):
            mesh_data.materials.clear()  # type: ignore[union-attr]
            mesh_data.materials.append(backdrop_mat)  # type: ignore[union-attr]

    print("✅ Studio backdrop and floor created")


def configure_render_settings() -> None:
    """Configure render engine and color management."""
    scene = bpy.context.scene
    if scene is None:
        print("❌ No active scene")
        return

    # Use Eevee - use setattr to avoid type checker issues with engine literals
    render = scene.render
    if hasattr(bpy.types, "BLENDER_EEVEE_NEXT") or "BLENDER_EEVEE_NEXT" in dir(
        bpy.types
    ):
        render.engine = "BLENDER_EEVEE_NEXT"  # pyright: ignore[reportAttributeAccessIssue]
    else:
        render.engine = "BLENDER_EEVEE"

    # Ambient occlusion
    eevee = getattr(scene, "eevee", None)
    if eevee is not None:
        if hasattr(eevee, "use_gtao"):
            eevee.use_gtao = True
            eevee.gtao_distance = 0.3
        # Soft shadows
        if hasattr(eevee, "use_soft_shadows"):
            eevee.use_soft_shadows = True

    # Color management - Filmic with high contrast
    view_settings = getattr(scene, "view_settings", None)
    if view_settings is not None:
        if hasattr(view_settings, "view_transform"):
            view_settings.view_transform = "Filmic"
        if hasattr(view_settings, "look"):
            view_settings.look = "Very High Contrast"
        if hasattr(view_settings, "exposure"):
            view_settings.exposure = 0.3

    print("✅ Render settings configured (Eevee, Filmic)")


def main():
    """Main entry point - setup render camera and scene."""
    print("\n" + "=" * 50)
    print("Setting up Render Camera and Scene")
    print("=" * 50 + "\n")

    create_render_camera()
    setup_studio_lighting()
    setup_dark_world()
    setup_studio_backdrop()
    setup_scene_materials()
    configure_render_settings()

    print("\n" + "=" * 50)
    print("✅ Render setup complete!")
    print("   Press Numpad 0 to view through camera")
    print("=" * 50 + "\n")


main()
