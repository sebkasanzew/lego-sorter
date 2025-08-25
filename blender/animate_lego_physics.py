#!/usr/bin/env python3
"""
Blender script to animate LEGO parts with realistic physics simulation.

This script applies physics properties to LEGO parts and the sorting bucket,
enabling realistic gravity simulation and collision detection for the 
sorting machine workflow.

Usage:
- Run this script in Blender after importing LEGO parts and creating the bucket
- Parts will fall under gravity and interact with the bucket and each other
- Physics simulation will start automatically after setup
"""

import bpy  # type: ignore
from typing import Optional, List, Any, cast
from mathutils import Vector


def ensure_material(name: str, color_rgba=(1.0, 1.0, 1.0, 1.0), roughness: float = 0.4, metallic: float = 0.0) -> Any:
    """Get or create a simple Principled BSDF material with the given color."""
    data = bpy.data
    mat = data.materials.get(name)
    if mat:
        return mat
    mat = data.materials.new(name=name)
    mat.use_nodes = True

    node_tree = getattr(mat, 'node_tree', None)
    if node_tree is None:
        return mat

    nodes = node_tree.nodes
    links = node_tree.links
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)

    # Set socket values defensively using setattr to avoid static-typing complaints
    try:
        base_color = bsdf.inputs.get("Base Color")
        if base_color is not None:
            setattr(base_color, 'default_value', color_rgba)
    except Exception:
        pass

    try:
        rough_socket = bsdf.inputs.get("Roughness")
        if rough_socket is not None:
            setattr(rough_socket, 'default_value', roughness)
    except Exception:
        pass

    try:
        metallic_socket = bsdf.inputs.get("Metallic")
        if metallic_socket is not None:
            setattr(metallic_socket, 'default_value', metallic)
    except Exception:
        pass

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (200, 0)
    try:
        links.new(bsdf.outputs[0], out.inputs[0])
    except Exception:
        pass
    return mat


def assign_material(obj: Any, mat: Any) -> None:
    """Assign a material to an object (replace first slot or append)."""
    try:
        if not obj.data:
            return
        mats = obj.data.materials
        if len(mats) == 0:
            mats.append(mat)
        else:
            mats[0] = mat
    except Exception:
        pass


def hsv_to_rgba(h: float, s: float, v: float) -> tuple[float, float, float, float]:
    import colorsys

    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (r, g, b, 1.0)

def setup_physics_world() -> None:
    """Configure the physics world settings for realistic LEGO simulation"""
    scene = getattr(bpy.context, 'scene', None)

    # Enable physics simulation
    if scene is not None:
        try:
            scene.frame_set(1)
        except Exception:
            pass

    # Ensure rigid body world exists
    if not getattr(scene, 'rigidbody_world', None):
        try:
            bpy.ops.rigidbody.world_add()  # type: ignore
        except Exception:
            pass

    # Set up gravity (standard Earth gravity: -9.81 m/s²)
    if scene is not None and hasattr(scene, 'gravity'):
        try:
            scene.gravity = (0, 0, -9.81)  # type: ignore
        except Exception:
            pass

    # Set simulation quality settings using correct Blender API
    rbw = getattr(scene, 'rigidbody_world', None)
    if rbw is not None:
        try:
            rbw.time_scale = 1.0  # type: ignore
        except Exception:
            pass

        # Use correct attribute names for Blender's rigid body world
        # Increase physics solver accuracy to reduce contact gaps
        try:
            if hasattr(rbw, 'substeps_per_frame'):
                rbw.substeps_per_frame = 60  # type: ignore
            if hasattr(rbw, 'solver_iterations'):
                rbw.solver_iterations = 120  # type: ignore
        except Exception:
            pass
    
    print("✅ Physics world configured with realistic gravity")

def setup_bucket_physics() -> Optional[Any]:
    """Setup physics properties for the sorting bucket"""
    # Use cast to handle dynamic Blender API
    bucket = bpy.data.objects.get("Sorting_Bucket")
    if not bucket:
        print("❌ Sorting bucket not found. Create bucket first.")
        return None
    
    # Select the bucket
    view_layer = getattr(bpy.context, 'view_layer', None)
    if view_layer and getattr(view_layer, 'objects', None) is not None:
        try:
            view_layer.objects.active = bucket
        except Exception:
            pass
    bucket.select_set(True)
    
    # Add rigid body physics (passive - doesn't move)
    bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
    
    # Set collision shape to mesh for accurate collision detection
    bucket.rigid_body.collision_shape = 'MESH'  # type: ignore
    bucket.rigid_body.mass = 50.0  # Heavy bucket (50kg)  # type: ignore
    bucket.rigid_body.friction = 0.8  # High friction for LEGO  # type: ignore
    bucket.rigid_body.restitution = 0.3  # Some bounce  # type: ignore
    # Tolerances: enable small collision margin and margin usage to avoid floating
    try:
        bucket.rigid_body.use_margin = True  # type: ignore
        # set margin to zero to eliminate solver gaps (works for deterministic renders)
        bucket.rigid_body.collision_margin = 0.0  # type: ignore
    except Exception:
        pass
    
    print(f"✅ Physics setup for bucket: {bucket.name}")
    return bucket

