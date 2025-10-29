# LEGO Sorter - Blender Simulation

> **For AI Agents**: See [AGENTS.md](AGENTS.md) for development instructions  
> **Quick Reference**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common tasks

Blender-based simulation for sorting LEGO parts using Model Context Protocol (MCP) and Jupyter notebooks.

## Project Goal

Model a machine that sorts LEGO bricks by shape and color through: Collection → Conveyor → Separation → Identification → Sorting → Output.

Inspired by [Coral Teachable Sorter](https://coral.ai/projects/teachable-sorter/).

## Key Files

- **`lego_sorter_pipeline.ipynb`** - Main interactive pipeline (run cells sequentially)
- **`quick_experiments.ipynb`** - Quick testing and debugging
- **`blender/*.py`** - Scene generation scripts (executed via MCP)
- **`utils/blender_mcp_client.py`** - MCP communication layer

## Setup

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start Blender** with BlenderMCP addon (Press N → BlenderMCP → "Connect to MCP server")
3. **Verify LDraw** library at `/Applications/Studio 2.0/ldraw/parts/` (macOS)

## Usage

```bash
# Launch Jupyter
jupyter notebook

# Open lego_sorter_pipeline.ipynb
# Run cells sequentially (Shift+Enter)
```

**Notebooks**:
- **`lego_sorter_pipeline.ipynb`** - Full pipeline with docs
- **`quick_experiments.ipynb`** - Quick tests and debugging

**Test MCP**: `python utils/blender_mcp_client.py`

## Architecture

```
Jupyter Notebook → BlenderMCPClient → TCP (localhost:9876) → Blender → Scene
```

**Code-driven**: No .blend files. Everything from Python scripts via MCP.

## Troubleshooting

**Connection failed**: Ensure Blender running with MCP addon enabled  
**LDraw errors**: Verify path in `blender/import_lego_parts.py`  
**Timeout**: Increase in notebook cells: `client = BlenderMCPClient(timeout=600)`

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more.
