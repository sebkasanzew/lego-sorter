import bpy
from mathutils import Vector
from typing import Optional, Any, cast
from bpy.types import Object


def ensure_material(
    name: str,
    rgba: tuple[float, float, float, float],
    roughness: float = 0.6,
    metallic: float = 0.05,
) -> Any:
    """Create or fetch a simple Principled BSDF material with given color."""
    mat = bpy.data.materials.get(name)

    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        node_tree = mat.node_tree
        if node_tree is None:
            return mat
        nodes = node_tree.nodes
        links = node_tree.links
        nodes.clear()
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        out = nodes.new(type="ShaderNodeOutputMaterial")
        bsdf.location = (-200, 0)
        out.location = (0, 0)
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Update color/props
    node_tree = mat.node_tree
    if node_tree is None:
        return mat

    bsdf = node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Node sockets may not have statically-known attributes in stubs; cast to Any
        base = bsdf.inputs.get("Base Color")
        if base is not None:
            base_socket = cast(Any, base)
            base_socket.default_value = rgba

        rough = bsdf.inputs.get("Roughness")
        if rough is not None:
            rough_socket = cast(Any, rough)
            rough_socket.default_value = roughness

        met = bsdf.inputs.get("Metallic")
        if met is not None:
            met_socket = cast(Any, met)
            met_socket.default_value = metallic

    return mat


def assign_material(obj: Any, mat: Any) -> None:
    """Assign material to object as slot 0 (replace or append)."""
    if not obj or getattr(obj, "data", None) is None:
        return
    mats = obj.data.materials

    if mats and len(mats) > 0:
        mats[0] = mat
    else:
        mats.append(mat)


def clear_existing_conveyor() -> None:
    """Remove any existing conveyor belt objects and collection."""
    # Remove conveyor collection if it exists
    conveyor_collection = bpy.data.collections.get("conveyor_belt")
    if conveyor_collection:
        for obj in conveyor_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(conveyor_collection)

    print("✓ Cleared existing conveyor belt objects")


def create_conveyor_belt() -> Optional[Object]:
    """Create a conveyor belt mesh positioned to transport LEGO parts from bucket up to sorting section."""
    # Create conveyor belt mesh - starts at bucket hole, goes up at slight angle
    # Position the conveyor to start at the bucket hole location (0.12, 0, 0.12)
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0.6, 0, 0.18),  # Start near bucket hole, positioned higher
    )

    obj = bpy.context.active_object
    if obj is None or not isinstance(obj, Object):
        print("❌ Failed to create conveyor belt")
        return None
    conveyor: Object = obj

    conveyor.name = "Conveyor_Belt"

    # Scale to create belt proportions (long, narrow, thin)
    conveyor.scale = Vector((1.2, 0.25, 0.02))  # Long, narrow, thin belt body
    # Pitch the belt upward slightly (rotate around Y). Use negative pitch so the
    # belt rises away from the bucket (transport direction positive X).
    conveyor.rotation_euler = (0, -0.18, 0)  # ~-10 degrees incline

    # Apply scale but keep rotation as object-space rotation (do not bake rotation
    # into mesh yet; we'll keep rotation so computed axes are correct)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Assign dark belt material
    belt_mat = ensure_material(
        "Conveyor_Belt_Mat", (0.12, 0.12, 0.12, 1.0), roughness=0.75, metallic=0.05
    )
    assign_material(conveyor, belt_mat)

    # Reposition conveyor so its near-end aligns with the Sorting_Bucket exit.
    # Compute desired X so the conveyor start (left end) sits at the bucket hole.
    bucket = bpy.data.objects.get("Sorting_Bucket")
    margin_end = 0.06
    try:
        length = conveyor.dimensions.x
        if bucket:
            # place conveyor so start_pt.x == bucket.location.x
            conveyor.location.x = bucket.location.x + (length * 0.5 - margin_end)
            # lift slightly to match bucket outlet height
            conveyor.location.z = bucket.location.z + 0.02
    except Exception:
        pass

    print("✓ Created conveyor belt base mesh")
    return conveyor


