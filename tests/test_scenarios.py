"""Test scenarios for LEGO Sorter simulation.

Defines expected behaviors and validation functions for different simulation
scenarios. These can be used by AI assistants to understand what "correct"
behavior looks like and to validate changes.

Usage:
    from tests.test_scenarios import SCENARIOS, validate_scenario

    # Check if scenario passes
    scenario = SCENARIOS["basic_gravity"]
    issues = validate_scenario(scenario)
    if not issues:
        print("✅ Scenario passed")
    else:
        print(f"❌ Failed: {issues}")
"""

from typing import Dict, List, Callable, Any

# Type alias for validator functions
Validator = Callable[[Any], bool]


# Define test scenarios with expected outcomes
SCENARIOS: Dict[str, Dict[str, Any]] = {
    "basic_gravity": {
        "description": "Single LEGO brick falls into bucket under gravity",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            # Would import single part instead of all parts
        ],
        "frames": 50,
        "expected": {
            "part_z_position": lambda z: z
            < 0.15,  # Part settled in bucket (below 0.15)
            "part_z_velocity": lambda v: abs(v) < 0.01,  # Part stopped moving
        },
        "validation_notes": [
            "Part should fall and settle in bucket bottom",
            "Final Z position should be near bucket base (< 0.15 units)",
            "Velocity should be near zero (< 0.01 units/frame)",
        ],
    },
    "conveyor_transport": {
        "description": "Part moves up conveyor belt from bucket",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            "create_conveyor_belt.py",
            # Import single part positioned on conveyor
        ],
        "frames": 100,
        "expected": {
            "part_x_position": lambda x: x > 1.0,  # Part moved up belt (X > 1.0)
            "part_z_position": lambda z: z > 0.3,  # Part elevated (Z > 0.3)
        },
        "validation_notes": [
            "Part should move up the inclined conveyor",
            "X position should increase beyond 1.0",
            "Z position should increase (following incline)",
            "Part should not slide backward (friction working)",
        ],
    },
    "multiple_parts_separation": {
        "description": "Multiple parts separate on conveyor without stacking",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            "create_conveyor_belt.py",
            # Import 3-5 parts close together
        ],
        "frames": 150,
        "expected": {
            "min_part_spacing": lambda spacing: spacing > 0.05,  # Min 0.05 units apart
            "all_parts_moving": lambda moving_count, total: moving_count == total,
        },
        "validation_notes": [
            "Parts should spread out on conveyor",
            "No parts should be permanently stacked",
            "All parts should reach the end eventually",
            "Minimum spacing of 0.05 units between parts",
        ],
    },
    "bucket_hole_clearance": {
        "description": "Standard LEGO parts pass through bucket hole",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            # Import parts positioned above hole
        ],
        "frames": 50,
        "expected": {
            "parts_below_hole": lambda count, total: count
            == total,  # All parts fell through
            "parts_in_bucket": lambda count: count == 0,  # No parts stuck
        },
        "validation_notes": [
            "All standard parts (2x4, 2x2, 1x2, 1x1 bricks/plates) should fit",
            "Hole diameter is 0.24 units (sufficient clearance)",
            "Parts should fall through without getting stuck",
        ],
    },
    "physics_stability": {
        "description": "Simulation remains stable without explosions",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            "create_conveyor_belt.py",
            "import_lego_parts.py",
        ],
        "frames": 200,
        "expected": {
            "max_velocity": lambda v: v < 50.0,  # No unrealistic speeds
            "max_position": lambda pos: abs(pos) < 100.0,  # Objects stay in scene
            "no_nan_values": lambda has_nan: not has_nan,  # No NaN in transforms
        },
        "validation_notes": [
            "No parts should fly off at high speed (< 50 units/frame)",
            "All objects should stay within reasonable bounds (< 100 units from origin)",
            "No NaN or Inf values in positions/rotations",
            "Simulation should complete without errors",
        ],
    },
    "conveyor_friction": {
        "description": "Parts don't slide backward on inclined conveyor",
        "setup": [
            "clear_scene.py",
            "create_conveyor_belt.py",
            # Import single part on conveyor
        ],
        "frames": 100,
        "expected": {
            "x_position_increasing": lambda x_positions: all(
                x_positions[i]
                <= x_positions[i + 1] + 0.001  # Allow tiny numerical error
                for i in range(len(x_positions) - 1)
            ),
            "net_movement_positive": lambda start_x, end_x: end_x > start_x + 0.1,
        },
        "validation_notes": [
            "X position should monotonically increase (or stay same)",
            "Part should not slide backward down the belt",
            "Friction coefficient of 0.8 should be sufficient",
            "Net movement should be positive (> 0.1 units)",
        ],
    },
    "material_assignment": {
        "description": "All objects have materials assigned",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            "create_conveyor_belt.py",
            "import_lego_parts.py",
        ],
        "frames": 1,  # No animation needed
        "expected": {
            "bucket_has_material": lambda has_mat: has_mat,
            "conveyor_has_material": lambda has_mat: has_mat,
            "parts_have_materials": lambda count, total: count == total,
        },
        "validation_notes": [
            "Bucket should have material assigned",
            "Conveyor belt should have material",
            "All LEGO parts should have materials",
            "Materials should use Principled BSDF",
        ],
    },
    "collection_organization": {
        "description": "Objects are properly organized in collections",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            "create_conveyor_belt.py",
            "import_lego_parts.py",
        ],
        "frames": 1,
        "expected": {
            "bucket_collection_exists": lambda exists: exists,
            "conveyor_collection_exists": lambda exists: exists,
            "parts_collection_exists": lambda exists: exists,
            "objects_in_correct_collections": lambda correct, total: correct == total,
        },
        "validation_notes": [
            "Three main collections should exist: bucket, conveyor_belt, lego_parts",
            "Bucket objects should be in 'bucket' collection only",
            "Conveyor objects in 'conveyor_belt' collection",
            "LEGO parts in 'lego_parts' collection",
        ],
    },
    "camera_positioning": {
        "description": "Camera is positioned to capture scene properly",
        "setup": [
            "clear_scene.py",
            "create_sorting_bucket.py",
            "create_conveyor_belt.py",
            "render_snapshot.py",
        ],
        "frames": 1,
        "expected": {
            "camera_exists": lambda exists: exists,
            "camera_has_target": lambda has_target: has_target,
            "camera_distance": lambda dist: 2.0 < dist < 10.0,  # Reasonable distance
        },
        "validation_notes": [
            "SorterCam should exist in scene",
            "Camera should be positioned to view entire scene",
            "Distance from origin should be 2-10 units",
            "Camera should point toward origin or bucket",
        ],
    },
    "lighting_setup": {
        "description": "Three-point lighting is properly configured",
        "setup": [
            "clear_scene.py",
            "setup_lighting.py",
        ],
        "frames": 1,
        "expected": {
            "min_lights": lambda count: count >= 3,  # At least 3 lights
            "key_light_exists": lambda exists: exists,
            "fill_light_exists": lambda exists: exists,
            "back_light_exists": lambda exists: exists,
        },
        "validation_notes": [
            "At least 3 lights should exist (key, fill, back)",
            "Key light should be brightest",
            "Fill light reduces shadows",
            "Back light provides depth separation",
        ],
    },
}


