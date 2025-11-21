"""
Position LEGO parts on the conveyor belt for proper transport.

This script moves existing LEGO parts onto the conveyor belt surface
so they can be transported by the moving slats.
"""

import bpy
from mathutils import Vector
from typing import Optional


def get_conveyor_surface_position() -> Optional[Vector]:
    """Calculate the position on the conveyor belt surface where parts should be placed."""
    # Try to get the Conveyor_Belt object first
    conveyor = bpy.data.objects.get("Conveyor_Belt")
    
    # If conveyor doesn't exist (it's deleted in create_conveyor_belt.py), use first slat
    if not conveyor:
        slats = [obj for obj in bpy.data.objects if "Slat" in obj.name]
        if slats:
            # Use first slat as reference
            slat = slats[0]
            # Start position is just in front of the first slat
            start_world = slat.location.copy()
            start_world.x -= 0.05  # Slightly before first slat
            start_world.z += 0.02  # Just above surface
            print(f"Using slat reference: {slat.name}")
            return start_world
        else:
            print("❌ No conveyor belt or slats found")
            return None
    
    # Get conveyor matrix and dimensions
    mw = conveyor.matrix_world
    length = conveyor.dimensions.x
    thickness = conveyor.dimensions.z
    
    # Position at the start of the belt, on the surface
    margin = 0.1  # Start slightly into the belt
    surface_offset = thickness * 0.5 + 0.01  # Just above surface
    
    # Local coordinates on the belt
    start_local = Vector((-length * 0.5 + margin, 0.0, surface_offset))
    
    # Transform to world space
    start_world = mw @ start_local
    
    return start_world


def position_parts_on_conveyor() -> None:
    """Move all LEGO parts to the conveyor belt surface in a grid pattern."""
    # Get LEGO parts collection
    lego_col = bpy.data.collections.get("lego_parts")
    if not lego_col:
        print("❌ LEGO parts collection not found")
        return
    
    parts = list(lego_col.objects)
    if not parts:
        print("❌ No LEGO parts found")
        return
    
    # Get starting position on conveyor
    start_pos = get_conveyor_surface_position()
    if not start_pos:
        return
    
    print(f"✓ Found {len(parts)} LEGO parts to position")
    print(f"  Start position: ({start_pos.x:.3f}, {start_pos.y:.3f}, {start_pos.z:.3f})")
    
    # Grid spacing
    spacing_x = 0.03  # Space between parts along belt
    spacing_y = 0.025  # Space between rows
    parts_per_row = 3
    
    # Position each part
    for idx, part in enumerate(parts):
        if not part or part.type != 'MESH':
            continue
        
        # Calculate grid position
        row = idx // parts_per_row
        col = idx % parts_per_row
        
        # Calculate offset from start position
        x_offset = row * spacing_x
        y_offset = (col - parts_per_row / 2) * spacing_y
        
        # Set new location
        new_loc = Vector((
            start_pos.x + x_offset,
            start_pos.y + y_offset,
            start_pos.z + 0.02  # Slightly above belt to avoid initial penetration
        ))
        
        part.location = new_loc
        
        # Reset rotation to ensure parts sit flat
        part.rotation_euler = (0, 0, 0)
        
        # Ensure rigid body is active
        if part.rigid_body:
            part.rigid_body.kinematic = False
            
        print(f"  Positioned {part.name} at ({new_loc.x:.3f}, {new_loc.y:.3f}, {new_loc.z:.3f})")
    
    print(f"✓ Positioned {len(parts)} parts on conveyor belt")


def verify_physics_setup() -> None:
    """Verify that physics is properly configured for conveyor transport."""
    print("\n=== Physics Verification ===")
    
    # Check conveyor slats
    conv_col = bpy.data.collections.get("conveyor_belt")
    if conv_col:
        slats = [obj for obj in conv_col.objects if "Slat" in obj.name]
        if slats:
            slat = slats[0]
            rb = slat.rigid_body
            if rb:
                print(f"✓ Slat physics: type={rb.type}, kinematic={rb.kinematic}, friction={rb.friction}")
            else:
                print("❌ Slat missing rigid body!")
    
    # Check LEGO parts
    lego_col = bpy.data.collections.get("lego_parts")
    if lego_col:
        parts = list(lego_col.objects)[:3]
        for part in parts:
            rb = part.rigid_body
            if rb:
                print(f"✓ {part.name}: type={rb.type}, mass={rb.mass:.4f}, friction={rb.friction}")
            else:
                print(f"❌ {part.name}: missing rigid body!")
    
    # Check rigid body world
    scene = bpy.context.scene
    if scene and scene.rigidbody_world:
        print("✓ Rigid body world exists")
    else:
        print("❌ No rigid body world!")


def main():
    """Main entry point for Blender execution."""
    print("\n=== Positioning LEGO Parts on Conveyor ===\n")
    
    position_parts_on_conveyor()
    verify_physics_setup()
    
    # Set frame to start to see initial setup
    scene = bpy.context.scene
    if scene:
        scene.frame_set(1)
    
    print("\n✓ Parts positioned on conveyor. Run simulation to test transport.")


main()
