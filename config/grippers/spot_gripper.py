import torch
import numpy as np
import trimesh
import trimesh.transformations as tra
from grasp_gen.robot import load_control_points_core, load_default_gripper_config
from pathlib import Path


def _load_mesh(fn):
    """Load a mesh file, flattening a Scene into a single Trimesh if needed (e.g. .obj with .mtl)."""
    mesh = trimesh.load(fn)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(list(mesh.geometry.values()))
    return mesh


class GripperModel:
    def __init__(self, data_root_dir=None):
        if data_root_dir is None:
            data_root_dir = f"{Path(__file__).parent.parent.parent}/assets/spot"

        # main wrist body that the finger and jaw are mounted to
        fn_wr1 = data_root_dir + "/meshes/arm/visual/arm_link_wr1.obj"
        # single moveable finger assembly
        fn_fngr = data_root_dir + "/meshes/gripper/visual/arm_link_fngr.obj"

        self.base = _load_mesh(fn_wr1)
        self.finger = _load_mesh(fn_fngr)

        # joint arm_f1x (per spot_gripper.urdf):
        #   origin xyz="0.11745 0.0 0.014820"   rpy="0 0 0"
        #   axis   xyz="0.0 1.0 0.0"
        #   limit  lower="-1.5708"  upper="0.0"
        #            ^-- open (-π/2)  ^-- closed (0 rad)
        #
        # for collision checking the gripper is in approach configuration = OPEN (-π/2 rad).
        # the finger transform in wr1 frame is:  T = T_translation @ R_y(-π/2)
        #
        # R_y(-π/2):
        #   [[ 0,  0, -1],
        #    [ 0,  1,  0],
        #    [ 1,  0,  0]]
        T_fngr_open = np.eye(4, dtype=np.float64)
        T_fngr_open[:3, 3] = [0.11745, 0.0, 0.014820]
        T_fngr_open[:3, :3] = np.array(
            [[0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]
        )
        self.finger.apply_transform(T_fngr_open)

        self.mesh = trimesh.util.concatenate([self.base, self.finger])

    def get_gripper_collision_mesh(self):
        return self.mesh

    def get_gripper_visual_mesh(self):
        return self.mesh


def get_gripper_offset_bins():
    # finger opening range: -pi/2 (open) → 0.0 (closed).
    # width bins estimated from maximum aperture of ~0.19 m.
    # weights kept consistent with other grippers (uniform distribution shape).
    offset_bins = [
        0.0,
        0.019,
        0.038,
        0.057,
        0.076,
        0.095,
        0.114,
        0.133,
        0.152,
        0.171,
        0.19,
    ]
    offset_bin_weights = [
        0.16652107,
        0.21488856,
        0.37031708,
        0.55618503,
        0.75124664,
        0.93943357,
        1.07824539,
        1.19423112,
        1.55731375,
        3.17161779,
    ]
    return offset_bins, offset_bin_weights


def load_control_points() -> torch.Tensor:
    """
    Load the control points for the gripper, used for training.
    Returns a tensor of shape (4, N) where N is the number of control points.
    """
    gripper_config = load_default_gripper_config(Path(__file__).stem)
    control_points = load_control_points_core(gripper_config)
    control_points = np.vstack([control_points, np.zeros(3)])
    control_points = np.hstack([control_points, np.ones([len(control_points), 1])])
    control_points = torch.from_numpy(control_points).float()
    return control_points.T


def load_control_points_for_visualization():

    gripper_config = load_default_gripper_config(Path(__file__).stem)

    control_points = load_control_points_core(gripper_config)

    mid_point = (control_points[0] + control_points[1]) / 2

    control_points = [
        control_points[-2],
        control_points[0],
        mid_point,
        [0, 0, 0],
        mid_point,
        control_points[1],
        control_points[-1],
    ]
    return [
        control_points,
    ]