def validate_scenario(scenario_name: str) -> List[str]:
    """Validate a scenario against its expected outcomes.

    This is a placeholder - actual implementation would run in Blender
    and check physics results.

    Args:
        scenario_name: Name of scenario from SCENARIOS dict

    Returns:
        List of validation issues (empty if all checks pass)
    """
    if scenario_name not in SCENARIOS:
        return [f"Unknown scenario: {scenario_name}"]

    scenario = SCENARIOS[scenario_name]

    # Placeholder: In real implementation, this would:
    # 1. Run the setup scripts
    # 2. Simulate to specified frame count
    # 3. Check expected conditions
    # 4. Return list of failures

    return [
        "Validation not yet implemented",
        "Would need to run in Blender with MCP connection",
        f"Expected checks: {list(scenario['expected'].keys())}",
    ]


def get_scenario_summary(scenario_name: str) -> str:
    """Get a human-readable summary of a scenario.

    Args:
        scenario_name: Name of scenario

    Returns:
        Formatted summary string
    """
    if scenario_name not in SCENARIOS:
        return f"Unknown scenario: {scenario_name}"

    scenario = SCENARIOS[scenario_name]

    summary = f"\n{'=' * 60}\n"
    summary += f"Scenario: {scenario_name}\n"
    summary += f"{'=' * 60}\n"
    summary += f"\nDescription:\n  {scenario['description']}\n"
    summary += f"\nSetup Steps:\n"
    for i, step in enumerate(scenario["setup"], 1):
        summary += f"  {i}. {step}\n"
    summary += f"\nSimulation Frames: {scenario['frames']}\n"
    summary += f"\nExpected Outcomes:\n"
    for check in scenario["expected"].keys():
        summary += f"  • {check}\n"
    summary += f"\nValidation Notes:\n"
    for note in scenario.get("validation_notes", []):
        summary += f"  • {note}\n"
    summary += f"{'=' * 60}\n"

    return summary


