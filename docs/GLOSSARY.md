# Project Glossary

> **Quick Start**: See [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for common tasks  
> **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for system design  
> **How-To**: See [COMMON_TASKS.md](COMMON_TASKS.md) for detailed examples

Terminology reference for the LEGO Sorter project, covering Blender-specific terms, project concepts, and physics simulation vocabulary.

---

## Blender-Specific Terms

### Core Concepts

**Object**
- A 3D entity in the scene (mesh, camera, light, empty, etc.)
- Has transform properties: location, rotation, scale
- Can be linked to collections for organization

**Mesh**
- Geometric data defining an object's shape
- Composed of vertices, edges, and faces
- Can be edited with operators or BMesh API

**Collection**
- Logical grouping of objects (like folders for 3D objects)
- Used for organization and batch operations
- Can be nested hierarchically
- Example: `"bucket"`, `"conveyor_belt"`, `"lego_parts"`

**Scene**
- Container for all objects, collections, and settings
- Has a single rigidbody world for physics
- Stores render settings and timeline

**Context**
- Blender's current state (active object, selected objects, scene, etc.)
- Accessed via `bpy.context`
- Operations depend on context being set correctly

### Geometry & Modeling

**Boolean Modifier**
- Combines or subtracts meshes using set operations
- Operations: UNION, DIFFERENCE, INTERSECT
- Used in bucket creation (subtract cylinder to create hole)
- Can be slow for complex geometry

**BMesh**
- Low-level mesh editing API
- More efficient than operators for programmatic mesh creation
- Provides direct access to vertices, edges, faces
- Example: `import bmesh; bm = bmesh.new()`

**Primitive**
- Basic geometric shapes (cube, sphere, cylinder, plane, etc.)
- Starting point for more complex geometry
- Created with `bpy.ops.mesh.primitive_*_add()`

**Vertex (Vertices)**
- Points in 3D space that define mesh geometry
- Connected by edges to form faces
- Has position (x, y, z) in local or world space

**Face**
- Flat surface defined by 3+ vertices
- Forms the visible surface of a mesh
- Can have materials assigned

### Materials & Shading

**Material**
- Defines surface appearance (color, roughness, metallic, etc.)
- Uses node-based system in Blender
- Can be shared across multiple objects

**Principled BSDF**
- Versatile material node for physically-based rendering
- Combines multiple shading models in one node
- Inputs: Base Color, Metallic, Roughness, etc.
- Standard material in this project

**Node Tree**
- Graph of connected nodes that define material or geometry
- Nodes process and pass data through sockets
- Example: BSDF node → Output node

**Shader**
- Program that calculates surface color/appearance
- Built from node trees
- Executed during rendering

### Physics

**Rigid Body**
- Physics-enabled object that responds to forces
- Two types: ACTIVE (dynamic) and PASSIVE (static)
- Has properties: mass, friction, restitution (bounciness)

**Collision**
- Detection and response when objects intersect
- Uses collision margin for performance
- Can be set to mesh or primitive shape (box, sphere, etc.)

**Constraint**
- Limits or connects rigid body motion
- Types: hinge, slider, fixed, spring, etc.
- Not currently used in this project

**Rigidbody World**
- Scene-level physics simulation settings
- Properties: gravity, substeps, solver iterations
- Must exist before adding rigid bodies

**Substeps**
- Number of physics calculations per frame
- Higher = more accurate but slower
- Default: 10, increase for fast-moving or small objects

### Animation

**Keyframe**
- Stores property value at specific frame
- Interpolated between keyframes to create animation
- Can be added manually or by physics baking

**Timeline**
- Sequence of frames for animation
- Start frame, end frame, current frame
- Physics simulation runs across timeline

**Frame**
- Single point in time in animation
- Frame rate typically 24 or 30 fps
- Physics calculated per frame (with substeps)

### Rendering

**Camera**
- Defines viewpoint for rendering
- Has location, rotation, and lens properties (focal length, sensor size)
- Created with `bpy.ops.object.camera_add()`

**Render Engine**
- Algorithm for generating images from scene
- Eevee (real-time) vs Cycles (ray-tracing)
- Project uses Eevee for speed

**Resolution**
- Output image dimensions in pixels
- Set via `scene.render.resolution_x` and `resolution_y`
- Example: 1920x1080 (Full HD)

**Samples**
- Number of rays per pixel (ray-tracing quality)
- More samples = less noise but slower
- Irrelevant for Eevee renders

**Orthographic Camera**
- Parallel projection (no perspective distortion)
- Used for technical drawings
- Set via `camera.data.type = 'ORTHO'`

---

## Project-Specific Terms

### Components

**Sorting Bucket**
- Main collection container for unsorted LEGO parts
- Cylindrical with hollow interior and hole in bottom
- Parts fall through hole onto conveyor belt
- Created by `create_sorting_bucket.py`

**Conveyor Belt**
- Inclined transport system for LEGO parts
- Uses friction-based physics to move parts upward
- Includes support structures and end platform
- Created by `create_conveyor_belt.py`

**LEGO Part**
- Imported geometry from LDraw library
- Represents real LEGO bricks, plates, tiles, etc.
- Has realistic physics properties (2g mass, 0.9 friction)
- Imported by `import_lego_parts.py`

**Camera System**
- Identifies parts as they fall through tubes
- Uses raycasting for detection (future implementation)
- Positioned to capture parts in identification zone

**Tube**
- Vertical path for parts to fall through
- Location for camera identification
- Splits into multiple output tubes (future)

**Output Bucket**
- Destination for sorted parts
- Multiple buckets for different categories
- Not yet implemented

### Physics Properties

**LEGO_MASS**
- Mass of typical LEGO brick: 0.002 kg (2 grams)
- Measured from real LEGO bricks
- Used for realistic simulation

**LEGO_FRICTION**
- Friction coefficient for LEGO plastic: 0.9
- High friction allows stacking without slipping
- Based on material properties of ABS plastic

**CONVEYOR_ANGLE**
- Incline angle of conveyor belt: 0.15 radians (~8.6°)
- Steep enough for gravity assist, gentle enough for control
- Tuned experimentally for reliable transport

**BELT_FRICTION**
- Friction coefficient for belt surface: 0.8
- Prevents parts from sliding backward
- Simulates rubber or textured belt material

**GRAVITY_SCALE**
- Acceleration due to gravity: 9.81 m/s²
- Standard Earth gravity
- Applied to all rigid bodies

### Workflow Concepts

**Code-Driven Scene**
- Entire scene generated from Python scripts
- No manual Blender operations required
- Enables version control and reproducibility

**MCP (Model Context Protocol)**
- Communication protocol for remote Blender control
- Socket-based (TCP on localhost:9876)
- JSON command format

**Pipeline**
- Sequence of scripts that build complete scene
- Standard order: clear → bucket → conveyor → parts → physics → lighting → render
- Orchestrated by `run_lego_sorter.py`

**Collection Management**
- Objects organized by functional groups
- Each component script manages its own collection
- Prevents namespace conflicts

**Scene Reset**
- Clearing all objects and collections before rebuild
- Ensures clean state for reproducible results
- Performed by `clear_scene.py`

---

## LDraw / LEGO Terms

**LDraw**
- Open standard for LEGO CAD files
- File format: `.dat` (plain text)
- Geometry defined by parts library
- Path: `/Applications/Studio 2.0/ldraw/parts/`

**Part Number**
- Official LEGO identifier for each piece
- Examples: "3001" (2x4 brick), "3023" (1x2 plate)
- Used to locate corresponding LDraw file

**Brick**
- LEGO piece with studs on top, height ≥ 1 unit
- Examples: 2x4 brick, 1x1 brick
- Typically used for walls and structures

**Plate**
- LEGO piece with studs on top, height = 1/3 brick
- Examples: 2x4 plate, 1x1 plate  
- Used for thin layers and bases

**Tile**
- LEGO piece without studs on top
- Smooth surface for finishing
- Examples: 1x2 tile, 2x2 tile

**Technic Part**
- LEGO piece with holes for pins/axles
- More complex geometry
- Examples: beams, liftarms, gears

**Stud**
- Cylindrical protrusion on top of LEGO pieces
- Connects to anti-studs underneath other pieces
- Diameter: 4.8mm (0.00048 Blender units at 1:10 scale)

---

## MCP Communication Terms

**BlenderMCPClient**
- Python class for communicating with Blender via MCP
- Located in `utils/blender_mcp_client.py`
- Methods: `test_connection()`, `execute_code()`, `execute_script_file()`

**Command**
- JSON message sent to Blender MCP server
- Structure: `{"type": "execute_code", "params": {"code": "..."}}`
- Sent over TCP socket

**Response**
- JSON message received from Blender MCP server
- Structure: `{"status": "success/error", "result": "...", "message": "..."}`
- Contains execution result or error details

**Timeout**
- Maximum duration to wait for response
- Default: 180 seconds (3 minutes)
- Configurable via `BLENDER_MCP_TIMEOUT` environment variable

**Retry Logic**
- Automatic re-execution on failure
- Exponential backoff between attempts
- Implemented in `run_with_retries()`

**Socket**
- Network communication endpoint
- TCP connection to localhost:9876
- Persistent across multiple commands

---

## Development Terms

**Vibe Coding**
- Development style using AI assistance for exploration
- Emphasis on experimentation and iteration
- Less upfront design, more learning by building

**Type Hints**
- Python annotations specifying expected types
- Example: `def func(x: int) -> str:`
- Provided by `fake-bpy-module` for Blender API

**fake-bpy-module**
- Python package providing type stubs for Blender
- Enables IDE autocomplete and type checking
- No runtime effect (only for development)

**Stub**
- Python file with type hints but no implementation
- Used for type checking without importing actual module
- Files ending in `.pyi`

**Pylance**
- Python language server for VSCode
- Provides IntelliSense, type checking, auto-imports
- Configured in `.vscode/settings.json`

**Flake8**
- Python linter for code quality
- Checks style (PEP 8) and common errors
- Some rules ignored for Blender compatibility (E501, W503, F401)

---

## Measurement Units

**Blender Unit (BU)**
- Default unit in Blender (typically 1 BU = 1 meter)
- Project uses 1 BU = 1 meter for simplicity
- LEGO dimensions scaled to meters (1 stud ≈ 0.008 m at 1:1)

**Frame**
- Time unit in animation (1 frame = 1/24 second at 24 fps)
- Physics calculates per frame
- Example: "Parts settled by frame 50"

**Seconds**
- Real-world time unit
- Used for timeouts and benchmarks
- Example: "Import takes 45 seconds"

---

## Coordinate System

**X, Y, Z Axes**
- Right-handed coordinate system
- X: left/right, Y: forward/back, Z: up/down
- Origin (0, 0, 0) is scene center

**Location**
- Object position in 3D space
- Tuple: (x, y, z)
- Example: `(0.6, 0, 0.18)` for conveyor belt

**Rotation**
- Object orientation in 3D space
- Euler angles: (x_rot, y_rot, z_rot) in radians
- Example: `(0, 0.15, 0)` for conveyor pitch

**Scale**
- Object size multiplier
- Tuple: (x_scale, y_scale, z_scale)
- Example: `(1.2, 0.25, 0.02)` for flat conveyor belt

---

## Common Abbreviations

- **bpy**: Blender Python API
- **ops**: Operators (high-level Blender commands)
- **MCP**: Model Context Protocol
- **BSDF**: Bidirectional Scattering Distribution Function
- **PBR**: Physically-Based Rendering
- **FPS**: Frames Per Second
- **RGB(A)**: Red, Green, Blue, (Alpha/transparency)
- **API**: Application Programming Interface
- **TCP**: Transmission Control Protocol
- **JSON**: JavaScript Object Notation
- **CAD**: Computer-Aided Design
- **IDE**: Integrated Development Environment

---

## Physics Simulation States

**Static**
- Object doesn't move (PASSIVE rigidbody)
- Examples: floor, bucket, conveyor belt
- Only collides, doesn't respond to forces

**Dynamic**
- Object responds to physics (ACTIVE rigidbody)
- Examples: LEGO parts
- Falls, collides, can be pushed

**Kinematic**
- Object moves via animation, not physics
- Not used in this project
- Could be used for scripted conveyor motion

---

## Render Types

**Perspective Render**
- Camera with depth perspective
- Objects farther away appear smaller
- More realistic for human viewing

**Orthographic Render**
- Parallel projection, no perspective
- Objects same size regardless of distance
- Used for technical drawings
- All snapshot renders in this project

**Isometric View**
- Orthographic view at 45° angles
- Shows three faces of object equally
- Examples: ISO_NE, ISO_NW, ISO_SE, ISO_SW

---

## File Extensions

- `.py` - Python script
- `.blend` - Blender scene file (not used in this project)
- `.dat` - LDraw part definition file
- `.png` - Rendered image output
- `.md` - Markdown documentation
- `.json` - JSON data or configuration
- `.toml` - TOML configuration (pyproject.toml)

---

## Notes for AI Assistants

When using terms from this glossary:
- Link related concepts (e.g., "rigid body" → "collision")
- Provide examples from the project
- Explain why specific values are chosen (e.g., LEGO_MASS = 0.002)
- Reference relevant files where terms are used
- Use consistent terminology across all suggestions

For ambiguous terms:
- Clarify context (Blender vs project-specific vs general)
- Provide alternatives if multiple meanings exist
- Ask for clarification when unsure

When adding new terms:
- Add to appropriate section
- Provide clear definition
- Include example usage
- Link to related concepts
