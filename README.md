# Examples with Drake and ROS 2

This repo shows examples of using [Drake](https://drake.mit.edu/) and [ROS 2](https://www.ros.org/) together.
It uses the pydrake API and is of prototype quality.
For a similar effort in ROS 1, see [EricCousineau-TRI/repro `drake_ros1_hacks`](https://github.com/EricCousineau-TRI/repro/tree/master/ros/drake_ros1_hacks).

## Prerequisites

* Ubuntu Focal (20.04)
* [ROS 2 Rolling](https://index.ros.org/doc/ros2/Installation/Rolling/)
* [Some Drake binary installation from October 2020](https://drake.mit.edu/from_binary.html)
* A colcon workspace with [ros/sdformat\_urdf#1](https://github.com/ros/sdformat_urdf/pull/1)

Install ROS 2 Rolling using the [Linux binary instructions](https://index.ros.org/doc/ros2/Installation/Rolling/Linux-Install-Debians/).
Install the apt package `ros-rolling-desktop`.
Create a colcon workspace with [ros/sdformat\_urdf#1](https://github.com/ros/sdformat_urdf/pull/1).
Use `rosdep` to install `sdformat_urdf`'s dependencies with `rosdep install --rosdistro=rolling -i --from-paths path/to/ws/src`.
Extract the Drake binary installation, install it's prerequisites, and [use this Python virutalenv trick](https://drake.mit.edu/python_bindings.html#inside-virtualenv).

## Setup

Once the prerequisites are met, install `drake_ros` into the Drake virtualenv.

```
. path/to/drake/bin/activate
cd path/to/this/repo
cd drake_ros/
python setup.py develop
```

## ROS 2 tf and Robot Model Demo

This demo shows RViz visualizing a single UR10 robot being simulated by Drake.
Set up two terminals: one for launching RViz, and another for launching the Drake simulation.

```
. /opt/ros/rolling/setup.bash
. path/to/sdformat_urdf/ws/install/setup.bash
cd path/to/this/repo
rviz2 -d view.rviz
```

```
. /opt/ros/rolling/setup.bash
. path/to/sdformat_urdf/ws/install/setup.bash
. path/to/drake/bin/activate
cd path/to/this/repo
./ros2_demo.py
```

![ur10_rviz_drake](https://user-images.githubusercontent.com/4175662/90415417-e7976980-e065-11ea-9564-96c820f51680.gif)
