# Blender MCP Testing Guide

## Quick Test Methods

### Method 1: Direct Blender Script (Recommended for testing)

1. Open Blender
2. Go to `Scripting` workspace
3. Create a new text file
4. Copy and paste the contents of `create_sphere.py`
5. Click "Run Script" or press `Alt+P`

### Method 2: Using MCP Integration (Full setup)

1. **Start Blender with MCP addon:**

   - Open Blender
   - Go to 3D View sidebar (press `N`)
   - Find "BlenderMCP" tab
   - Click "Connect to Claude"

2. **Configure VSCode MCP:**

   - Open VSCode
   - Look for "MCP Servers" in the activity bar
   - Add server with:
     - Name: `blender`
     - Command: `uvx`
     - Args: `["blender-mcp"]`

3. **Test via GitHub Copilot Chat:**
   - Open GitHub Copilot Chat in VSCode
   - Ask: "Create a sphere at the center of the Blender scene"
   - The MCP tools should appear and execute the command

### Method 3: Terminal Test

Run the `test_blender_mcp.py` script:

```bash
python3 test_blender_mcp.py
```

## Expected Results

- A UV sphere should appear at coordinates (0, 0, 0)
- The sphere should be named "TestSphere"
- Default radius of 1.0 unit
- The sphere should be selected and active

## Troubleshooting

- If MCP server isn't running: Check Blender BlenderMCP tab
- If connection fails: Verify port 8888 is available
- If VSCode doesn't show MCP tools: Restart VSCode after configuring

## What the sphere looks like:

- Standard UV sphere with 32 segments and 16 rings
- Smooth shading applied by default
- Located at world origin (0, 0, 0)
- Standard material (gray by default)
