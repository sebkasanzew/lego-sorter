#!/usr/bin/env python3
"""
Blender script to import common LEGO parts from LDraw files.

This script imports the most common LEGO parts from LDraw .dat files
and arranges them vertically in the Blender scene for sorting simulation.

Requirements:
- LDraw library installed (typically in /Applications/Studio 2.0/ldraw/parts/)
- Blender LDraw importer addon enabled

Usage:
- Run this script in Blender to import LEGO parts
- Parts will be arranged vertically with proper spacing
- All parts will be added to a 'lego_parts' collection
"""

import bpy
import os
from typing import Any, cast
from mathutils import Vector

# Set the folder path where your .dat files are stored
LDRAW_PARTS_PATH = "/Applications/Studio 2.0/ldraw/parts/"

# Most common LEGO parts with weights (higher weight = more copies imported)
# Weight defines how many copies of this part type to import
WEIGHTED_LEGO_PARTS = [
    # Very common parts (weight 8-10)
    ("3024", 10),  # 1x1 Plate - most common
    ("3023", 10),  # 1x2 Plate
    ("3022", 8),  # 2x2 Plate
    ("3020", 8),  # 2x4 Plate
    ("3005", 8),  # 1x1 Brick
    ("3004", 8),  # 1x2 Brick
    ("3003", 6),  # 2x2 Brick
    ("3001", 6),  # 2x4 Brick
    # Common parts (weight 4-5)
    ("3710", 5),  # 1x4 Plate
    ("3021", 5),  # 2x3 Plate
    ("3623", 5),  # 1x3 Plate
    ("3666", 4),  # 1x6 Plate
    ("3010", 4),  # 1x4 Brick
    ("4073", 4),  # 1x1 Plate, Round
    ("54200", 4),  # 1x1 Slope 30° (Cheese)
    # Less common parts (weight 2-3)
    ("3069b", 3),  # 1x2 Tile
    ("3070b", 3),  # 1x1 Tile
    ("98138", 2),  # 1x1 Tile, Round
    ("2780", 2),  # Technic Pin
    ("3039", 2),  # 2x2 Slope 45
    ("3040", 2),  # 2x1 Slope 45
    # Additional parts (weight 1)
    ("3622", 1),  # 1x3 Brick
    ("3009", 1),  # 1x6 Brick
    ("3700", 1),  # Technic Brick 1x2
    ("6632", 1),  # Technic Pin Long with Friction Ridges
    ("32000", 1),  # Technic Brick 1x2 with Axle Hole
    ("30236", 1),  # 1x2 Plate with clip
    ("3062", 1),  # 1x1 round brick
    ("3009pb02", 1),  # Brick 1 x 6 with Stone Brick Pattern
    ("2458", 1),  # 1x2x5 Brick
    ("14719", 1),  # Plate 2 x 2, Corner
    ("3066", 1),  # 1x2 Brick, modified, w/ handle
    ("2450", 1),  # 3 x 3 plate corner
    ("32062", 1),  # Technic Axle 2
    ("6636", 1),  # 1x6 Tile
    ("4032", 1),  # 2x2 plate round
    ("26047", 1),  # Plate Round 1 x 1 with Bar Handle
    ("3176", 1),  # Plate Special 3 x 2 with hole
    ("6141", 1),  # Plate round 1x1
    ("4273", 1),  # Technic Pin 3/4
    ("32073", 1),  # Technic Axle 6
    ("3665", 1),  # 2x1 Slope 45
    ("2819", 1),  # Hinge Brick 1 x 2 Locking
    ("41678", 1),  # Technic Axle 3
    ("2460", 1),  # Plate, Modified 2 x 2 with Pin on Top
    ("3673", 1),  # 2x1 Brick, rounded top
    ("3937", 1),  # Hinge Brick 1 x 2
    ("11211", 1),  # 1x2 Brick modified with Studs on Sides
    ("2877", 1),  # 1 x 2 Brick, modified, masonry
    ("43857", 1),  # Panel 1 x 2 x 1, corner
    ("30363", 1),  # 1x2 Plate with Bar on End
    ("6140", 1),  # Plate round 2x2
    ("4085d", 1),  # Plate, Modified 1 x 1 with Clip Vertical
    ("99207", 1),  # Bracket 1 x 2 - 1 x 2
    ("3680", 1),  # Turntable 2 x 2
    ("2456", 1),  # Plate 2 x 6
    ("4477", 1),  # Plate 1 x 10
    ("3832", 1),  # Plate 2 x 10
    ("3002", 1),  # Brick 2 x 3
    ("3007", 1),  # Brick 2 x 8
    ("3749", 1),  # Technic Pin
    ("48336", 1),  # Plate Modified 1 x 2 with Handle on Side
    ("18654", 1),  # Plate 1x2 with 1 Stud
    ("41750", 1),  # Hinge Plate 1 x 2 with 2 Fingers On Top
    ("2540", 1),  # Plate, Modified 1 x 2 with Handle on Side
    ("32063", 1),  # Technic Axle 3 with Stud
    ("32064", 1),  # Technic Axle 4 with Stop
    ("4485", 1),  # Technic Pin without Friction Ridges
    ("32013", 1),  # Technic Axle and Pin Connector Perpendicular
    ("6536", 1),  # Technic Axle and Pin Connector
    ("92947", 1),  # Plate, Modified 2 x 2 with Rounded Bottom
    ("43722", 1),  # Bracket 1 x 2 - 1 x 4
    ("60477", 1),  # Plate, Modified 1 x 2 with Bar Handle on Side
    ("18651", 1),  # Brick Special 1 x 1 with Stud on 1 Side
    ("30057", 1),  # Brick 1 x 1 with Stud on One Side
    ("25269", 1),  # Tile Round 1 x 1 Quarter
    ("2357", 1),  # Brick Corner 1x2x2
    ("6081", 1),  # Plate, Modified 1 x 2 with Clip Horizontal
    ("4286", 1),  # Slope 33 3x1
    ("32523", 1),  # Technic Beam 3
    ("32009", 1),  # Technic Liftarm 1 x 1
    ("42107", 1),  # Technic Beam 5
    ("15207", 1),  # Technic Beam 2
    ("4716", 1),  # Technic Pin with Friction Ridges and Slot
    ("14704", 1),  # Bracket 1 x 2 - 2 x 2
    ("42610", 1),  # Technic Pin 3/4 with Friction Ridges
    ("3794", 1),  # Plate, Modified 1 x 2 with 1 Stud
    ("2429c01", 1),  # Plate, Modified 1 x 2 with Pin Hole on Top
    ("6538", 1),  # Technic Axle and Pin Connector Angled
    ("30162", 1),  # Brick, Modified 1 x 2 with Studs on 2 Sides
]

