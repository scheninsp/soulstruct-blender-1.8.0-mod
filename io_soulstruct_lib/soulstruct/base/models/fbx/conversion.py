from pathlib import Path

from soulstruct.utilities.maths import Vector3

from soulstruct.base.models.fbx.core import FBX
from soulstruct.base.models.flver.core import FLVER
from soulstruct.base.models.flver.submesh import Submesh, FaceSet
from soulstruct.base.models.flver.vertex import Vertex


def dsr_map_piece_fbx_to_flver(fbx_path: Path, scale=0.01):
    """Convert an FBX to a DSR Map Piece.

    Map pieces should be straightforward enough for me to do this.

    Note that I am leaving FLVER -> FBX conversion to Noesis, which is also straightforward.
    """

    fbx = FBX(fbx_path)

    # TODO: The "Connections" root node of FBX links arbitrary "Objects" nodes together by their ID (node's first
    #  property).

    # TODO: Objects:
    #   - Geometry: a mesh. Contains `Vertices`, `PolygonVertexIndex` (faces?), `Edges` (likely not stored in FLVER?),
    #   `LayerElementNormal.Normals` (normals)`, `LayerElementUV.UV` (UVs, and `UVIndex` to map them to faces)

    # "Vertices" contains flattened XYZ vectors for all vertices.
    # TODO: Blender (or more likely Noesis) appears to scale the vertices up by 100. Find and fix this setting, or just
    #  have an option to undo it here. (It's scaled in Blender view, so must be a Noesis thing.)

    # Notably, all the weird repeated vertices seem to be stripped out of the FLVER, probably by Noesis. So it won't be
    # possible to get byte-perfect writes, but it hardly matters.

    FACE_SET_MAX_TRIANGLES = 65535  # ushort max

    print(fbx.to_string())

    for node in fbx["Objects"].children:
        if node.name == "Geometry":  # mesh
            flat_v = node["Vertices"]
            vertices = []
            for i in range(0, len(flat_v), 3):
                vertex = Vertex()
                # Note that the X axis is inverted.
                vertex.position = Vector3(-flat_v[i], flat_v[i + 1], flat_v[i + 2]) * scale
                # TODO: normal, normal_w, uvs, tangents, bitangent, colors
                vertices.append(vertex)

            face_indices = node["PolygonVertexIndex"]

            # TODO: Note that FBX always stores faces as TRIANGLES, whereas FLVER can optionally use TRIANGLE_STRIP.
            #  No need to go through the hassle of converting to STRIP, so I'll keep it as TRIANGLES (another worthwhile
            #  strike against byte-perfect writes).

            face_set = FaceSet(flags=0, triangle_strip=False, use_backface_culling=False, unk_x06=0, vertex_indices=[])
            for i in range(0, len(face_indices), 3):
                # TODO: Meow reverses the indices in each face. Not sure why; they seem correctly ordered.
                #  He also resolves the negative indices by casting them to `ushort`, but I don't think that works.
                #  Maybe the `geometryContent` instance he uses has already done some conversion.
                face_set.vertex_indices += [face_indices[i], face_indices[i + 1], ~face_indices[i + 2]]
                if len(face_set.vertex_indices) + 3 > FACE_SET_MAX_TRIANGLES:
                    # New `FaceSet` needed.
                    face_set = FaceSet(
                        flags=0, triangle_strip=False, use_backface_culling=False, unk_x06=0, vertex_indices=[]
                    )
            face_set.vertex_indices = [~f if f < 0 else f for f in face_indices]

            # TODO: Trying to get Blender to export per-vertex normals instead of per-vertex-per-face.
            #  Also note


if __name__ == '__main__':
    dsr_map_piece_fbx_to_flver(Path("../../../../tests/darksouls1r/resources/m0000B0A16_blender_export.fbx"))
