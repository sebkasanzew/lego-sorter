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
from mathutils import Vector

# Set the folder path where your .dat files are stored
LDRAW_PARTS_PATH = "/Applications/Studio 2.0/ldraw/parts/"

# Most common LEGO parts from https://brickarchitect.com/most-common-lego-parts/
COMMON_LEGO_PARTS = [
    "4073",  # 1x1 Plate, Round
    "3023",  # 1x2 Plate
    "3024",  # 1x1 Plate
    "2780",  # Technic Pin with Friction Ridges Lengthwise and Center Slots
    "54200",  # 1x1 Slope 30° (Cheese)
    "3069b",  # 1x2 Tile
    "3710",  # 1x4 Plate
    "3005",  # 1x1 Brick
    "3020",  # 2x4 Plate
    "3022",  # 2x2 Plate
    "2412b",  # 1x2 Tile, Grille
    "6558",  # Technic Pin Long with Friction Ridges Lengthwise
    "15573",  # 1x2 Jumper
    "98138",  # 1x1 Tile, Round
    "3070b",  # 1x1 Tile
    "3021",  # 2x3 Plate
    "3003",  # 2x2 Brick
    "3666",  # 1x6 Plate
    "3623",  # 1x3 Plate
    "11477",  # 2x1 Curved
    "2431",  # 1x4 Tile
    "85984",  # 1x2 Slope 30° (Double Cheese)
    "4274",  # Technic Pin 1/2
    "3010",  # 1x4 Brick
    "3001",  # 2x4 Brick
    "3062b",  # Brick Round 1 x 1 Open Stud
    "2420",  # 2x2 Plate, Corner
    "15068",  # 2x2 Curved
    "43093",  # Technic Axle Pin with Friction Ridges Lengthwise
    "87580",  # 2x2 Jumper
    "3795",  # 2x6 Plate
    "3068b",  # 2x2 Tile
    "25269",  # Tile Round 1 x 1 Quarter
    "3004",  # 1x2 Brick
    "3008",  # 1x8 Brick
    "3705",  # Technic Axle 4
    "4865b",  # Panel 1 x 2 x 1 [Rounded Corners]
    "11458",  # Plate Special 1 x 2 with Pin Hole on Top
    "42003",  # Technic Axle and Pin Connector Perpendicular 3L with 2 Pin Holes
    "3039",  # 2x2 Slope 45
    "3040",  # 2x1 Slope 45
    "3622",  # 1x3 Brick
    "3009",  # 1x6 Brick
    "3700",  # Technic Brick 1x2
    "6632",  # Technic Pin Long with Friction Ridges
    "32000",  # Technic Brick 1x2 with Axle Hole
    "30236",  # 1x2 Plate with clip
    "3062",  # 1x1 round brick (old version, could be 3062b)
    "3009pb02",  # Brick 1 x 6 with Stone Brick Pattern
    "2458",  # 1x2x5 Brick
    "14719",  # Plate 2 x 2, Corner
    "3066",  # 1x2 Brick, modified, w/ handle
    "2450",  # 3 x 3 plate corner
    "32062",  # Technic Axle 2
    "6636",  # 1x6 Tile
    "4032",  # 2x2 plate round
    "26047",  # Plate Round 1 x 1 with Bar Handle
    "3176",  # Plate Special 3 x 2 with hole
    "6141",  # Plate round 1x1
    "4273",  # Technic Pin 3/4
    "32073",  # Technic Axle 6
    "3665",  # 2x1 Slope 45
    "2819",  # Hinge Brick 1 x 2 Locking
    "41678",  # Technic Axle 3
    "2460",  # Plate, Modified 2 x 2 with Pin on Top
    "3673",  # 2x1 Brick, rounded top
    "3937",  # Hinge Brick 1 x 2
    "11211",  # 1x2 Brick modified with Studs on Sides
    "2877",  # 1 x 2 Brick, modified, masonry
    "43857",  # Panel 1 x 2 x 1, corner
    "30363",  # 1x2 Plate with Bar on End
    "6140",  # Plate round 2x2
    "4085d",  # Plate, Modified 1 x 1 with Clip Vertical
    "99207",  # Bracket 1 x 2 - 1 x 2
    "3680",  # Turntable 2 x 2
    "2456",  # Plate 2 x 6
    "4477",  # Plate 1 x 10
    "3832",  # Plate 2 x 10
    "3002",  # Brick 2 x 3
    "3007",  # Brick 2 x 8
    "3749",  # Technic Pin
    "48336",  # Plate Modified 1 x 2 with Handle on Side
    "18654",  # Plate 1x2 with 1 Stud
    "41750",  # Hinge Plate 1 x 2 with 2 Fingers On Top
    "2540",  # Plate, Modified 1 x 2 with Handle on Side
    "32063",  # Technic Axle 3 with Stud
    "32064",  # Technic Axle 4 with Stop
    "4485",  # Technic Pin without Friction Ridges
    "32013",  # Technic Axle and Pin Connector Perpendicular
    "6536",  # Technic Axle and Pin Connector
    "92947",  # Plate, Modified 2 x 2 with Rounded Bottom
    "43722",  # Bracket 1 x 2 - 1 x 4
    "60477",  # Plate, Modified 1 x 2 with Bar Handle on Side
    "18651",  # Brick Special 1 x 1 with Stud on 1 Side
    "30057",  # Brick 1 x 1 with Stud on One Side
    "25269",  # Tile Round 1 x 1 Quarter
    "2357",  # Brick Corner 1x2x2
    "6081",  # Plate, Modified 1 x 2 with Clip Horizontal
    "4286",  # Slope 33 3x1
    "32523",  # Technic Beam 3
    "32009",  # Technic Liftarm 1 x 1
    "42107",  # Technic Beam 5
    "15207",  # Technic Beam 2
    "4716",  # Technic Pin with Friction Ridges and Slot
    "14704",  # Bracket 1 x 2 - 2 x 2
    "42610",  # Technic Pin 3/4 with Friction Ridges
    "3794",  # Plate, Modified 1 x 2 with 1 Stud
    "2429c01",  # Plate, Modified 1 x 2 with Pin Hole on Top
    "6538",  # Technic Axle and Pin Connector Angled
    "30162",  # Brick, Modified 1 x 2 with Studs on 2 Sides
]