# Total parts to import
TOTAL_PARTS_TO_IMPORT = 10


def build_import_list() -> list:
    """Build list of parts to import based on weights, totaling TOTAL_PARTS_TO_IMPORT."""
    import_list = []
    total_weight = sum(weight for _, weight in WEIGHTED_LEGO_PARTS)

    for part_id, weight in WEIGHTED_LEGO_PARTS:
        # Calculate how many copies based on weight proportion
        copies = max(1, round((weight / total_weight) * TOTAL_PARTS_TO_IMPORT))
        import_list.extend([part_id] * copies)

    # Trim or extend to exactly TOTAL_PARTS_TO_IMPORT
    if len(import_list) > TOTAL_PARTS_TO_IMPORT:
        import_list = import_list[:TOTAL_PARTS_TO_IMPORT]
    elif len(import_list) < TOTAL_PARTS_TO_IMPORT:
        # Fill remaining with most common parts
        while len(import_list) < TOTAL_PARTS_TO_IMPORT:
            import_list.append(WEIGHTED_LEGO_PARTS[0][0])

    return import_list


# Build the parts list for import (contains duplicates based on weights)
PARTS_TO_IMPORT = build_import_list()

# Classic LEGO colors (RGB values)
LEGO_COLORS = [
    (0.800, 0.067, 0.067, 1.0),  # Red
    (0.000, 0.420, 0.678, 1.0),  # Blue
    (0.980, 0.800, 0.100, 1.0),  # Yellow
    (0.133, 0.533, 0.133, 1.0),  # Green
    (1.000, 0.400, 0.000, 1.0),  # Orange
    (1.000, 1.000, 1.000, 1.0),  # White
    (0.100, 0.100, 0.100, 1.0),  # Black
    (0.600, 0.600, 0.600, 1.0),  # Light Gray
    (0.300, 0.300, 0.300, 1.0),  # Dark Gray
    (0.650, 0.165, 0.165, 1.0),  # Dark Red
    (0.000, 0.318, 0.500, 1.0),  # Dark Blue
    (0.200, 0.400, 0.200, 1.0),  # Dark Green
    (0.690, 0.537, 0.341, 1.0),  # Tan
    (0.400, 0.200, 0.067, 1.0),  # Brown
    (0.678, 0.847, 0.902, 1.0),  # Light Blue
    (0.596, 0.984, 0.596, 1.0),  # Lime Green
    (1.000, 0.753, 0.796, 1.0),  # Pink
    (0.580, 0.000, 0.827, 1.0),  # Purple
    (0.000, 0.808, 0.820, 1.0),  # Cyan/Teal
    (0.933, 0.510, 0.933, 1.0),  # Magenta
]


