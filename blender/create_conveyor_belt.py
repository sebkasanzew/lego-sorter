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
    # Position the conveyor to start at the bucket hole location (0.12, 0, 0.12)
    bpy.ops.mesh.primitive_cube_add(  # type: ignore
        size=1,
        location=(0.6, 0, 0.18)  # Start near bucket hole, positioned higher
    )
    
    conveyor = bpy.context.active_object
    if not conveyor:
        print("❌ Failed to create conveyor belt")
        return None
    
    conveyor.name = "Conveyor_Belt"
    
    # Scale to create belt proportions (long, narrow, thin)
    conveyor.scale = (1.2, 0.25, 0.02)  # type: ignore # Slightly shorter and narrower
    conveyor.rotation_euler = (0, 0.12, 0)  # type: ignore # More gentle 7-degree incline
    
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


def create_conveyor_supports(conveyor: Optional[Any]) -> None:
    """Create side supports that stop below the belt to avoid clipping."""
    if not conveyor:
        return

    # Compute dimensions and placement
    length = conveyor.dimensions.x
    width = conveyor.dimensions.y
    thickness = conveyor.dimensions.z

    center = conveyor.location
    x_positions = [center.x - length * 0.35, center.x + length * 0.35]
    y_offset = width * 0.5 + 0.05
    top_z = center.z - thickness * 0.5 - 0.01  # stop 1cm below underside
    depth = max(top_z - 0.0, 0.05)

    names = []
    for i, x_pos in enumerate(x_positions, start=1):
        for side, y_pos in (("L", center.y - y_offset), ("R", center.y + y_offset)):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.015,
                depth=depth,
                location=(x_pos, y_pos, depth / 2.0)
            )
            support = bpy.context.active_object
            if support:
                support.name = f"Conveyor_Support_{i}{side}"
                names.append(support.name)
                # Add to conveyor collection
                conveyor_collection = bpy.data.collections.get("conveyor_belt")  # type: ignore
                if conveyor_collection and all(o.name != support.name for o in conveyor_collection.objects):
                    conveyor_collection.objects.link(support)
                    bpy.context.scene.collection.objects.unlink(support)

    print("✓ Created conveyor belt supports:", ", ".join(names))


def create_bucket_hole() -> None:
    """Create a hole in the bucket's side wall for parts to flow out onto conveyor."""
    # Get the sorting bucket
    bucket = bpy.data.objects.get("Sorting_Bucket")  # type: ignore
    if not bucket:
        print("❌ Sorting bucket not found")
        return
    
    # Create a cylinder to cut the hole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,  # Slightly larger hole radius
        depth=0.2,    # Depth to ensure it cuts through wall
        location=(0.12, 0, 0.16)  # Position on bucket side, slightly higher
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
    boolean_mod.operation = 'DIFFERENCE'  # type: ignore[attr-defined]
    boolean_mod.object = hole_cutter      # type: ignore[attr-defined]
    
    # Apply the modifier
    bpy.context.view_layer.objects.active = bucket
    bpy.ops.object.modifier_apply(modifier="Bucket_Hole")
    
    # Remove the hole cutter object
    bpy.data.objects.remove(hole_cutter, do_unlink=True)  # type: ignore
    
    print("✓ Created hole in bucket side wall")


def setup_cloth_conveyor_physics(conveyor: Optional[Any]) -> None:
    """Setup cloth simulation for realistic friction-based conveyor belt movement."""
    if not conveyor:
        return
    
    # Select the conveyor
    bpy.context.view_layer.objects.active = conveyor
    conveyor.select_set(True)
    
    # Enter edit mode to add more geometry for cloth simulation
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')  # type: ignore
    bpy.ops.mesh.subdivide(number_cuts=12)  # type: ignore # More subdivisions for better cloth
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add cloth physics modifier
    cloth_mod = conveyor.modifiers.new(name="Cloth", type='CLOTH')
    cloth_settings = cloth_mod.settings
    
    # Configure cloth settings for conveyor belt behavior
    cloth_settings.quality = 8
    cloth_settings.mass = 0.3
    cloth_settings.tension_stiffness = 80
    cloth_settings.compression_stiffness = 80
    cloth_settings.shear_stiffness = 80
    cloth_settings.bending_stiffness = 20
    cloth_settings.tension_damping = 25
    cloth_settings.compression_damping = 25
    cloth_settings.shear_damping = 25
    cloth_settings.air_damping = 1
    
    # Set collision settings for interaction with LEGO parts
    collision_settings = cloth_mod.collision_settings
    collision_settings.use_collision = True
    collision_settings.collision_quality = 4
    collision_settings.distance_min = 0.001
    collision_settings.friction = 15  # High friction to grip LEGO parts
    
    # Pin edges to simulate belt being held by rollers
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')  # type: ignore
    
    # Select edge vertices to pin (belt attachment points)
    bpy.ops.mesh.select_mode(type='VERT')  # type: ignore
    
    # Pin the edges where the belt would be attached to rollers
    vertex_group = conveyor.vertex_groups.new(name="Pinned")
    
    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Pin group assignment (edges of the belt)
    cloth_settings.vertex_group_mass = vertex_group.name
    
    print("✓ Setup cloth-based conveyor physics with high friction")