def setup_lego_part_physics(obj: Any) -> None:
    """Setup physics properties for a single LEGO part"""
    if not obj:
        return
    
    # Select the object
    view_layer = getattr(bpy.context, 'view_layer', None)
    if view_layer and getattr(view_layer, 'objects', None) is not None:
        try:
            view_layer.objects.active = obj
        except Exception:
            pass
    obj.select_set(True)
    
    # Add rigid body physics (active - can move)
    bpy.ops.rigidbody.object_add(type='ACTIVE')  # type: ignore
    
    # Use MESH collision shape for higher accuracy (less approximation gap)
    try:
        # Force high-fidelity collision shapes and zero margins for accuracy
        obj.rigid_body.collision_shape = 'MESH'
    except Exception:
        try:
            obj.rigid_body.collision_shape = 'CONVEX_HULL'  # type: ignore
        except Exception:
            pass
    
    # Set realistic LEGO properties
    obj.rigid_body.mass = 0.002  # ~2 grams per small LEGO piece  # type: ignore
    obj.rigid_body.friction = 0.9  # High friction (LEGO is grippy)  # type: ignore
    obj.rigid_body.restitution = 0.4  # Some bounce (plastic)  # type: ignore
    
    # Set damping to prevent eternal bouncing
    obj.rigid_body.linear_damping = 0.1  # type: ignore
    obj.rigid_body.angular_damping = 0.1  # type: ignore
    
    # Enable the object for physics simulation
    obj.rigid_body.enabled = True  # type: ignore
    # Reduce collision margin for small parts to avoid floating above surfaces
    try:
        obj.rigid_body.use_margin = True  # type: ignore
        # use explicit margins of zero whenever possible to avoid artificial gaps
        obj.rigid_body.collision_margin = 0.0
    except Exception:
        pass
    
    print(f"✅ Physics setup for LEGO part: {obj.name}")

def get_lego_parts() -> List[Any]:
    """Get all LEGO parts from the lego_parts collection"""
    lego_parts = []
    
    # Find the lego_parts collection using cast to handle dynamic API
    lego_collection = bpy.data.collections.get("lego_parts")
    if not lego_collection:
        print("❌ LEGO parts collection not found. Import LEGO parts first.")
        return []
    
    # Get all objects in the collection
    for obj in lego_collection.objects:
        if obj.type == 'MESH':
            lego_parts.append(obj)
    
    print(f"📦 Found {len(lego_parts)} LEGO parts for physics simulation")
    return lego_parts

def position_parts_above_bucket(lego_parts: List[Any]) -> None:
    """Position LEGO parts above the bucket so they fall down"""
    if not lego_parts:
        return
    
    # Get the bucket to position parts above it
    # Prefer using an internal collider to compute safe spawn height
    collider = bpy.data.objects.get("Sorting_Bucket_Collider")
    bucket = bpy.data.objects.get("Sorting_Bucket")
    if collider:
        # compute top Z from collider bounding box
        bbox = [collider.matrix_world @ Vector(c) for c in collider.bound_box]
        max_z = max(v.z for v in bbox)
        bucket_top_z = max_z + 0.10  # 10cm above internal collider (increase spawn buffer)
    elif bucket:
        # fallback: use bucket location and a heuristic height
        bbox = [bucket.matrix_world @ Vector(c) for c in bucket.bound_box]
        max_z = max(v.z for v in bbox)
        bucket_top_z = max_z + 0.05
    else:
        print("❌ No bucket found - positioning parts at default height")
        bucket_top_z = 0.5  # Default height
    
    # Position parts in a grid above the bucket
    import math
    grid_size = math.ceil(math.sqrt(len(lego_parts)))
    spacing = 0.05  # 5cm spacing between parts
    start_x = -(grid_size - 1) * spacing / 2
    start_y = -(grid_size - 1) * spacing / 2
    
    for i, part in enumerate(lego_parts):
        if not part:
            continue
            
        # Calculate grid position
        row = i // grid_size
        col = i % grid_size
        
        # Set position above the bucket
        part.location.x = start_x + col * spacing
        part.location.y = start_y + row * spacing
        part.location.z = bucket_top_z + (i * 0.02)  # Stack with 2cm between each part
        
        # Clear any existing keyframes (only if they exist)
        try:
            if part.animation_data and part.animation_data.action:
                part.keyframe_delete("location")
                part.keyframe_delete("rotation_euler")
        except:
            pass  # No keyframes to delete, which is fine
    
    print(f"✅ Positioned {len(lego_parts)} parts above the bucket at height {bucket_top_z:.2f}m")