COMMON_LEGO_PARTS_SLICE = COMMON_LEGO_PARTS[
    :10
]  # Use only the first 10 for fast import


def import_lego_parts():
    """Import LEGO parts from LDraw files and arrange them vertically"""
    # Check if the folder exists
    if not os.path.exists(LDRAW_PARTS_PATH):
        print(f"❌ LDraw parts folder not found: {LDRAW_PARTS_PATH}")
        return

    # Get all .dat files in the folder
    dat_files = [f for f in os.listdir(LDRAW_PARTS_PATH) if f.endswith(".dat")]

    if not dat_files:
        print("❌ No .dat files found in the LDraw parts folder.")
        return

    # Filter dat files based on the sliced common LEGO parts list
    filtered_dat_files = [
        f for f in dat_files if os.path.splitext(f)[0] in COMMON_LEGO_PARTS_SLICE
    ]

    # Limit to the first 100 filtered files to avoid overwhelming the scene
    filtered_dat_files = filtered_dat_files[:100]

    if not filtered_dat_files:
        print("❌ No matching LEGO parts found in the LDraw folder.")
        return

    print(f"📦 Found {len(filtered_dat_files)} LEGO parts to import")

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
    for dat_file in filtered_dat_files:
        file_path = os.path.join(LDRAW_PARTS_PATH, dat_file)

        try:
            scene = bpy.context.scene
            if scene is None:
                print("❌ No active scene found; skipping import")
                failed_files.add(dat_file)
                continue

            # Get existing objects to identify newly imported ones
            existing_objects = set(scene.objects)

            # Import the .dat file using the LDraw importer (support a couple operator names)
            # Use a local Any-typed shim to perform attribute lookup on bpy.ops.import_scene
            # This avoids using getattr(...) while keeping runtime lookup dynamic for different Blender builds.
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
                print(
                    f"⚠️  LDraw import operator not found (ensure the importer addon is enabled). Skipping {dat_file}."
                )
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
            import random

            x_offset = random.uniform(
                -0.08, 0.08
            )  # Random x position within bucket  # noqa: S311
            y_offset = random.uniform(
                -0.08, 0.08
            )  # Random y position within bucket  # noqa: S311

            for obj in imported_objects:
                obj.location.x = x_offset
                obj.location.y = y_offset
                obj.location.z = z_position - center_z

            # Update spacing for next part (smaller spacing since they're distributed)
            spacing_multiplier = 1.5
            z_position += total_height * spacing_multiplier

            # Deselect all objects
            try:
                bpy.ops.object.select_all(action="DESELECT")
            except Exception:
                pass

            imported_count += 1
            print(f"✅ Imported {dat_file} (#{imported_count})")

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