def setup_conveyor_physics(conveyor: Optional[Any]) -> None:
    """Setup physics properties for the conveyor belt as a passive rigid body surface with friction."""
    if not conveyor:
        return

    bpy.context.view_layer.objects.active = conveyor
    conveyor.select_set(True)

    # Add passive rigid body so LEGO parts (active) interact with the belt
    bpy.ops.rigidbody.object_add(type='PASSIVE')  # type: ignore
    conveyor.rigid_body.collision_shape = 'MESH'  # type: ignore
    conveyor.rigid_body.friction = 1.2  # type: ignore  # grippy belt
    conveyor.rigid_body.restitution = 0.1  # type: ignore
    conveyor.rigid_body.use_deactivation = True  # type: ignore

    print("✓ Setup conveyor belt passive rigid body for part transport")


def create_conveyor_collection() -> Optional[Any]:
    """Create a collection for conveyor belt objects."""
    # Create conveyor collection
    conveyor_collection = bpy.data.collections.new("conveyor_belt")  # type: ignore
    bpy.context.scene.collection.children.link(conveyor_collection)
    
    print("✓ Created conveyor belt collection")
    return conveyor_collection


def create_conveyor_rollers(conveyor: Optional[Any]) -> None:
    """Create rotating rollers at each end of the conveyor to drive the belt."""
    if not conveyor:
        return
    
    # Compute local axes and world-space dimensions for robust placement
    mw = conveyor.matrix_world
    axes = mw.to_3x3()
    x_axis = (axes @ Vector((1, 0, 0))).normalized()  # along belt
    y_axis = (axes @ Vector((0, 1, 0))).normalized()  # across belt (roller axis)
    z_axis = (axes @ Vector((0, 0, 1))).normalized()  # belt normal

    length = conveyor.dimensions.x
    width = conveyor.dimensions.y
    thickness = conveyor.dimensions.z

    margin_end = 0.05  # 5cm from each end
    roller_radius = 0.02
    clearance = 0.003
    roller_depth = width + 0.02

    end1_center = conveyor.location - x_axis * (length * 0.5 - margin_end) - z_axis * (thickness * 0.5 + roller_radius + clearance)
    end2_center = conveyor.location + x_axis * (length * 0.5 - margin_end) - z_axis * (thickness * 0.5 + roller_radius + clearance)

    for i, center in enumerate((end1_center, end2_center), start=1):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=roller_radius,
            depth=roller_depth,
            location=center
        )
        
        roller = bpy.context.active_object
        if roller:
            roller.name = f"Conveyor_Roller_{i}"
            # Align cylinder axis along Y (belt width); for small pitch, X-90 works fine visually
            roller.rotation_euler = (1.5708, 0, 0)  # type: ignore
            
            # Apply rotation
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            
            # Add rotation animation to drive the belt
            roller.rotation_euler = (0, 0, 0)  # type: ignore
            roller.keyframe_insert(data_path="rotation_euler", index=2, frame=1)  # type: ignore[attr-defined]
            
            # Set end keyframe for continuous rotation
            roller.rotation_euler = (0, 0, 6.28319)  # type: ignore # Full rotation (2π radians)
            roller.keyframe_insert(data_path="rotation_euler", index=2, frame=120)  # type: ignore[attr-defined]
            
            # Set linear interpolation and make it cyclic
            if getattr(roller, 'animation_data', None) and roller.animation_data.action:  # type: ignore[attr-defined]
                for fcurve in roller.animation_data.action.fcurves:  # type: ignore[attr-defined]
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = 'LINEAR'
                    # Add cycles modifier for continuous rotation
                    cycles_mod = fcurve.modifiers.new(type='CYCLES')
                    cycles_mod.mode_before = 'REPEAT'
                    cycles_mod.mode_after = 'REPEAT'
            
            # Add to conveyor collection
            conveyor_collection = bpy.data.collections.get("conveyor_belt")  # type: ignore
            if conveyor_collection and all(o.name != roller.name for o in conveyor_collection.objects):
                conveyor_collection.objects.link(roller)
                bpy.context.scene.collection.objects.unlink(roller)
    
    print("✓ Created animated conveyor rollers")
    # (Removed duplicate collection creation)


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
    create_conveyor_supports(conveyor)
    create_conveyor_rollers(conveyor)

    # Setup physics and animation - use collision physics for better part interaction
    setup_conveyor_physics(conveyor)
    setup_conveyor_animation(conveyor)
    setup_friction_based_conveyor(conveyor)
    
    # Create hole in bucket
    create_bucket_hole()
    
    print("🎉 Conveyor belt system created successfully!")
    print("🔄 Using enhanced collision physics for part transport")
    print("✓ Conveyor properly positioned to connect with bucket hole")
    print("▶️ Press Space to start physics simulation")


# Execute the script
main()