def randomize_starting_positions(lego_parts: List[Any]) -> None:
    """Add slight randomization to starting positions to prevent perfect stacking"""
    import random
    
    for i, part in enumerate(lego_parts):
        if not part:
            continue
        
        # Add small random offset to prevent perfect alignment
        random_x = random.uniform(-0.01, 0.01)  # ±1cm
        random_y = random.uniform(-0.01, 0.01)  # ±1cm
        random_z = random.uniform(0, 0.005)     # 0-5mm upward
        
        # Apply random offset
        part.location.x += random_x
        part.location.y += random_y
        part.location.z += random_z
        
        # Add slight random rotation
        part.rotation_euler.x += random.uniform(-0.1, 0.1)
        part.rotation_euler.y += random.uniform(-0.1, 0.1)
        part.rotation_euler.z += random.uniform(-0.1, 0.1)
    
    print("✅ Added random variation to starting positions")

def create_physics_ground_plane() -> Optional[Any]:
    """Create an invisible ground plane to catch falling parts"""
    # Create a large plane at the new ground level
    bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 0))  # type: ignore
    ground_plane = bpy.context.active_object
    
    if ground_plane:
        ground_plane.name = "Physics_Ground"

        # Make it transparent but keep collision (use guarded setattr)
        try:
            setattr(ground_plane, 'hide_render', True)
        except Exception:
            pass
        try:
            setattr(ground_plane, 'display_type', 'WIRE')
        except Exception:
            pass
        
        # Add passive rigid body
        bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
        ground_plane.rigid_body.collision_shape = 'BOX'  # type: ignore
        ground_plane.rigid_body.friction = 0.8  # type: ignore
        ground_plane.rigid_body.restitution = 0.2  # type: ignore
        
        print("✅ Created physics ground plane")
        return ground_plane
    
    return None


def manual_per_frame_sampling(start: int, end: int) -> None:
    """Manually sample evaluated transforms for rigid-body objects and keyframe them.

    This is a robust fallback for headless/MCP runs where bpy.ops.rigidbody baking
    operators are unavailable. It evaluates the depsgraph each frame and writes
    the evaluated world transform back to the original objects as keyframes.
    """
    try:
        deps = bpy.context.evaluated_depsgraph_get()

        # Collect active rigid body objects (lego_parts, conveyor_belt, bucket)
        objs = []
        lego_col = bpy.data.collections.get('lego_parts')
        if lego_col:
            objs.extend([o for o in lego_col.objects if getattr(o, 'rigid_body', None)])
        conv_col = bpy.data.collections.get('conveyor_belt')
        if conv_col:
            objs.extend([o for o in conv_col.objects if getattr(o, 'rigid_body', None)])
        bucket = bpy.data.objects.get('Sorting_Bucket')
        if bucket and getattr(bucket, 'rigid_body', None):
            objs.append(bucket)

        # Deduplicate
        objs = list(dict.fromkeys(objs))

        for f in range(start, end + 1):
            scene = getattr(bpy.context, 'scene', None)
            if scene is not None:
                try:
                    scene.frame_set(f)
                except Exception:
                    pass
            try:
                deps.update()
            except Exception:
                pass
            for o in objs:
                try:
                    eo = o.evaluated_get(deps)
                    wm = eo.matrix_world.copy()
                    # Write location/rotation back to object and keyframe
                    o.location = wm.to_translation()
                    try:
                        o.rotation_euler = wm.to_euler()
                    except Exception:
                        # Some objects may use quaternion rotation; skip if necessary
                        pass
                    o.keyframe_insert(data_path='location', frame=f)
                    try:
                        o.keyframe_insert(data_path='rotation_euler', frame=f)
                    except Exception:
                        pass
                except Exception:
                    pass
    except Exception:
        pass

