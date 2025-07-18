import bpy
from mathutils import Vector
from typing import Optional, Any


def clear_existing_conveyor() -> None:
    """Remove any existing conveyor belt objects and collection."""
    # Remove conveyor collection if it exists
    conveyor_collection = bpy.data.collections.get("conveyor_belt")  # type: ignore
    if conveyor_collection:
        for obj in conveyor_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)  # type: ignore
        bpy.data.collections.remove(conveyor_collection)
    
    print("✓ Cleared existing conveyor belt objects")


def create_conveyor_belt() -> Optional[Any]:
    """Create a conveyor belt mesh positioned to catch LEGO parts from the bucket."""
    # Create conveyor belt mesh
    bpy.ops.mesh.primitive_cube_add(  # type: ignore
        size=1,
        location=(0.25, 0, 0.95)  # Position next to bucket, slightly below (updated for new positioning)
    )
    
    conveyor = bpy.context.active_object
    if not conveyor:
        print("❌ Failed to create conveyor belt")
        return None
    
    conveyor.name = "Conveyor_Belt"
    
    # Scale to create belt proportions (long, narrow, thin)
    conveyor.scale = (1.5, 0.3, 0.02)  # type: ignore # 1.5 units long, 0.3 wide, very thin
    conveyor.rotation_euler = (0, 0.1, 0)  # type: ignore # Slight incline for parts to roll
    
    # Apply transforms
    bpy.ops.object.transform_apply(
        location=False, 
        rotation=True, 
        scale=True
    )
    
    print("✓ Created conveyor belt base mesh")
    return conveyor


def add_conveyor_details(conveyor: Optional[Any]) -> None:
    """Add visual details to make the conveyor look more realistic."""
    if not conveyor:
        return
    
    # Simple subdivide using operators instead of bmesh
    bpy.context.view_layer.objects.active = conveyor
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select all and subdivide
    bpy.ops.mesh.select_all(action='SELECT')  # type: ignore
    bpy.ops.mesh.subdivide(number_cuts=8)  # type: ignore
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print("✓ Added conveyor belt details")


def create_conveyor_supports() -> None:
    """Create support structures for the conveyor belt."""
    # Create support legs
    for i, x_pos in enumerate([0.0, 0.5]):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.02,
            depth=0.1,
            location=(x_pos, 0, 0.85)  # Updated for new positioning
        )
        
        support = bpy.context.active_object
        if support:
            support.name = f"Conveyor_Support_{i+1}"
            
            # Add to conveyor collection
            conveyor_collection = bpy.data.collections.get("conveyor_belt")  # type: ignore
            if conveyor_collection and support.name not in conveyor_collection.objects:
                conveyor_collection.objects.link(support)
                bpy.context.scene.collection.objects.unlink(support)
    
    print("✓ Created conveyor belt supports")


def create_bucket_hole() -> None:
    """Create a hole in the bucket's side wall for parts to flow out."""
    # Get the sorting bucket
    bucket = bpy.data.objects.get("Sorting_Bucket")  # type: ignore
    if not bucket:
        print("❌ Sorting bucket not found")
        return
    
    # Create a cylinder to cut the hole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.04,  # Hole radius
        depth=0.3,    # Depth to ensure it cuts through wall
        location=(0.11, 0, 1.02)  # Position on bucket side, slightly above bottom (updated for new positioning)
    )
    
    hole_cutter = bpy.context.active_object
    if not hole_cutter:
        print("❌ Failed to create hole cutter")
        return
    
    hole_cutter.name = "Bucket_Hole_Cutter"
    hole_cutter.rotation_euler = (0, 1.5708, 0)  # type: ignore # Rotate 90 degrees horizontally
    
    # Apply rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Select bucket and hole cutter for boolean operation
    bpy.context.view_layer.objects.active = bucket
    bucket.select_set(True)
    hole_cutter.select_set(True)
    
    # Add boolean modifier to bucket
    boolean_mod = bucket.modifiers.new(name="Bucket_Hole", type='BOOLEAN')
    boolean_mod.operation = 'DIFFERENCE'
    boolean_mod.object = hole_cutter
    
    # Apply the modifier
    bpy.context.view_layer.objects.active = bucket
    bpy.ops.object.modifier_apply(modifier="Bucket_Hole")
    
    # Remove the hole cutter object
    bpy.data.objects.remove(hole_cutter, do_unlink=True)  # type: ignore
    
    print("✓ Created hole in bucket side wall")


def setup_conveyor_physics(conveyor: Optional[Any]) -> None:
    """Setup physics properties for the conveyor belt."""
    if not conveyor:
        return
    
    # Select the conveyor
    bpy.context.view_layer.objects.active = conveyor
    conveyor.select_set(True)
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
    
    # Set physics properties
    if conveyor.rigid_body:
        conveyor.rigid_body.type = 'PASSIVE'  # Static object
        conveyor.rigid_body.friction = 0.3    # Low friction for sliding
        conveyor.rigid_body.restitution = 0.1 # Low bounce
    
    print("✓ Setup conveyor belt physics")


def create_conveyor_collection() -> Optional[Any]:
    """Create a collection for conveyor belt objects."""
    # Create conveyor collection
    conveyor_collection = bpy.data.collections.new("conveyor_belt")  # type: ignore
    bpy.context.scene.collection.children.link(conveyor_collection)
    
    print("✓ Created conveyor belt collection")
    return conveyor_collection


def main() -> None:
    """Main function to create the complete conveyor belt system."""
    print("🏗️ Creating conveyor belt system...")
    
    # Clear any existing conveyor
    clear_existing_conveyor()
    
    # Create collection
    conveyor_collection = create_conveyor_collection()
    
    # Create the main conveyor belt
    conveyor = create_conveyor_belt()
    
    if conveyor and conveyor_collection:
        # Move conveyor to collection
        conveyor_collection.objects.link(conveyor)
        bpy.context.scene.collection.objects.unlink(conveyor)
        
        # Add details and supports
        add_conveyor_details(conveyor)
        create_conveyor_supports()
        
        # Setup physics
        setup_conveyor_physics(conveyor)
    
    # Create hole in bucket
    create_bucket_hole()
    
    print("🎉 Conveyor belt system created successfully!")
    print("🔄 LEGO parts should now flow from bucket onto conveyor belt")


# Execute the script
main()