def add_conveyor_details(conveyor: Optional[Any]) -> None:
    """Add visual details to make the conveyor look more realistic."""
    if not conveyor:
        return

    # Simple subdivide using operators instead of bmesh
    view_layer = bpy.context.view_layer
    if view_layer is not None and getattr(view_layer, "objects", None) is not None:
        try:
            view_layer.objects.active = conveyor
        except Exception:
            pass
    bpy.ops.object.mode_set(mode="EDIT")

    # Select all and subdivide
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.subdivide(number_cuts=8)

    # Return to object mode
    bpy.ops.object.mode_set(mode="OBJECT")

    print("✓ Added conveyor belt details")


def create_conveyor_supports(conveyor: Optional[Any]) -> None:
    """No-op: supports removed to focus on belt and slats."""
    return


def create_bucket_hole() -> None:
    """Create a hole in the bucket's side wall for parts to flow out onto conveyor."""
    # Get the sorting bucket
    bucket = bpy.data.objects.get("Sorting_Bucket")
    if not bucket:
        print("❌ Sorting bucket not found")
        return

    # Create a cylinder to cut the hole
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,  # Slightly larger hole radius
        depth=0.2,  # Depth to ensure it cuts through wall
        location=(0.12, 0, 0.16),  # Position on bucket side, slightly higher
    )

    hole_cutter = bpy.context.active_object
    if not hole_cutter:
        print("❌ Failed to create hole cutter")
        return

    hole_cutter.name = "Bucket_Hole_Cutter"
    hole_cutter.rotation_euler = (0, 1.5708, 0)

    # Apply rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # Select bucket and hole cutter for boolean operation
    view_layer = bpy.context.view_layer
    if view_layer is not None and getattr(view_layer, "objects", None) is not None:
        try:
            view_layer.objects.active = bucket
        except Exception:
            pass
    bucket.select_set(True)
    hole_cutter.select_set(True)

    # Add boolean modifier to bucket
    boolean_mod = bucket.modifiers.new(name="Bucket_Hole", type="BOOLEAN")
    # Modifier attributes are dynamic across Blender versions; use a weakly-typed shim
    from typing import Any as _Any

    _mod_any: _Any = boolean_mod
    try:
        _mod_any.operation = "DIFFERENCE"
    except Exception:
        pass
    try:
        _mod_any.object = hole_cutter
    except Exception:
        pass

    # Apply the modifier
    view_layer = bpy.context.view_layer
    if view_layer is not None and getattr(view_layer, "objects", None) is not None:
        try:
            view_layer.objects.active = bucket
        except Exception:
            pass
    bpy.ops.object.modifier_apply(modifier="Bucket_Hole")

    # Remove the hole cutter object
    bpy.data.objects.remove(hole_cutter, do_unlink=True)

    print("✓ Created hole in bucket side wall")


def setup_cloth_conveyor_physics(conveyor: Optional[Any]) -> None:
    """Setup cloth simulation for realistic friction-based conveyor belt movement."""
    if not conveyor:
        return

    # Select the conveyor
    view_layer = bpy.context.view_layer
    if view_layer is not None and getattr(view_layer, "objects", None) is not None:
        try:
            view_layer.objects.active = conveyor
        except Exception:
            pass
    conveyor.select_set(True)

    # Enter edit mode to add more geometry for cloth simulation
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.subdivide(number_cuts=12)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Add cloth physics modifier
    cloth_mod = conveyor.modifiers.new(name="Cloth", type="CLOTH")
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
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")

    # Select edge vertices to pin (belt attachment points)
    bpy.ops.mesh.select_mode(type="VERT")

    # Pin the edges where the belt would be attached to rollers
    vertex_group = conveyor.vertex_groups.new(name="Pinned")

    # Return to object mode
    bpy.ops.object.mode_set(mode="OBJECT")

    # Pin group assignment (edges of the belt)
    cloth_settings.vertex_group_mass = vertex_group.name

    print("✓ Setup cloth-based conveyor physics with high friction")


