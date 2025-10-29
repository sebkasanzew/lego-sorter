# Project Glossary

Quick terminology reference for LEGO Sorter project.

## Blender Core

**Object** - 3D entity (mesh, camera, light). Has location, rotation, scale.  
**Collection** - Group of objects (`"bucket"`, `"lego_parts"`, `"conveyor_belt"`).  
**Boolean Modifier** - Combine/subtract meshes (UNION, DIFFERENCE, INTERSECT).  
**BMesh** - Low-level mesh editing API for precise operations.  
**Rigid Body** - Physics simulation type (ACTIVE=dynamic, PASSIVE=static).

## MCP Integration

**MCP (Model Context Protocol)** - Communication layer between Python and Blender.  
**BlenderMCP Addon** - Blender addon enabling MCP server (localhost:9876).  
**MCP Client** - Python class (`BlenderMCPClient`) sending commands to Blender.  
**execute_script_file()** - Run Python script in Blender via MCP.  
**execute_code()** - Run code string in Blender via MCP.

## Physics

**Rigid Body World** - Physics container managing all simulations.  
**Mass** - Object weight (2g for LEGO bricks: `0.002` kg).  
**Friction** - Surface resistance (LEGO: `0.9`, conveyor: `0.8`).  
**Collision Shape** - Physics boundary (CONVEX_HULL, MESH, BOX).

## LEGO/LDraw

**LDraw** - Library of LEGO part geometries (.dat files).  
**LDraw Importer** - Blender addon converting .dat to meshes.  
**Part ID** - LDraw identifier (e.g., `3001` = 2x4 brick).

## Project Patterns

**Auto-execution** - Scripts end with `main()` call (no `if __name__`).  
**Code-driven** - No .blend files, all scenes from Python scripts.  
**Ephemeral State** - Scene cleared and rebuilt each run.
- More efficient than operators for programmatic mesh creation
- Provides direct access to vertices, edges, faces
- Example: `import bmesh; bm = bmesh.new()`