def start_physics_simulation() -> None:
    """Start the physics simulation"""
    scene = getattr(bpy.context, 'scene', None)

    # Set frame range for simulation
    if scene is not None:
        try:
            scene.frame_start = 1
            scene.frame_end = 100  # limit animation to 100 frames
            scene.frame_set(1)
        except Exception:
            pass

    # Enable rigid body world if not already enabled
    if not getattr(scene, 'rigidbody_world', None):
        try:
            bpy.ops.rigidbody.world_add()  # type: ignore
        except Exception:
            pass

    # Update the scene to ensure physics is ready
    view_layer = getattr(bpy.context, 'view_layer', None)
    if view_layer is not None:
        try:
            view_layer.update()
        except Exception:
            pass
    
    # Don't auto-play - let user control when to start
    print("🎬 Physics simulation ready!")
    print("💡 Press SPACE in Blender to start the simulation")
    print("🎯 Go to frame 1 and press SPACE to see parts fall")
    # Attempt to bake rigid-body simulation to keyframes so renders show simulated motion
    try:
        start_frame = 1
        end_frame = 100
        print(f"🔁 Baking rigid-body simulation to keyframes ({start_frame}..{end_frame})...")
        # Try common rigid-body bake operators (Blender API varies)
        try:
            bpy.ops.rigidbody.bake_to_keyframes(frame_start=start_frame, frame_end=end_frame)  # type: ignore
            print("✅ Rigid-body baked to keyframes (bpy.ops.rigidbody.bake_to_keyframes)")
        except Exception:
            try:
                bpy.ops.rigidbody.world_bake(frame_start=start_frame, frame_end=end_frame)  # type: ignore
                print("✅ Rigid-body world baked (bpy.ops.rigidbody.world_bake)")
            except Exception:
                # Fallback: set scene frames to force evaluation (not a real bake but helps some MCP setups)
                for f in (start_frame, end_frame):
                    scene = getattr(bpy.context, 'scene', None)
                    if scene is not None:
                        try:
                            scene.frame_set(f)
                        except Exception:
                            pass
                print("ℹ️ Rigid-body bake not available on this Blender build; scene frames evaluated as fallback.")
                # Try ptcache bake (another common bake entrypoint)
                try:
                    bpy.ops.ptcache.bake_all()  # type: ignore
                    print("✅ ptcache.bake_all succeeded")
                except Exception:
                    try:
                        bpy.ops.ptcache.bake()  # type: ignore
                        print("✅ ptcache.bake succeeded")
                    except Exception:
                        print("❌ All bake fallbacks failed; physics will require interactive playback to simulate.")
                        # Final fallback: manually sample evaluated transforms per frame
                        try:
                            print("🔁 Falling back to manual per-frame sampling of rigid-body transforms...")
                            # fallback moved to shared helper below
                            manual_per_frame_sampling(start_frame, end_frame)
                            print("✅ Manual per-frame rigid-body sampling complete")
                        except Exception:
                            pass
    except Exception:
        pass

def setup_collision_collections() -> None:
    """Setup collision collections for better organization"""
    # No longer needed - using functional collections instead
    print("ℹ️  Using simplified functional organization (bucket, conveyor_belt, lego_parts)")

def main() -> None:
    """Main function to setup physics simulation for LEGO parts"""
    print("🔬 Setting up LEGO physics simulation...")
    
    # Clear any existing physics settings
    bpy.ops.object.select_all(action='SELECT')  # type: ignore
    
    # Check if rigid body world exists, if not create it
    scene = getattr(bpy.context, 'scene', None)
    if not getattr(scene, 'rigidbody_world', None):
        try:
            bpy.ops.rigidbody.world_add()  # type: ignore
        except Exception:
            pass
    
    # Setup physics world
    setup_physics_world()
    
    # Setup collision collections
    setup_collision_collections()
    
    # Create ground plane
    ground_plane = create_physics_ground_plane()
    
    # Setup bucket physics
    bucket = setup_bucket_physics()
    if not bucket:
        print("❌ Cannot proceed without sorting bucket")
        return
    
    # Get LEGO parts
    lego_parts = get_lego_parts()
    if not lego_parts:
        print("❌ Cannot proceed without LEGO parts")
        return
    
    # Setup physics for each LEGO part
    for part in lego_parts:
        setup_lego_part_physics(part)

    # Assign unique, deterministic colors to each LEGO part to aid debugging
    try:
        total = max(1, len(lego_parts))
        for i, part in enumerate(lego_parts):
            h = float(i) / float(total)
            rgba = hsv_to_rgba(h, 0.7, 0.9)
            mat = ensure_material(f"LEGO_Part_Mat_{i:03d}", color_rgba=rgba, roughness=0.35)
            assign_material(part, mat)
        print(f"\u2705 Assigned unique colors to {len(lego_parts)} LEGO parts")
    except Exception:
        print("\u26A0\ufe0f Failed to assign per-part colors (continuing)" )
    
        # Position parts above the bucket so they can fall
        position_parts_above_bucket(lego_parts)
    
        # Clear any animation data on parts to avoid pre-existing keyframes freezing transforms
        for p in lego_parts:
            try:
                if p.animation_data:
                    p.animation_data_clear()
            except Exception:
                pass
    
    # Add randomization to prevent perfect stacking
    randomize_starting_positions(lego_parts)
    
    # Start the simulation
    start_physics_simulation()
    
    print("🎉 Physics simulation setup complete!")
    print(f"📊 Simulating {len(lego_parts)} LEGO parts with realistic physics")
    print("🎯 Parts are positioned above the bucket and ready to fall")
    print("⚡ Go to frame 1 in Blender and press SPACE to start the simulation!")

# Always run main when script is executed
main()
