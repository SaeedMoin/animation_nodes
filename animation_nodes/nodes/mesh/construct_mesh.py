import bpy
from bpy.props import *
from ... data_structures import Mesh
from ... base_types import AnimationNode

sourceItems = [
    ("MESH_DATA", "Mesh Data", "", "OUTLINER_DATA_MESH", 0),
    ("OBJECT", "Object", "", "OBJECT_DATAMODE", 1)
]

class ConstructMeshNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstructMeshNode"
    bl_label = "Construct Mesh"

    source = EnumProperty(name = "Source", default = "MESH_DATA",
        items = sourceItems, update = AnimationNode.refresh)

    def create(self):
        if self.source == "MESH_DATA":
            self.newInput("Vector List", "Vertices", "vertices")
            self.newInput("Edge Indices List", "Edge Indices", "edgeIndices")
            self.newInput("Polygon Indices List", "Polygon Indices", "polygonIndices")
        elif self.source == "OBJECT":
            self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
            self.newInput("Boolean", "Use World Space", "useWorldSpace", value = True)
            self.newInput("Boolean", "Use Modifiers", "useModifiers", value = False)
            self.newInput("Scene", "Scene", "scene", hide = True)
        self.newOutput("Mesh", "Mesh", "mesh")

    def draw(self, layout):
        layout.prop(self, "source", text = "")

    def getExecutionFunctionName(self):
        if self.source == "MESH_DATA":
            return "execute_MeshData"
        elif self.source == "OBJECT":
            return "execute_Object"

    def execute_MeshData(self, vertices, edgeIndices, polygonIndices):
        return Mesh(vertices, edgeIndices, polygonIndices)

    def execute_Object(self, object, useWorldSpace, useModifiers, scene):
        if object is None:
            return Mesh()

        sourceMesh = object.an.getMesh(scene, useModifiers)

        vertices = sourceMesh.an.getVertices()
        if useWorldSpace:
            vertices.transform(object.matrix_world)

        edges = sourceMesh.an.getEdgeIndices()
        polygons = sourceMesh.an.getPolygonIndices()

        if sourceMesh.users == 0:
            bpy.data.meshes.remove(sourceMesh)

        return Mesh(vertices, edges, polygons, skipValidation = True)