# Development Context

> **Quick Start**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common tasks  
> **AI Instructions**: See [AGENTS.md](AGENTS.md) for development guidance  
> **Last Updated**: 2025-10-07

## Current Focus

**Goal**: Improve AI-assisted development workflow

**Active Tasks**:
- ✅ Migrated to AGENTS.md format (GitHub Copilot standard)
- ✅ Created comprehensive documentation structure
- 🔄 Adding validation and debugging utilities
- 🔜 Implementing camera identification system

## Recent Changes (Last 3 Sessions)

### Session 2025-10-07
- Added `AGENTS.md` (migrated from `.github/copilot-instructions.md`)
- Created `CHANGELOG.md` for development tracking
- Created `docs/ARCHITECTURE.md` with system design details
- Created `docs/COMMON_TASKS.md` with quick reference guide
- Adding `CONTEXT.md` (this file) for session state tracking
- Next: Create `docs/GLOSSARY.md`, validation scripts, debug utilities

### Session 2025-10-06 (Previous)
- Added lighting system (`setup_lighting.py`)
- Added orthographic rendering from 10 viewpoints
- Added camera system with automatic positioning
- Fixed physics timing issues with conveyor belt
- Added frame-specific diagnostic tools

### Session 2025-10-05 (Earlier)
- Implemented physics animation system
- Added realistic LEGO properties (2g mass, 0.9 friction)
- Added retry logic with exponential backoff for MCP
- Added debug mode with `BLENDER_MCP_DEBUG` environment variable

## Next Steps

### Immediate (This Session)
1. ✅ Create `docs/GLOSSARY.md` - Terminology reference
2. ✅ Create `utils/validate_scene.py` - Scene validation script
3. ✅ Create `utils/blender_debug.py` - Debug helpers
4. ✅ Create `tests/test_scenarios.py` - Test scenarios
5. ✅ Update `pyproject.toml` - Add metadata and keywords

### Short Term (Next 1-2 Sessions)
1. Enhance error handling
   - Add better error context in all scripts
   - Implement automatic scene recovery
   - Add structured logging to file

2. Build a working conveyor system
   - Add output bucket
   - Improve the conveyor belt with physics
   - Move the lego parts from input to output bucket using physics

3. Add tube splitting mechanism
   - Design parametric tube geometry
   - Implement branching logic
   - Move parts randomly, as this simulation is only about the conveyor and general architecture

### Medium Term (Next 3-5 Sessions)
1. Color detection logic
   - Extract color from material properties
   - Classify parts by color families
   - Route to appropriate output buckets

2. Performance optimization
   - Cache LDraw part imports
   - Reduce physics substeps where possible
   - Optimize rendering settings

3. Testing infrastructure
   - Automated scene validation
   - Visual regression testing
   - Physics validation at key frames

### Long Term (Future)
1. Multi-bucket sorting
   - 4+ output buckets for fine-grained sorting
   - Configurable sorting rules
   - Statistics tracking (parts per bucket)

2. Conveyor system enhancements
   - Test different designs for optimal transport of lego parts
   - Variable speed control
   - Dynamic obstacles
   - Real-time user controls

2. Visualization improvements
   - Animation export (video)

## Known Issues

### Active Bugs
- [ ] **Issue #12**: Physics occasionally desync at frame 20
  - **Symptom**: Parts jump or teleport unexpectedly
  - **Workaround**: Re-run simulation from scratch
  - **Investigation**: See `diagnose_raycast_frame20.py`

- [ ] **LDraw Import**: Some Technic parts fail to import
  - **Affected Parts**: Complex parts with many subparts
  - **Workaround**: Use simpler brick/plate parts only
  - **TODO**: Add error handling for failed imports

### Resolved Issues
- [x] **Bucket hole too small** (Fixed 2025-10-05)
  - Increased diameter from 0.20 to 0.24 units
  - All standard parts now pass through

- [x] **Conveyor friction too low** (Fixed 2025-10-06)
  - Increased friction coefficient from 0.5 to 0.8
  - Parts no longer slide backward