def setup_conveyor_physics(conveyor: Optional[Any]) -> None:
    """Setup physics properties for the conveyor belt as a passive rigid body surface with friction."""
    if not conveyor:
        return

    view_layer = bpy.context.view_layer
    if view_layer is not None and getattr(view_layer, "objects", None) is not None:
        try:
            view_layer.objects.active = conveyor
        except Exception:
            pass
    conveyor.select_set(True)

    # Add passive rigid body so LEGO parts (active) interact with the belt body
    bpy.ops.rigidbody.object_add(type="PASSIVE")
    conveyor.rigid_body.collision_shape = "MESH"
    conveyor.rigid_body.friction = 1.2
    conveyor.rigid_body.restitution = 0.05
    conveyor.rigid_body.use_deactivation = True

    # Ensure the passive collider does not move but provides base support
    conveyor.rigid_body.kinematic = False

    print("✓ Setup conveyor belt passive rigid body for part transport")


def create_conveyor_collection() -> Optional[Any]:
    """Create a collection for conveyor belt objects."""
    # Create conveyor collection
    conveyor_collection = bpy.data.collections.new("conveyor_belt")
    scene = bpy.context.scene
    if scene and getattr(scene, "collection", None) is not None:
        try:
            scene.collection.children.link(conveyor_collection)
        except Exception:
            pass

    print("✓ Created conveyor belt collection")
    return conveyor_collection


def create_conveyor_rollers(conveyor: Optional[Any]) -> None:
    """No-op: rollers removed to focus on belt and slats."""
    return


