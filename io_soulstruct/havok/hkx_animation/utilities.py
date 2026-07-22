from __future__ import annotations

__all__ = [
    "HKXAnimationImportError",
    "HKXAnimationExportError",
    "get_armature_frames",
    "get_root_motion",
    "get_animation_name",
]

import numpy as np

from soulstruct_havok.utilities.maths import TRSTransform
from soulstruct_havok.wrappers.hkx2015 import AnimationHKX, SkeletonHKX, ANIBND


class HKXAnimationImportError(Exception):
    """Exception raised during HKX animation import."""
    pass


class HKXAnimationExportError(Exception):
    """Exception raised during HKX animation export."""
    pass


def get_armature_frames(
    animation_hkx: AnimationHKX, skeleton_hkx: SkeletonHKX
) -> list[dict[str, TRSTransform]]:
    """Get a list of animation frame dictionaries, which each map bone names to armature-space transforms that frame.

    Bone names are resolved from the skeleton via ``transformTrackToBoneIndices`` in the animation binding,
    NOT from ``annotationTracks`` (which may be empty for some game versions like Elden Ring).
    """

    # Create ANIBND with just this animation (always using dummy/default ID 0) to get advanced method access.
    anibnd = ANIBND(skeleton_hkx=skeleton_hkx, animations_hkx={0: animation_hkx}, default_anim_id=0)

    # Build track index -> bone name mapping from skeleton (robust against empty annotationTracks).
    track_bone_indices = animation_hkx.animation_container.animation_binding.transformTrackToBoneIndices
    skeleton = skeleton_hkx.skeleton

    arma_frames = []
    for frame_index in range(len(anibnd[0].interleaved_data)):
        track_transforms = anibnd.get_all_armature_space_transforms_in_frame(frame_index)
        # Get dictionary mapping Blender bone names to (game) armature space transforms this frame.
        frame_dict = {}
        for track_index, transform in enumerate(track_transforms):
            bone_index = track_bone_indices[track_index]
            bone_name = skeleton.bones[bone_index].name
            frame_dict[bone_name] = transform
        arma_frames.append(frame_dict)
    return arma_frames


def get_root_motion(animation_hkx: AnimationHKX, swap_yz=True) -> np.ndarray | None:
    try:
        root_motion = animation_hkx.animation_container.get_reference_frame_samples()
    except (ValueError, TypeError):
        return None

    if swap_yz:
        # Swap Y and Z axes and negate rotation (now around Z axis). Array is read-only, so we construct a new one.
        root_motion = np.c_[root_motion[:, 0], root_motion[:, 2], root_motion[:, 1], -root_motion[:, 3]]
    return root_motion


def get_animation_name(animation_id: int, template: str, prefix="a"):
    """Takes a template like '##_####' and converts `animation_id` int (e.g. 13000) to a string (e.g. 'a01_3000')."""
    parts = template.split('_')
    string_parts = []
    animation_id = str(animation_id)

    if len(template.replace("_", "")) < len(animation_id):
        raise ValueError(
            f"Animation ID '{animation_id}' is too long for template '{template}'."
        )

    for part in reversed(parts):
        length = len(part)  # number of digits we want to take from the end of the animation ID
        string_parts.append(animation_id[-length:].zfill(length))
        animation_id = animation_id[:-length]

    return prefix + '_'.join(reversed(string_parts))