def create_lego_material(name: str, color: tuple) -> Any:
    """Create a plastic-like LEGO material with given color."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    node_tree = mat.node_tree
    if node_tree is None:
        return mat
    nodes = node_tree.nodes
    nodes.clear()

    # Create Principled BSDF
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    output = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf.location = (-200, 0)
    output.location = (0, 0)
    node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # Set material properties for plastic-like appearance
    base = bsdf.inputs.get("Base Color")
    if base:
        cast(Any, base).default_value = color
    rough = bsdf.inputs.get("Roughness")
    if rough:
        cast(Any, rough).default_value = 0.35  # Slightly glossy plastic
    spec = bsdf.inputs.get("Specular IOR Level")
    if spec:
        cast(Any, spec).default_value = 0.5

    return mat


def assign_random_lego_color(obj: Any, part_index: int) -> None:
    """Assign a random LEGO color material to an object and all its children."""
    import random

    # Use part_index as seed for consistent color per part
    random.seed(part_index * 7 + 13)
    color_idx = random.randint(0, len(LEGO_COLORS) - 1)
    color = LEGO_COLORS[color_idx]

    mat_name = f"LEGO_Color_{color_idx:02d}"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = create_lego_material(mat_name, color)

    # Ensure material is valid
    if mat is None:
        print(f"⚠️ Failed to create material {mat_name}")
        return

    def apply_material_to_mesh(mesh_obj: Any, material: Any) -> bool:
        """Apply material to a mesh object, replacing all existing materials."""
        if mesh_obj.type != "MESH":
            return False
        if mesh_obj.data is None:
            return False
        mesh_data = mesh_obj.data
        if not hasattr(mesh_data, "materials"):
            return False
        # Clear all existing materials and add our LEGO color
        mesh_data.materials.clear()
        mesh_data.materials.append(material)
        return True

    # Apply to this object if it's a mesh
    applied = apply_material_to_mesh(obj, mat)
    if applied:
        print(f"🎨 Applied {mat_name} to {obj.name}")

    # Apply to all children recursively (use children_recursive for deep hierarchies)
    for child in obj.children_recursive:
        if apply_material_to_mesh(child, mat):
            print(f"🎨 Applied {mat_name} to child {child.name}")


def import_lego_parts():
    """Import LEGO parts from LDraw files and arrange them vertically.

    Uses PARTS_TO_IMPORT list which contains duplicates based on part weights.
    Each entry in the list results in one part instance (original import or copy).
    """
    # Check if the folder exists
    if not os.path.exists(LDRAW_PARTS_PATH):
        print(f"❌ LDraw parts folder not found: {LDRAW_PARTS_PATH}")
        return

    # Get all .dat files in the folder
    dat_files = [f for f in os.listdir(LDRAW_PARTS_PATH) if f.endswith(".dat")]

    if not dat_files:
        print("❌ No .dat files found in the LDraw parts folder.")
        return

    # Create a mapping from part ID to .dat filename
    available_parts = {os.path.splitext(f)[0]: f for f in dat_files}

    # Filter import list to only parts that exist in the LDraw folder
    valid_parts = [p for p in PARTS_TO_IMPORT if p in available_parts]

    if not valid_parts:
        print("❌ No matching LEGO parts found in the LDraw folder.")
        return

    print(
        f"📦 Importing {len(valid_parts)} LEGO part instances (from {len(set(valid_parts))} unique types)"
    )

    z_start_offset = 0.25  # Position parts inside the bucket (bucket is at z=0.15)
    z_position = z_start_offset
    failed_files = set()

    # Create a collection for all imported parts
    collection_name = "lego_parts"
    new_collection = bpy.data.collections.new(collection_name)
    scene = bpy.context.scene
    if scene is None:
        print("❌ No active scene to link collection into; aborting")
        return

    # Prefer linking into the scene's collection when available
    if scene.collection is not None:
        try:
            scene.collection.children.link(new_collection)
        except Exception:
            # Linking can fail if collection is already linked or Blender state is odd; continue to try view layer
            pass
    else:
        # Fallback: try to link into the active layer collection (may not exist on all Blender versions)
        view_layer = bpy.context.view_layer
        if view_layer is None:
            print("❌ Could not link new collection into scene; aborting")
            return
        try:
            alc = view_layer.active_layer_collection
        except Exception:
            alc = None

        if alc is not None and getattr(alc, "collection", None) is not None:
            try:
                alc.collection.children.link(new_collection)
            except Exception:
                pass
        else:
            print("❌ Could not link new collection into scene; aborting")
            return

    imported_count = 0
    imported_part_templates = {}  # Cache of imported part objects by part_id

    for part_id in valid_parts:
        dat_file = available_parts[part_id]
        file_path = os.path.join(LDRAW_PARTS_PATH, dat_file)

        try:
            scene = bpy.context.scene
            if scene is None:
                print("❌ No active scene found; skipping import")
                failed_files.add(dat_file)
                continue

            # Check if we already imported this part type
            if part_id in imported_part_templates:
                # Duplicate existing objects
                template_objs = imported_part_templates[part_id]
                imported_objects = []
                for template_obj in template_objs:
                    new_obj = template_obj.copy()
                    if template_obj.data:
                        new_obj.data = template_obj.data.copy()
                    new_collection.objects.link(new_obj)
                    imported_objects.append(new_obj)
            else:
                # First time importing this part type - do actual import
                existing_objects = set(scene.objects)

                # Import the .dat file using the LDraw importer
                from typing import Any

                _ops_scene: Any = bpy.ops.import_scene
                import_op = None
                try:
                    import_op = _ops_scene.importldraw
                except Exception:
                    try:
                        import_op = _ops_scene.import_ldraw
                    except Exception:
                        import_op = None

                if import_op is None:
                    print(f"⚠️  LDraw import operator not found. Skipping {dat_file}.")
                    failed_files.add(dat_file)
                    continue

                try:
                    import_op(filepath=file_path)
                except Exception as e:
                    print(f"⚠️  Import operator failed for {dat_file}: {e}")
                    failed_files.add(dat_file)
                    continue

                # Identify newly imported objects
                imported_objects = [
                    obj for obj in scene.objects if obj not in existing_objects
                ]

                if not imported_objects:
                    if dat_file not in failed_files:
                        print(f"⚠️  No objects imported from {dat_file}")
                        failed_files.add(dat_file)
                    continue

                # Cache template for future duplicates
                imported_part_templates[part_id] = imported_objects

                # Move imported objects to the new collection
                for obj in imported_objects:
                    try:
                        if (
                            scene.collection is not None
                            and obj.name in scene.collection.objects
                        ):
                            try:
                                scene.collection.objects.unlink(obj)
                            except Exception:
                                pass
                    except Exception:
                        pass
                    try:
                        new_collection.objects.link(obj)
                    except Exception:
                        pass

            # Apply transformations and calculate bounding box
            min_z = float("inf")
            max_z = float("-inf")

            for obj in imported_objects:
                view_layer = bpy.context.view_layer
                if view_layer:
                    try:
                        view_layer.objects.active = obj
                    except Exception:
                        pass
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                if view_layer:
                    try:
                        view_layer.update()
                    except Exception:
                        pass

                bbox_corners = [
                    obj.matrix_world @ Vector(corner) for corner in obj.bound_box
                ]
                min_z = min(min_z, *[corner.z for corner in bbox_corners])
                max_z = max(max_z, *[corner.z for corner in bbox_corners])

            # Position the objects
            total_height = max_z - min_z
            center_z = (min_z + max_z) / 2

            # Add randomization to distribute parts inside bucket
            # Parts must spawn DIRECTLY ABOVE bucket center (X=0.02, Y=0)
            # Bucket opening is ~12cm radius, but keep spawn area small to ensure
            # all parts fall into the bucket opening
            import random

            # Bucket center is at approximately X=0.02, Y=0
            bucket_center_x = 0.02
            bucket_center_y = 0.0

            x_offset = bucket_center_x + random.uniform(
                -0.03, 0.03
            )  # Small x variation around bucket center  # noqa: S311
            y_offset = bucket_center_y + random.uniform(
                -0.03, 0.03
            )  # Small y variation around bucket center  # noqa: S311

            for obj in imported_objects:
                obj.location.x = x_offset
                obj.location.y = y_offset
                obj.location.z = z_position - center_z

            # Assign random LEGO color to imported objects
            for obj in imported_objects:
                assign_random_lego_color(obj, imported_count)

            # Update spacing for next part (smaller spacing since they're distributed)
            spacing_multiplier = 1.5
            z_position += total_height * spacing_multiplier

            # Deselect all objects
            try:
                bpy.ops.object.select_all(action="DESELECT")
            except Exception:
                pass

            imported_count += 1
            if imported_count % 10 == 0:
                print(f"✅ Imported {imported_count}/{len(valid_parts)} parts...")

        except Exception as e:
            print(f"❌ Failed to import {dat_file}: {e}")
            try:
                bpy.ops.object.select_all(action="DESELECT")
            except Exception:
                pass

    print(f"🎉 Import completed! Successfully imported {imported_count} LEGO parts")
    if failed_files:
        print(f"⚠️  Failed to import {len(failed_files)} files")


def main():
    """Main function to import LEGO parts"""
    print("🧱 Starting LEGO parts import...")

    # Import LEGO parts (scene clearing should be done separately)
    import_lego_parts()


# Always run main when script is executed
main()
