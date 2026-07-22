from pathlib import Path

from soulstruct import FLVER
from soulstruct.eldenring.containers import DivBinder
from soulstruct_havok.wrappers.hkx2018 import SkeletonHKX, AnimationHKX


def test_flver():
    model = "c2010"
    chrbnd_path = Path(rf"C:\Steam\steamapps\common\ELDEN RING (Modding 1.10)\Game\chr\{model}.chrbnd.dcx")
    chrbnd = DivBinder.from_path(chrbnd_path)
    # print(chrbnd)

    flver = FLVER.from_binder(chrbnd, f"{model}.flver")

    submesh = flver.submeshes[-1]  # sword

    print(submesh.default_bone_index)
    print(submesh.vertices[:10])
    for v in range(10):
        bone_indices = submesh.vertices[v]["bone_indices"]
        bone_weights = submesh.vertices[v]["bone_weights"]
        print([flver.bones[i].name for i in bone_indices])
        print(bone_weights)


def main():
    model = "c2010"
    anibnd_path = Path(rf"C:\Steam\steamapps\common\ELDEN RING (Modding 1.10)\Game\chr\{model}.anibnd.dcx")
    anibnd = DivBinder.from_path(anibnd_path)
    # print(anibnd)

    skeleton = SkeletonHKX.from_binder(anibnd, "skeleton.hkx")
    a000 = AnimationHKX.from_binder(anibnd, "a000_000000.hkx")

    for anno in a000.animation_container.animation.annotationTracks:
        print(anno.trackName)

    # print(skeleton.get_root_tree_string())
    # print(a000.base_hkx_repr())
    # print(a000.get_root_tree_string())


if __name__ == '__main__':
    # main()
    test_flver()
