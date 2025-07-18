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

def setup_physics_world() -> None:
    """Configure the physics world settings for realistic LEGO simulation"""
    scene = bpy.context.scene
    
    # Enable physics simulation
    scene.frame_set(1)
    
    # Ensure rigid body world exists
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()  # type: ignore
    
    # Set up gravity (standard Earth gravity: -9.81 m/s²)
    if hasattr(scene, 'gravity'):
        scene.gravity = (0, 0, -9.81)  # type: ignore
    
    # Set simulation quality settings using correct Blender API
    rbw = scene.rigidbody_world
    rbw.time_scale = 1.0  # type: ignore
    
    # Use correct attribute names for Blender's rigid body world
    if hasattr(rbw, 'substeps_per_frame'):
        rbw.substeps_per_frame = 10  # type: ignore
    if hasattr(rbw, 'solver_iterations'):
        rbw.solver_iterations = 10  # type: ignore
    
    print("✅ Physics world configured with realistic gravity")

def setup_bucket_physics() -> Optional[Any]:
    """Setup physics properties for the sorting bucket"""
    # Use cast to handle dynamic Blender API
    bucket = cast(Any, bpy.data.objects).get("Sorting_Bucket")
    if not bucket:
        print("❌ Sorting bucket not found. Create bucket first.")
        return None
    
    # Select the bucket
    bpy.context.view_layer.objects.active = bucket
    bucket.select_set(True)
    
    # Add rigid body physics (passive - doesn't move)
    bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
    
    # Set collision shape to mesh for accurate collision detection
    bucket.rigid_body.collision_shape = 'MESH'  # type: ignore
    bucket.rigid_body.mass = 50.0  # Heavy bucket (50kg)  # type: ignore
    bucket.rigid_body.friction = 0.8  # High friction for LEGO  # type: ignore
    bucket.rigid_body.restitution = 0.3  # Some bounce  # type: ignore
    
    print(f"✅ Physics setup for bucket: {bucket.name}")
    return bucket

def setup_lego_part_physics(obj: Any) -> None:
    """Setup physics properties for a single LEGO part"""
    if not obj:
        return
    
    # Select the object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Add rigid body physics (active - can move)
    bpy.ops.rigidbody.object_add(type='ACTIVE')  # type: ignore
    
    # Set collision shape to convex hull for better performance
    obj.rigid_body.collision_shape = 'CONVEX_HULL'  # type: ignore
    
    # Set realistic LEGO properties
    obj.rigid_body.mass = 0.002  # ~2 grams per small LEGO piece  # type: ignore
    obj.rigid_body.friction = 0.9  # High friction (LEGO is grippy)  # type: ignore
    obj.rigid_body.restitution = 0.4  # Some bounce (plastic)  # type: ignore
    
    # Set damping to prevent eternal bouncing
    obj.rigid_body.linear_damping = 0.1  # type: ignore
    obj.rigid_body.angular_damping = 0.1  # type: ignore
    
    # Enable the object for physics simulation
    obj.rigid_body.enabled = True  # type: ignore
    
    print(f"✅ Physics setup for LEGO part: {obj.name}")

def get_lego_parts() -> List[Any]:
    """Get all LEGO parts from the lego_parts collection"""
    lego_parts = []
    
    # Find the lego_parts collection using cast to handle dynamic API
    lego_collection = cast(Any, bpy.data.collections).get("lego_parts")
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
    bucket = cast(Any, bpy.data.objects).get("Sorting_Bucket")
    if not bucket:
        print("❌ No bucket found - positioning parts at default height")
        bucket_top_z = 0.5  # Default height
    else:
        # Get the bucket's top Z coordinate
        bucket_top_z = bucket.location.z + 0.5  # 50cm above bucket
    
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
        
        # Make it transparent but keep collision (use cast for dynamic properties)
        cast(Any, ground_plane).hide_render = True
        cast(Any, ground_plane).display_type = 'WIRE'
        
        # Add passive rigid body
        bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
        ground_plane.rigid_body.collision_shape = 'BOX'  # type: ignore
        ground_plane.rigid_body.friction = 0.8  # type: ignore
        ground_plane.rigid_body.restitution = 0.2  # type: ignore
        
        print("✅ Created physics ground plane")
        return ground_plane
    
    return None

def start_physics_simulation() -> None:
    """Start the physics simulation"""
    scene = bpy.context.scene
    
    # Set frame range for simulation
    scene.frame_start = 1
    scene.frame_end = 500  # ~20 seconds at 24fps
    scene.frame_set(1)
    
    # Enable rigid body world if not already enabled
    if not scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()  # type: ignore
    
    # Update the scene to ensure physics is ready
    bpy.context.view_layer.update()
    
    # Don't auto-play - let user control when to start
    print("🎬 Physics simulation ready!")
    print("💡 Press SPACE in Blender to start the simulation")
    print("🎯 Go to frame 1 and press SPACE to see parts fall")

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
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()  # type: ignore
    
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
    
    # Position parts above the bucket so they can fall
    position_parts_above_bucket(lego_parts)
    
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