def list_scenarios() -> None:
    """Print all available test scenarios."""
    print("\nAvailable Test Scenarios:")
    print("=" * 60)
    for name, scenario in SCENARIOS.items():
        print(f"\n{name}:")
        print(f"  {scenario['description']}")
        print(f"  Frames: {scenario['frames']}")
        print(f"  Checks: {len(scenario['expected'])}")
    print("\n" + "=" * 60)


# Example usage for AI assistants
EXAMPLE_USAGE = """
Example: Validating a scenario manually in Blender

1. Run setup scripts in order:
   ```python
   from utils.blender_mcp_client import BlenderMCPClient
   client = BlenderMCPClient()
   
   scenario = SCENARIOS["basic_gravity"]
   for script in scenario["setup"]:
       client.execute_script_file(f'blender/{script}', script)
   ```

2. Advance to specified frame:
   ```python
   client.execute_code(f'''
   import bpy
   bpy.context.scene.frame_set({scenario["frames"]})
   ''', 'Set Frame')
   ```

3. Check expected conditions:
   ```python
   client.execute_code('''
   import bpy
   parts_col = bpy.data.collections.get("lego_parts")
   if parts_col and len(parts_col.objects) > 0:
       part = parts_col.objects[0]
       print(f"Part Z position: {part.location.z}")
       # Compare against scenario["expected"]["part_z_position"]
   ''', 'Check Position')
   ```

Example: Using scenarios to understand expected behavior

An AI assistant can reference scenarios to understand what "correct" means:

```python
# When debugging physics issues
from tests.test_scenarios import SCENARIOS, get_scenario_summary

# Show what "conveyor_transport" should look like
print(get_scenario_summary("conveyor_transport"))

# This tells the AI that parts should:
# - Move in positive X direction (up the belt)
# - Increase Z position (following incline)
# - Not slide backward
# - End up at X > 1.0, Z > 0.3
```

Example: Validation function structure

```python
def check_basic_gravity(frame: int = 50) -> List[str]:
    import bpy
    issues = []
    
    parts_col = bpy.data.collections.get("lego_parts")
    if not parts_col:
        return ["LEGO parts collection not found"]
    
    if len(parts_col.objects) == 0:
        return ["No LEGO parts in scene"]
    
    part = parts_col.objects[0]
    
    # Check Z position
    if not (part.location.z < 0.15):
        issues.append(f"Part Z too high: {part.location.z:.3f} (expected < 0.15)")
    
    # Note: Velocity not accessible in cached simulation
    # Would need to compare positions across frames
    
    return issues
```
"""


if __name__ == "__main__":
    # Show all scenarios when run as script
    list_scenarios()

    # Show example
    print("\n" + EXAMPLE_USAGE)
