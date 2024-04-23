import os
import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    package_name = 'semantic_rules'
    #
    # Command-line args?
    #
    model = LaunchConfiguration("model")  # TODO: why is this needed?
    model_cmd = DeclareLaunchArgument(
        "model",
        default_value="yolov8m.pt",
        description="Model name or path")

    #
    # NODE ARGS
    #
    # detection to obstacle
    obstacle_topic = "detection"
    detections_topic = "/yolo/detections_3d"

    parameters_dto = []
    remappings_dto = [
        ('/obstacles', obstacle_topic),
        ('/detections_3d', detections_topic),
    ]
    # kf hungarian tracker
    tracker_config = os.path.join(
        get_package_share_directory('kf_hungarian_tracker'),
        'config',
        'kf_hungarian.yaml'
    )
    tracker_remappings = [
            # ("tracking", "kf_tracking"),
            # ("detection", "/yolo/detections_3d")
    ]

    # semantic rules
    # TODO: rule params to config
    rule1_parameters = [{
        'direction_type': 'front',
        'cost_type': 'velocity_falloff',
        'falloff_type': 'abs_percentage',
        'base_cost': 20.0,
        'falloff': -0.20,
        'min_range': 0,
        'velocity_segments': 5,
    }]
    rule_tracking_topic = "tracking"
    # detections_topic = "/yolo/detections_3d"
    rule1_remappings = [
        # ('costmap_publisher', '/costmap/rule1'),
        ('tracking', rule_tracking_topic),
        # ('tracking_marker', '/yolo/dgb_kp_markers'),
    ]

    #
    # NODES
    #
    detection_converter = Node(
        package=package_name, executable='detection_converter_node', output='screen',
        parameters=parameters_dto,
        remappings=remappings_dto)

    kf_hungarian_node = Node(
        package='kf_hungarian_tracker',
        name='kf_hungarian_node',
        executable='kf_hungarian_node',
        parameters=[tracker_config],
        remappings=tracker_remappings
    )

    rule1 = Node(
            package=package_name, executable='detection_costmap_rule', output='screen',
            parameters=rule1_parameters,
            remappings=rule1_remappings)

    ld = LaunchDescription()

    # ld.add_action(model_cmd)
    ld.add_action(detection_converter)
    ld.add_action(kf_hungarian_node)
    ld.add_action(rule1)

    return ld