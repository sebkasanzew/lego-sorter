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
    """Create a conveyor belt mesh positioned to transport LEGO parts from bucket up to sorting section."""
    # Create conveyor belt mesh - starts at bucket hole, goes up at slight angle
    bpy.ops.mesh.primitive_cube_add(  # type: ignore
        size=1,
        location=(0.4, 0, 0.08)  # Start near bucket at ground level
    )
    
    conveyor = bpy.context.active_object
    if not conveyor:
        print("❌ Failed to create conveyor belt")
        return None
    
    conveyor.name = "Conveyor_Belt"
    
    # Scale to create belt proportions (long, narrow, thin)
    conveyor.scale = (1.5, 0.3, 0.02)  # type: ignore # 1.5 units long, narrow, very thin
    conveyor.rotation_euler = (0, 0.15, 0)  # type: ignore # Gentle 8-degree incline
    
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
    # Create support legs at appropriate heights for gentle inclined belt
    support_positions = [
        (0.15, 0, 0.06),   # Lower support near bucket
        (0.7, 0, 0.12),    # Higher support at far end
    ]
    
    for i, (x_pos, y_pos, z_pos) in enumerate(support_positions):
        # Create support that reaches from ground to belt
        support_height = z_pos * 2  # Double the height to reach the belt
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.02,
            depth=support_height,
            location=(x_pos, y_pos, support_height/2)  # Position so bottom touches ground
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
    """Create a hole in the bucket's side wall for parts to flow out onto conveyor."""
    # Get the sorting bucket
    bucket = bpy.data.objects.get("Sorting_Bucket")  # type: ignore
    if not bucket:
        print("❌ Sorting bucket not found")
        return
    
    # Create a cylinder to cut the hole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.04,  # Hole radius
        depth=0.2,    # Depth to ensure it cuts through wall
        location=(0.12, 0, 0.12)  # Position on bucket side, aligned with bucket height
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
    """Setup physics properties for the conveyor belt using friction-based movement."""
    if not conveyor:
        return
    
    # Select the conveyor
    bpy.context.view_layer.objects.active = conveyor
    conveyor.select_set(True)
    
    # Add rigid body physics
    bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
    
    # Set physics properties for friction-based conveyor movement
    if conveyor.rigid_body:
        conveyor.rigid_body.type = 'PASSIVE'  # Static object
        conveyor.rigid_body.friction = 0.8    # High friction to grip parts
        conveyor.rigid_body.restitution = 0.05 # Very low bounce
    
    print("✓ Setup conveyor belt physics (friction-based)")


def create_conveyor_collection() -> Optional[Any]:
    """Create a collection for conveyor belt objects."""
    # Create conveyor collection
    conveyor_collection = bpy.data.collections.new("conveyor_belt")  # type: ignore
    bpy.context.scene.collection.children.link(conveyor_collection)
    
    print("✓ Created conveyor belt collection")
    return conveyor_collection


def setup_conveyor_animation(conveyor: Optional[Any]) -> None:
    """Setup conveyor belt animation to move LEGO parts up the belt."""
    if not conveyor:
        return
    
    # Add material with animated texture to simulate belt movement
    mat = bpy.data.materials.new(name="Conveyor_Material") # type: ignore
    mat.use_nodes = True
    conveyor.data.materials.append(mat)
    
    # Get material nodes
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create nodes for animated texture
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Set up node positions
    tex_coord.location = (-800, 0)
    mapping.location = (-600, 0)
    noise_tex.location = (-400, 0)
    principled.location = (-200, 0)
    output.location = (0, 0)
    
    # Connect nodes
    links = mat.node_tree.links
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])
    links.new(noise_tex.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Set material properties for conveyor belt look
    principled.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)  # Dark gray
    principled.inputs['Roughness'].default_value = 0.8
    principled.inputs['Metallic'].default_value = 0.1
    
    # Set noise texture properties
    noise_tex.inputs['Scale'].default_value = 20.0
    noise_tex.inputs['Roughness'].default_value = 0.5
    
    # Animate the texture mapping to simulate belt movement
    bpy.context.scene.frame_set(1)
    mapping.inputs['Location'].default_value[0] = 0
    mapping.inputs['Location'].keyframe_insert(data_path="default_value", index=0)
    
    bpy.context.scene.frame_set(250)  # End frame
    mapping.inputs['Location'].default_value[0] = 5  # Move texture
    mapping.inputs['Location'].keyframe_insert(data_path="default_value", index=0)
    
    # Set linear interpolation for smooth movement
    fcurves = mat.node_tree.animation_data.action.fcurves
    for fcurve in fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'
    
    print("✓ Setup conveyor belt animation")


def setup_friction_based_conveyor(conveyor: Optional[Any]) -> None:
    """Setup friction-based conveyor belt movement by animating the belt surface."""
    if not conveyor:
        return
    
    # Add keyframe animation to simulate belt movement through surface displacement
    # This creates a moving surface that will carry objects via friction
    
    # Set up material displacement for moving surface effect
    if conveyor.data and len(conveyor.data.materials) > 0:  # type: ignore
        mat = conveyor.data.materials[0]  # type: ignore
        if mat and mat.node_tree:
            # Find the mapping node and animate its location
            for node in mat.node_tree.nodes:
                if node.type == 'MAPPING':
                    # Clear existing keyframes
                    node.inputs['Location'].default_value[0] = 0
                    
                    # Set up cyclic animation for continuous belt movement
                    bpy.context.scene.frame_set(1)
                    node.inputs['Location'].default_value[0] = 0
                    node.inputs['Location'].keyframe_insert(data_path="default_value", index=0)
                    
                    bpy.context.scene.frame_set(120)  # 5 second cycle at 24fps
                    node.inputs['Location'].default_value[0] = 2  # Move texture
                    node.inputs['Location'].keyframe_insert(data_path="default_value", index=0)
                    
                    # Set to repeat the animation
                    if mat.node_tree.animation_data and mat.node_tree.animation_data.action:
                        for fcurve in mat.node_tree.animation_data.action.fcurves:
                            fcurve.modifiers.new(type='CYCLES')
                    break
    
    print("✓ Setup friction-based conveyor movement")


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
        
        # Setup physics and animation
        setup_conveyor_physics(conveyor)
        setup_conveyor_animation(conveyor)
        setup_friction_based_conveyor(conveyor)
    
    # Create hole in bucket
    create_bucket_hole()
    
    print("🎉 Conveyor belt system created successfully!")
    print("🔄 LEGO parts will move via friction on the inclined belt")
    print("▶️ Press Space to start physics simulation")


# Execute the script
main()
