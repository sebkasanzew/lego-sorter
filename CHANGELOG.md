# Changelog

All notable changes to the LEGO Sorter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### In Progress
- Camera identification system for LEGO parts
- Tube splitting mechanism for sorting buckets
- Color detection logic for part classification

### Added
- **Documentation Optimization for AI Agents** (2025-10-07):
  - `QUICK_REFERENCE.md` - Concise 10-task quick reference (150 lines)
  - Cross-references between all documentation files for better navigation
  - Executive summary in `docs/ARCHITECTURE.md` for quick scanning
  - Expanded Pylance/VSCode setup in `docs/TYPE_IGNORE_GUIDE.md`

### Changed
- **Streamlined AGENTS.md** from 304 to ~180 lines (40% reduction):
  - Removed redundant MCP setup details (kept in README.md)
  - Moved Pylance/typing configuration to TYPE_IGNORE_GUIDE.md
  - Moved detailed workflow patterns to ARCHITECTURE.md
  - Added clear documentation map with cross-references
- **Enhanced documentation discoverability**:
  - Added navigation headers to all major documentation files
  - Linked related documents for easier AI agent navigation
  - Structured information hierarchy for context window efficiency

## [0.1.0] - 2025-01-16

### Added
- Comprehensive documentation structure for AI-assisted development:
  - `AGENTS.md` - Primary AI assistant instructions (migrated from `.github/copilot-instructions.md`)
  - `CHANGELOG.md` - Development journal and version history
  - `CONTEXT.md` - Session state and progress tracking
  - `docs/ARCHITECTURE.md` - Complete system design documentation (~400 lines)
  - `docs/COMMON_TASKS.md` - Quick reference guide for frequent operations
  - `docs/GLOSSARY.md` - 100+ term definitions for project context
- Scene validation utilities:
  - `utils/validate_scene.py` - Automated scene validation with detailed checks
  - Validates collections, physics world, bucket, conveyor, LEGO parts, camera, lighting, timeline
  - Returns statistics and actionable error messages
- Visual debugging helpers:
  - `utils/blender_debug.py` - Markers, arrows, state inspection
  - Functions for adding debug markers, measuring distances, visualizing bounding boxes
  - State inspection for objects, collections, and physics properties
- Test infrastructure:
  - `tests/test_scenarios.py` - Predefined test scenarios for common workflows
  - Defines test cases for validation, performance, and edge cases
- Project improvements:
  - Type hints with proper `bpy` module None handling for IDE support
  - Pylance configuration optimized with fake-bpy-module stubs
  - Better workspace structure with `typings-project/` for stub management

### Changed
- **Version scheme**: Adopted 0.MINOR.PATCH format (MAJOR stays at 0 until production-ready)
  - PATCH for daily changes, MINOR for milestones
- Migrated from `.github/copilot-instructions.md` to `AGENTS.md` (GitHub Copilot standard)
- Improved type checking setup:
  - Added `Dict`, `Any` imports to validation utilities
  - Used assertions for type narrowing in Blender context access
  - Configured Pylance to use PyPI stubs over local `typings/` folder

### Fixed
- Type errors in validation and debug utilities when imported outside Blender
- Import issues with `typing` module (added missing `Dict` and `Any`)
- Pylance not recognizing `bpy.types` properly (configured stub path correctly)

## [0.0.9] - 2025-10-07

### Added
- Lighting system with three-point setup (`setup_lighting.py`)
- Orthographic rendering from 10 viewpoints (top, bottom, sides, isometric)
- Camera system with automatic positioning (`render_snapshot.py`)
- Frame-specific diagnostic tools (`diagnose_raycast_frame20.py`)
- Scene state inspection utilities (`inspect_parts_state.py`)

### Fixed
- Physics timing issues with conveyor belt incline
- LEGO parts now properly transport up conveyor without sliding back
- Bucket hole diameter adjusted to allow all standard parts to pass through

## [0.0.3] - 2025-10-06

### Added
- Physics animation system (`animate_lego_physics.py`)
- Realistic LEGO properties: 2g mass, 0.9 friction coefficient
- Rigid body simulation with gravity
- Conveyor belt animation through material displacement
- Retry logic with exponential backoff for MCP operations
- Debug mode with `BLENDER_MCP_DEBUG` environment variable

### Changed
- Improved error handling in MCP client with longer timeouts
- Enhanced user feedback with emoji-based progress indicators

## [0.0.2] - 2025-10-05

### Added
- Conveyor belt system with inclined transport (`create_conveyor_belt.py`)
- Support structures for conveyor belt
- Friction-based physics for part transport
- Material system with Principled BSDF shaders
- Collection-based object organization

### Changed
- Refactored bucket creation to use boolean operations for hollow interior
- Improved LDraw import with vertical part arrangement

## [0.0.1] - 2025-10-01

### Added
- Initial project setup with MCP-Blender integration
- MCP client utility (`blender_mcp_client.py`)
- Scene clearing functionality (`clear_scene.py`)
- Sorting bucket creation with hollow interior (`create_sorting_bucket.py`)
- LDraw part import with 70+ common LEGO parts (`import_lego_parts.py`)
- Main orchestration script (`run_lego_sorter.py`)
- VSCode configuration for Blender type hints
- Type hints using `fake-bpy-module`

### Project Context
- Inspired by [Coral Teachable Sorter](https://coral.ai/projects/teachable-sorter/)
- Goal: Simulate complete LEGO sorting pipeline
- Architecture: Code-driven scene generation (no binary .blend files)
- Communication: Remote Blender control via MCP protocol

## Development Philosophy

### Code-Driven Design
All scene geometry is generated through Python scripts with no manual Blender operations. This ensures:
- Complete reproducibility from source control
- Version-trackable scene changes
- Automated testing and CI/CD potential
- Collaborative development without binary conflicts

### Known Challenges
- **Physics Timing**: Parts sometimes desync at specific frames (investigating frame 20 issues)
- **LDraw Import**: Some complex Technic parts fail to import properly
- **Conveyor Friction**: Fine-tuning friction coefficients for reliable transport
- **MCP Timeouts**: Heavy operations (import, physics bake) require extended timeouts

### Future Roadmap
1. **Identification System**: Camera-based part detection using raycasting
2. **Sorting Logic**: Tube splitting mechanism with multiple output buckets
3. **AI Integration**: Color/shape classification (potential Coral TPU integration)
4. **Performance**: Optimize physics simulation for faster iteration
5. **Visualization**: Enhanced rendering for presentation and debugging

---

## Notes for AI Assistants

When adding entries:
- Use **Added** for new features
- Use **Changed** for modifications to existing functionality
- Use **Fixed** for bug fixes
- Use **Removed** for deleted features
- Include relevant file names in parentheses
- Note frame numbers for physics-related changes
- Reference issue numbers when applicable