- [x] **MCP timeouts on heavy operations** (Fixed 2025-10-06)
  - Added configurable timeouts via environment variable
  - Implemented retry logic with exponential backoff

## Environment Setup

### Current Configuration
- **Blender Version**: 4.2 (or latest)
- **Python**: 3.13
- **MCP Server**: localhost:9876
- **LDraw Path**: `/Applications/Studio 2.0/ldraw/parts/` (macOS)
- **Render Output**: `renders/` directory

### VSCode Settings
- Python interpreter: `/Users/sebastian/.pyenv/versions/3.13.5/bin/python`
- Type checking: Basic
- Linting: Flake8 enabled (E501, W503, F401 ignored)
- Extra paths: `./blender`, `./utils`

### Key Dependencies
- `fake-bpy-module-latest==20251003` (type hints)
- BlenderMCP addon (remote control)
- LDraw library (LEGO geometry)

## Project Status

### Completed Components ✅
- [x] Scene clearing and reset
- [x] Sorting bucket with hollow interior
- [x] Conveyor belt system with physics
- [x] LEGO part import from LDraw
- [x] Physics simulation with gravity
- [x] Lighting system (three-point)
- [x] Multi-view rendering system
- [x] MCP communication layer
- [x] Documentation structure

### In Progress 🔄
- [ ] Scene validation utilities (80% complete)
- [ ] Debug helpers (50% complete)
- [ ] Test scenarios (30% complete)

### Planned Components 📋
- [ ] Camera identification system
- [ ] Tube splitting mechanism
- [ ] Color detection logic
- [ ] Sorting decision tree
- [ ] Multiple output buckets
- [ ] Statistics tracking
- [ ] Video export

### Deferred/Optional 💤
- [ ] Real-time preview mode
- [ ] Multi-camera setup

## Metrics & Statistics

### Performance Benchmarks
| Operation | Duration | Last Measured |
|-----------|----------|---------------|
| Clear scene | ~2s | 2025-10-07 |
| Create bucket | ~4s | 2025-10-07 |
| Create conveyor | ~8s | 2025-10-07 |
| Import parts (70 parts) | ~45s | 2025-10-07 |
| Physics setup | ~6s | 2025-10-07 |
| Lighting setup | ~3s | 2025-10-07 |
| Render (10 views) | ~180s | 2025-10-07 |
| **Total Pipeline** | **~248s** | **2025-10-07** |

### Code Statistics
- Total Python files: ~15
- Total lines of code: ~3500
- Blender scripts: 10
- Utility scripts: 3
- Test scripts: 2
- Documentation files: 5

## Notes for AI Assistants

### Current Session Context
We're improving the AI-assisted development workflow by adding:
1. Better documentation structure (AGENTS.md, CHANGELOG.md, ARCHITECTURE.md)
2. Quick reference guides (COMMON_TASKS.md, GLOSSARY.md)
3. Validation and debugging utilities
4. Test scenarios for automated validation

### What's Working Well
- MCP-based remote control is reliable
- Physics simulation is stable (except frame 20 edge case)
- Code-driven scene generation enables good version control
- Type hints provide excellent IDE support

### What Needs Improvement
- Error messages could be more contextual
- Physics debugging is still manual
- No automated scene validation yet
- Testing requires manual inspection

### Preferred Patterns
- Use `ensure_material()` pattern for materials
- Use `clear_existing_*()` before creating components
- Always check `bpy.context.active_object` for None
- Use collection-based organization
- Add emoji indicators for user feedback (✅ ❌ 🔄)

### Anti-Patterns to Avoid
- Don't use `if __name__ == "__main__"` in Blender scripts
- Don't assume `bpy.context.active_object` is not None
- Don't hardcode file paths (use environment variables)
- Don't skip `clear_scene.py` at start of pipeline
- Don't ignore physics timing (frame order matters)

---

**Update this file at the start and end of each development session!**