def setup_conveyor_animation(conveyor: Optional[Any]) -> None:
    """Setup simple material animation for visual belt motion (optional)."""
    if not conveyor:
        return

    # Reuse the assigned belt material; if missing, create one
    mat = None
    if conveyor.data and len(conveyor.data.materials) > 0:
        mat = conveyor.data.materials[0]
    if not mat:
        mat = ensure_material(
            "Conveyor_Belt_Mat", (0.12, 0.12, 0.12, 1.0), roughness=0.75, metallic=0.05
        )
        assign_material(conveyor, mat)

    # Get material nodes
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Create nodes for animated texture
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    mapping = nodes.new(type="ShaderNodeMapping")
    noise_tex = nodes.new(type="ShaderNodeTexNoise")
    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    output = nodes.new(type="ShaderNodeOutputMaterial")

    # Set up node positions
    tex_coord.location = (-800, 0)
    mapping.location = (-600, 0)
    noise_tex.location = (-400, 0)
    principled.location = (-200, 0)
    output.location = (0, 0)

    # Connect nodes
    links = mat.node_tree.links
    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise_tex.inputs["Vector"])
    links.new(noise_tex.outputs["Color"], principled.inputs["Base Color"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    # Set material properties for conveyor belt look
    principled.inputs["Base Color"].default_value = (
        0.12,
        0.12,
        0.12,
        1.0,
    )  # Belt dark gray
    principled.inputs["Roughness"].default_value = 0.8
    principled.inputs["Metallic"].default_value = 0.1

    # Set noise texture properties
    noise_tex.inputs["Scale"].default_value = 20.0
    noise_tex.inputs["Roughness"].default_value = 0.5

    # Animate the texture mapping to simulate belt movement
    scene = bpy.context.scene
    if scene is not None:
        try:
            scene.frame_set(1)
        except Exception:
            pass
    mapping.inputs["Location"].default_value[0] = 0
    mapping.inputs["Location"].keyframe_insert(data_path="default_value", index=0)

    scene = bpy.context.scene
    if scene is not None:
        try:
            scene.frame_set(100)  # End frame
        except Exception:
            pass
    mapping.inputs["Location"].default_value[0] = 2  # Move texture within 100 frames
    mapping.inputs["Location"].keyframe_insert(data_path="default_value", index=0)

    # Set linear interpolation for smooth movement
    anim_data = getattr(mat.node_tree, "animation_data", None)
    if anim_data and getattr(anim_data, "action", None):
        for fcurve in anim_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "LINEAR"

    print("✓ Setup conveyor belt material animation (visual)")


def setup_friction_based_conveyor(conveyor: Optional[Any]) -> None:
    """Create a path-driven belt made of animated slats that carry rigid bodies via friction."""
    if not conveyor:
        return

    scene = bpy.context.scene

    # Compute belt endpoints in world space
    mw = conveyor.matrix_world

    length = conveyor.dimensions.x
    thickness = conveyor.dimensions.z
    width = conveyor.dimensions.y

    margin_end = 0.06
    surface_offset = thickness * 0.5 + 0.004

    # compute start/end in world space using local coordinates and matrix_world
    mw = conveyor.matrix_world
    start_local = Vector((-length * 0.5 + margin_end, 0.0, surface_offset))
    end_local = Vector((length * 0.5 - margin_end, 0.0, surface_offset))
    start_pt = mw @ start_local
    end_pt = mw @ end_local

    # Create a curve path between start and end
    curve_data = bpy.data.curves.new("ConveyorPath", type="CURVE")
    curve_data.dimensions = "3D"
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(1)
    p0 = spline.bezier_points[0]
    p1 = spline.bezier_points[1]
    p0.co = start_pt
    p1.co = end_pt
    # Auto handles to keep it straight but allow smoothness
    p0.handle_left_type = p0.handle_right_type = "AUTO"
    p1.handle_left_type = p1.handle_right_type = "AUTO"

    curve_obj = bpy.data.objects.new("Conveyor_Path", curve_data)
    scene = bpy.context.scene
    if scene and getattr(scene, "collection", None) is not None:
        try:
            scene.collection.objects.link(curve_obj)
        except Exception:
            pass

    # Mark the curve as a path with evaluation time (for some Blender versions)
    curve_data.use_path = True
    curve_data.path_duration = 100  # frames baseline
    # Make the curve cyclic so the conveyor path is a loop
    if spline:
        try:
            spline.use_cyclic_u = True
        except Exception:
            pass

    # Put curve into conveyor collection
    conveyor_collection = bpy.data.collections.get("conveyor_belt")
    if conveyor_collection:
        conveyor_collection.objects.link(curve_obj)
        scene = bpy.context.scene
        if scene and getattr(scene, "collection", None) is not None:
            try:
                scene.collection.objects.unlink(curve_obj)
            except Exception:
                pass

    # Helper to create a single slat that follows the path
    def create_slat(name: str, offset_factor: float) -> Optional[Any]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=start_pt)
        slat_obj = bpy.context.active_object
        if slat_obj is None or not isinstance(slat_obj, Object):
            return None
        slat: Object = slat_obj
        slat.name = name

        # Size and orient the slat for reliable collisions
        slat_length = max(length * 0.06, 0.05)
        slat.scale = Vector(
            (slat_length, width * 0.52, max(0.01, thickness * 0.4))
        )  # give it some thickness
        slat.rotation_euler = conveyor.rotation_euler.copy()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # Material
        slat_mat = ensure_material(
            "Conveyor_Slat_Mat", (0.20, 0.40, 0.85, 1.0), roughness=0.5, metallic=0.05
        )
        assign_material(slat, slat_mat)

        # Rigid body: PASSIVE (kinematic) so animated motion pushes ACTIVE bodies
        view_layer = bpy.context.view_layer
        if view_layer is not None and getattr(view_layer, "objects", None) is not None:
            try:
                view_layer.objects.active = slat
            except Exception:
                pass
        slat.select_set(True)
        bpy.ops.rigidbody.object_add(type="PASSIVE")
        # Guard rigid_body access with a local variable so static checkers know it's been narrowed
        rb = slat.rigid_body
        if rb is None:
            raise Exception("Rigid body not assigned")

        rb.collision_shape = "MESH"
        rb.friction = 1.5
        rb.restitution = 0.0
        rb.use_deactivation = False
        rb.kinematic = True
        # Set very small or zero collision margin to avoid floating gaps
        rb.use_margin = True
        # Force a zero collision margin to avoid solver contact gaps.
        # Some Blender builds or later operations may reset this, so set it again
        # after keyframe baking as well.
        rb.collision_margin = 0.0

        # Follow Path constraint and animation
        # Create the constraint and set attributes defensively (avoid typing.cast)
        constr = slat.constraints.new("FOLLOW_PATH")

        try:
            # constraint attributes may not be present in stubs; use a weakly-typed shim
            constr_any = cast(Any, constr)
            constr_any.target = curve_obj
            constr_any.use_curve_follow = True
            constr_any.use_fixed_location = True
            constr_any.offset_factor = offset_factor
        except Exception:
            # Fall back to individual guarded assignments in case some are missing
            try:
                cast(Any, constr).target = curve_obj
            except Exception:
                pass
            try:
                cast(Any, constr).use_curve_follow = True
            except Exception:
                pass
            try:
                cast(Any, constr).use_fixed_location = True
            except Exception:
                pass
            try:
                cast(Any, constr).offset_factor = offset_factor
            except Exception:
                pass
        slat.keyframe_insert(
            data_path=f'constraints["{constr.name}"].offset_factor', frame=1
        )
        # Advance by +1.0 so the fcurve can cycle continuously
        try:
            cast(Any, constr).offset_factor = offset_factor + 1.0
        except Exception:
            try:
                cast(Any, constr).offset_factor = offset_factor + 1.0
            except Exception:
                pass
        slat.keyframe_insert(
            data_path=f'constraints["{constr.name}"].offset_factor', frame=100
        )

        # Make fcurves linear and cyclic
        anim = getattr(slat, "animation_data", None)
        if anim and getattr(anim, "action", None):
            for fcurve in anim.action.fcurves:
                for kpt in fcurve.keyframe_points:
                    kpt.interpolation = "LINEAR"
                fcurve.modifiers.new(type="CYCLES")

        # Add to conveyor collection
        if conveyor_collection and all(
            o.name != slat.name for o in conveyor_collection.objects
        ):
            conveyor_collection.objects.link(slat)
            scene = getattr(bpy.context, "scene", None)
            if scene and getattr(scene, "collection", None) is not None:
                try:
                    scene.collection.objects.unlink(slat)
                except Exception:
                    pass

        return slat

    # Create multiple slats evenly spaced along the path
    num_slats = 20
    for i in range(num_slats):
        offset = (i / num_slats) % 1.0
        create_slat(f"Conveyor_Slat_{i + 1:02d}", offset)

    # Bake slat FOLLOW_PATH motion to keyframes so physics sees animated transforms
    try:
        start_frame = 1
        end_frame = 100
        # Iterate over objects whose names match the slat pattern and ensure runtime type
        for slat in [
            o for o in list(bpy.data.objects) if o.name.startswith("Conveyor_Slat_")
        ]:
            if not isinstance(slat, Object):
                continue
            # evaluate curve-driven constraint at each frame and keyframe location/rotation
            constr = next(
                (c for c in slat.constraints if c.type == "FOLLOW_PATH"), None
            )
            if not constr:
                continue
            for f in range(start_frame, end_frame + 1):
                scene = bpy.context.scene
                if scene is not None:
                    try:
                        scene.frame_set(1)
                    except Exception:
                        pass
                # Evaluate dependency graph to update constraint-driven transform
                view_layer = bpy.context.view_layer
                if view_layer is not None:
                    try:
                        view_layer.update()
                    except Exception:
                        pass
                # Keyframe object transform
                slat.keyframe_insert(data_path="location", frame=f)
                slat.keyframe_insert(data_path="rotation_euler", frame=f)
            # After baking, remove the follow-path constraint so the solver uses animated transforms
            slat.constraints.remove(constr)
        # restore frame to 1
        scene = bpy.context.scene
        if scene is not None:
            try:
                scene.frame_set(start_frame)
            except Exception:
                pass
    except Exception:
        pass

    # Bake slat Follow Path constraint motion into object keyframes so the
    # rigid-body solver receives explicit animated transforms. Baking from
    # frame 1..100 matches the constraint keyframes created above. After
    # baking we remove the Follow Path constraint to avoid double animation.
    try:
        start_frame = 1
        end_frame = 100
        # Collect slats created
        slat_objs = [
            o
            for o in bpy.data.objects
            if o.name.startswith("Conveyor_Slat_") and isinstance(o, Object)
        ]
        if slat_objs:
            # Ensure scene has correct frame range
            scene = bpy.context.scene
            if scene is not None:
                try:
                    scene.frame_start = start_frame
                    scene.frame_end = end_frame
                except Exception:
                    pass
            # Bake each slat's visual transform (location/rotation) from constraint
            for slat in slat_objs:
                view_layer = bpy.context.view_layer
                if (
                    view_layer is not None
                    and getattr(view_layer, "objects", None) is not None
                ):
                    try:
                        view_layer.objects.active = slat
                    except Exception:
                        pass
                slat.select_set(True)
                try:
                    bpy.ops.nla.bake(
                        frame_start=start_frame,
                        frame_end=end_frame,
                        only_selected=True,
                        visual_keying=True,
                        clear_constraints=True,
                        use_current_action=False,
                        step=1,
                    )
                except Exception:
                    # Fallback: keyframe sample transforms per frame
                    for f in range(start_frame, end_frame + 1):
                        scene = bpy.context.scene
                        if scene is not None:
                            try:
                                scene.frame_set(f)
                            except Exception:
                                pass
                        slat.keyframe_insert(data_path="location", frame=f)
                        slat.keyframe_insert(data_path="rotation_euler", frame=f)
                slat.select_set(False)
                # Re-apply collision margin after baking in case it was reset
                try:
                    rb = slat.rigid_body
                    if rb is not None:
                        try:
                            rb.use_margin = True
                            rb.collision_margin = 0.0
                        except Exception:
                            pass
                except Exception:
                    pass
    except Exception:
        pass

    # Ensure the scene has a rigid body world (for preview when running this step alone)
    if not getattr(scene, "rigidbody_world", None):
        try:
            bpy.ops.rigidbody.world_add()
        except Exception:
            pass

    print("✓ Created path-driven animated slats for friction transport")


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
    scene = bpy.context.scene
    if scene and getattr(scene, "collection", None) is not None:
        try:
            scene.collection.objects.unlink(conveyor)
        except Exception:
            pass

    # Add details (kept) and skip decorative supports/rollers
    add_conveyor_details(conveyor)

    # Setup physics and animation
    setup_conveyor_physics(conveyor)
    # Visual motion on material (optional) and physical slats for actual transport
    setup_conveyor_animation(conveyor)
    setup_friction_based_conveyor(conveyor)

    # Create hole in bucket
    create_bucket_hole()
    # Remove the decorative Conveyor_Belt mesh object so only the path and slats remain
    try:
        conveyor_collection = bpy.data.collections.get("conveyor_belt")
        # Remove any object named exactly 'Conveyor_Belt'
        belt_obj = bpy.data.objects.get("Conveyor_Belt")
        if belt_obj:
            # Unlink from collection if present
            try:
                if conveyor_collection and belt_obj.name in conveyor_collection.objects:
                    conveyor_collection.objects.unlink(belt_obj)
            except Exception:
                pass
            # Remove the object from the blend entirely
            try:
                bpy.data.objects.remove(belt_obj, do_unlink=True)
                print(
                    "✓ Removed decorative Conveyor_Belt object, preserving path and slats"
                )
            except Exception:
                pass

        # Prune any other non-path/non-slat objects from the conveyor collection to ensure collection contains only the path and slats
        if conveyor_collection:
            for obj in list(conveyor_collection.objects):
                if not (
                    obj.name == "Conveyor_Path" or obj.name.startswith("Conveyor_Slat_")
                ):
                    try:
                        # Unlink and remove to keep collection minimal
                        conveyor_collection.objects.unlink(obj)
                        bpy.data.objects.remove(obj, do_unlink=True)
                    except Exception:
                        # If removal fails, at least unlink it
                        try:
                            conveyor_collection.objects.unlink(obj)
                        except Exception:
                            pass
    except Exception:
        pass

    print("🎉 Conveyor belt system created successfully!")
    print("🔄 Using enhanced collision physics for part transport")
    print("✓ Conveyor properly positioned to connect with bucket hole")
    print("▶️ Press Space to start physics simulation")


# Execute the script
main()
