# GraspGen Justfile
# Usage: just <recipe> [args]

# Default gripper configs
franka  := "GraspGenModels/checkpoints/graspgen_franka_panda.yml"
robotiq := "GraspGenModels/checkpoints/graspgen_robotiq_2f_140.yml"
suction := "GraspGenModels/checkpoints/graspgen_single_suction_cup_30mm.yml"
spot    := "GraspGenModels/checkpoints/graspgen_spot_gripper.yml"

# Default values
gripper := franka     # spot
mesh    := "assets/objects/box.usd"
scale   := "1.0"
output  := "output_grasps.yaml"
n       := "400"

# List available recipes
default:
    @just --list

# Run grasp generation on a mesh file (no visualization)
grasp mesh=mesh gripper=gripper scale=scale output=output n=n:
    uv run python scripts/demo_object_mesh.py \
        --mesh_file {{mesh}} \
        --mesh_scale {{scale}} \
        --gripper_config {{gripper}} \
        --output_file {{output}} \
        --num_grasps {{n}} \
        --no-visualization

# Run grasp generation on a mesh file (with visualization)
grasp-vis mesh=mesh gripper=gripper scale=scale n=n:
    uv run python scripts/demo_object_mesh.py \
        --mesh_file {{mesh}} \
        --mesh_scale {{scale}} \
        --gripper_config {{gripper}} \
        --num_grasps {{n}}

# Run grasp on the drill (quick test)
drill gripper=gripper:
    just grasp assets/objects/drill.usd {{gripper}} 0.01 drill_grasps.yaml

# Run grasp on the bottle (quick test)
bottle gripper=gripper:
    just grasp assets/objects/bottle.usd {{gripper}} 0.01 bottle_grasps.yaml

# Run grasp on a point cloud file
grasp-pc sample_dir gripper=gripper:
    uv run python scripts/demo_object_pc.py \
        --sample_data_dir {{sample_dir}} \
        --gripper_config {{gripper}}

# Run grasp on a scene point cloud
grasp-scene sample_dir gripper=gripper:
    uv run python scripts/demo_scene_pc.py \
        --sample_data_dir {{sample_dir}} \
        --gripper_config {{gripper}}

# Convert an OBJ mesh to USD
convert-usd obj_file output_file:
    uv run python scripts/convert_obj_to_usd.py \
        --input_file {{obj_file}} \
        --output_file {{output_file}}

# Run grasp generation then open viser viewer in the browser
grasp-and-vis mesh=mesh gripper=gripper scale=scale output=output n=n:
    uv run python scripts/demo_object_mesh.py \
        --mesh_file {{mesh}} \
        --mesh_scale {{scale}} \
        --gripper_config {{gripper}} \
        --output_file {{output}} \
        --num_grasps {{n}}

# Save an existing grasps YAML into a USD file (for Isaac Sim / Omniverse)
# Usage: just save-usd <usd_file> <grasps_yaml> [output] [gripper_name]
# Example: just save-usd assets/objects/drill.usd drill_grasp.yaml drill_with_grasps.usd spot_gripper
save-usd usd_file grasps_yaml output="" gripper_name="spot_gripper":
    uv run python scripts/save_grasps_to_usd.py \
        --usd_file {{usd_file}} \
        --grasps_yaml {{grasps_yaml}} \
        --output {{output}} \
        --gripper_name {{gripper_name}}
