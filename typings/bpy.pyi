"""
Stub file for bpy module to provide type hints for VSCode.
This file provides basic type definitions for the Blender Python API.
"""

from typing import Any, Dict, List, Optional, Union, Iterable, Iterator

class BlenderObject:
    name: str
    type: str
    location: Any
    bound_box: Any
    matrix_world: Any
    rotation_euler: Any
    modifiers: 'BlenderModifiers'
    rigid_body: Any
    data: Any
    
    def select_set(self, state: bool) -> None: ...

class BlenderModifier:
    name: str
    type: str
    # Common Boolean modifier attributes used in repo
    operation: str
    object: Optional[BlenderObject]
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...


class BlenderModifiers:
    def new(self, name: str, type: str) -> BlenderModifier: ...
    def __getitem__(self, key: str) -> BlenderModifier: ...
    def __iter__(self) -> Iterator[BlenderModifier]: ...


class BlenderCollectionObjects:
    def link(self, obj: BlenderObject) -> None: ...
    def unlink(self, obj: BlenderObject) -> None: ...
    def __iter__(self) -> Iterator[BlenderObject]: ...
    def __contains__(self, item: Any) -> bool: ...


class BlenderCollection:
    name: str
    objects: BlenderCollectionObjects
    
    def link(self, obj: BlenderObject) -> None: ...
    def unlink(self, obj: BlenderObject) -> None: ...

class LightData:
    name: str
    energy: float
    color: Any
    shape: str
    size: float


class World:
    name: str
    use_nodes: bool
    node_tree: Any


class DataObjects:
    """Collection-like accessor for data.objects"""
    def new(self, name: str, data: Any = None) -> BlenderObject: ...
    def get(self, name: str) -> Optional[BlenderObject]: ...
    def remove(self, obj: BlenderObject, do_unlink: bool = False) -> None: ...
    def __iter__(self) -> Iterator[BlenderObject]: ...


class DataCollections:
    def new(self, name: str) -> BlenderCollection: ...
    def get(self, name: str) -> Optional[BlenderCollection]: ...
    def remove(self, col: BlenderCollection) -> None: ...
    def __iter__(self) -> Iterator[BlenderCollection]: ...


class DataLights:
    def new(self, name: str, type: str = "POINT") -> LightData: ...
    def get(self, name: str) -> Optional[LightData]: ...
    def __iter__(self) -> Iterator[LightData]: ...


class DataWorlds:
    def new(self, name: str) -> World: ...
    def get(self, name: str) -> Optional[World]: ...
    def __iter__(self) -> Iterator[World]: ...


class BlenderData:
    objects: DataObjects
    collections: DataCollections
    lights: DataLights
    worlds: DataWorlds

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
