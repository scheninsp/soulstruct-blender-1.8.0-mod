
import math
import numpy as np
from pathlib import Path

from soulstruct import DSR_PATH
from soulstruct.containers import Binder
from soulstruct.base.models.flver import FLVER
from soulstruct.utilities.maths import Matrix3, Vector3

from soulstruct_havok.utilities.vispy_window import VispyWindow


DSR_VANILLA_CHR_PATH = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (Vanilla Backup 1.03.1)/chr")


def main():
    chrbnd_path = DSR_VANILLA_CHR_PATH / "c5260.chrbnd.dcx"
    chrbnd = Binder.from_path(chrbnd_path)
    flver_entry = chrbnd["c5260.flver"]
    flver = flver_entry.to_binary_file(FLVER)

    bone_arma_translate = {bone.name: bone.get_absolute_translate_rotate(flver.bones)[0] for bone in flver.bones}
    bones_by_name = {bone.name: bone for bone in flver.bones}  # type: dict[str, FLVER.Bone]

    window = VispyWindow()
    default_scatter_color = "blue"
    default_line_color = "white"

    def highlight_bone(_bone_name):
        return False

    points = []
    highlight_points = []
    lines = []
    highlight_lines = []
    for bone_name, bone in bones_by_name.items():
        translation = bone_arma_translate[bone_name]
        print(f"   Bone {bone_name} arma translate: {translation}")
        highlight = highlight_bone(bone_name)
        (highlight_points if highlight else points).append(translation.to_xzy())

        if bone.parent_index != -1:
            parent_bone_name = flver.bones[bone.parent_index].name
            parent_translation = bone_arma_translate[parent_bone_name]
            (highlight_lines if highlight else lines).append(
                np.array([parent_translation.to_xzy(), translation.to_xzy()])
            )

    window.add_markers(np.array(points), face_color=default_scatter_color)
    if highlight_points:
        window.add_markers(np.array(highlight_points), face_color="red")
    for line in lines:
        window.add_line(line, line_color=default_line_color)
    for line in highlight_lines:
        window.add_line(line, line_color="yellow")

    window.add_axes()

    print("Running window...")
    window.show()
    window.run()


def test_chrtpf():
    from soulstruct.containers import Binder, TPF
    from soulstruct.base.textures.dds import DDS
    chrbnd = Binder.from_path(DSR_VANILLA_CHR_PATH / "c5260.chrbnd.dcx")
    chrbhd = chrbnd["c5260.chrtpfbhd"]
    chrbdt_path = DSR_VANILLA_CHR_PATH / "c5260.chrtpfbdt"
    chrbxf = Binder.from_bytes(chrbhd.data, chrbdt_path.read_bytes())
    print(chrbxf)
    for entry in chrbxf:
        tpf = entry.to_binary_file(TPF)
        tpf.textures[0].get_dds()


if __name__ == '__main__':
    # main()
    test_chrtpf()
