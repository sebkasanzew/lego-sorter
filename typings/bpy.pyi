"""
Stub file for bpy module to provide type hints for VSCode.
This file provides basic type definitions for the Blender Python API.
"""

from typing import Any, Dict, List, Optional, Union

class BlenderObject:
    name: str
    type: str
    location: Any
    bound_box: Any
    matrix_world: Any
    
    def select_set(self, state: bool) -> None: ...

class BlenderCollection:
    name: str
    objects: List[BlenderObject]
    
    def link(self, obj: BlenderObject) -> None: ...
    def unlink(self, obj: BlenderObject) -> None: ...

class BlenderData:
    objects: List[BlenderObject]
    collections: List[BlenderCollection]
    
    def remove(self, obj: BlenderObject, do_unlink: bool = False) -> None: ...

class BlenderContext:
    object: Optional[BlenderObject]
    active_object: Optional[BlenderObject]
    scene: Any
    collection: BlenderCollection
    view_layer: Any

class BlenderOperators:
    def select_all(self, action: str) -> None: ...
    def delete(self, use_global: bool = True) -> None: ...

class MeshOperators:
    def primitive_cylinder_add(self, radius: float = 1.0, depth: float = 2.0, location: tuple = (0, 0, 0)) -> None: ...
    def primitive_circle_add(self, radius: float = 1.0, enter_editmode: bool = False, align: str = 'WORLD', location: tuple = (0, 0, 0), rotation: tuple = (0, 0, 0)) -> None: ...
    def fill(self) -> None: ...

class ObjectOperators:
    def select_all(self, action: str) -> None: ...
    def delete(self, use_global: bool = True) -> None: ...
    def mode_set(self, mode: str) -> None: ...
    def join(self) -> None: ...
    def transform_apply(self, location: bool = False, rotation: bool = False, scale: bool = False) -> None: ...
    def modifier_apply(self, modifier: str) -> None: ...

class ImportOperators:
    def importldraw(self, filepath: str) -> None: ...

class Operations:
    object: ObjectOperators
    mesh: MeshOperators
    import_scene: ImportOperators

# Module-level objects
data: BlenderData
context: BlenderContext
ops: Operations
