import functools
import math

import geometry_msgs.msg
import numpy

from pydrake.common.value import AbstractValue
from pydrake.math import RotationMatrix
from pydrake.multibody.tree import Joint_
from pydrake.multibody.tree import RevoluteJoint_
from pydrake.systems.framework import LeafSystem
from pydrake.systems.framework import BasicVector_

from visualization_msgs.msg import InteractiveMarker
from visualization_msgs.msg import InteractiveMarkerControl
from visualization_msgs.msg import InteractiveMarkerFeedback
from visualization_msgs.msg import Marker


class MoveableJoints(LeafSystem):

    def __init__(self, server, tf_buffer, joints):
        super().__init__()

        # TODO(sloretz) do I need to store allllll of this in the context?
        # if so, how tf do I get the context in callbacks?
        self._tf_buffer = tf_buffer

        # System will publish transforms for these joints only
        self._joints = tuple(joints)

        if 0 == len(self._joints):
            raise ValueError('Need at least one joint')

        for joint in self._joints:
            if not Joint_.is_subclass_of_instantiation(type(joint)):
                raise TypeError('joints must be an iterable of Joint_[T]')

        self._server = server

        self._joint_states = [0.0] * len(self._joints)
        # Map joint names to indexes in joint_states
        self._joint_indexes = {j.name(): i for j, i in zip(self._joints, range(len(self._joints)))}

        for joint in self._joints:
            print('Making stuff for', joint.name())
            if RevoluteJoint_.is_subclass_of_instantiation(type(joint)):
                server.insert(
                    self._make_revolute_marker(joint),
                    feedback_callback=functools.partial(self._revolute_feedback, joint))
            else:
                # TODO(sloretz) support more than revolute joints
                raise TypeError('joints must be an iterable of RevoluteJoint_[T]')
            break  # xxx

        server.applyChanges()

        self.DeclareVectorOutputPort(
            'joint_states',
            BasicVector_[float](len(self._joint_states)),
            self._do_get_joint_states)

    def _revolute_feedback(self, joint, feedback):
        if feedback.event_type != InteractiveMarkerFeedback.MOUSE_UP:
            # Only care about pose updates happening after MOUSE_UP
            return

        if feedback.control_name != f'rotate_axis_{joint.name()}':
            print(f'Unexpected control name {feedback.control_name} with joint {joint.name()}')
            # Unexpected control name
            return

        expected_frame = joint.child_body().body_frame().name()

        if expected_frame != feedback.header.frame_id:
            print(expected_frame, point_stamped.header.frame_id)
            # TODO(sloretz) fix tf2_geometry_msgs_py :(
            # transformed_point = self._tf_buffer.transform(point_stamped, self._frame_id)
            print("TODO accept feedback in different frame")
            return

        # print(feedback.pose.orientation)
        # print(dir(joint), joint.revolute_axis())
        angle = 2.0 * math.acos(feedback.pose.orientation.w)
        self._joint_states[self._joint_indexes[joint.name()]] = angle

    def _do_get_joint_states(self, context, data):
        data.SetFromVector(self._joint_states)

    def _make_revolute_marker(self, revolute_joint: RevoluteJoint_):
        int_marker = InteractiveMarker()
        int_marker.header.frame_id = revolute_joint.child_body().body_frame().name()
        int_marker.name = revolute_joint.name()
        int_marker.scale = 0.3
        # print(f'marker name {int_marker.name}')

        # https://math.stackexchange.com/q/476311
        # RViz ROTATE_AXIS marker rotates around X axis in child frame by default
        # Find rotation matrix transforming X asis to Joint axis
        # Then convert that rotation matrix to quaternion for the interactive marker
        x_axis = (1, 0, 0)
        joint_axis = revolute_joint.revolute_axis()
        joint_axis_hat = joint_axis / numpy.linalg.norm(joint_axis)
        v = numpy.cross(x_axis, joint_axis_hat)
        c = numpy.dot(x_axis, joint_axis_hat)
        v_sub_x = numpy.array((
            (0, -v[2], v[1]),
            (v[2], 0, -v[0]),
            (-v[1], v[0], 0)))
        identity = numpy.array((
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)))
        i_plus_v_sub_x = numpy.add(identity, v_sub_x)
        v_sub_x_squared = numpy.multiply(v_sub_x, v_sub_x)
        rotation_matrix = numpy.add(i_plus_v_sub_x, v_sub_x_squared * (1.0 / (1.0 + c)))
        pydrake_quat = RotationMatrix(rotation_matrix).ToQuaternion()
        print(pydrake_quat)

        # axis/angle with angle = 0 to quaternion
        # ax, ay, az = revolute_joint.revolute_axis()
        # print(ax, ay, az)
        # int_marker.pose.orientation.w = math.cos(0)
        # int_marker.pose.orientation.x = ax * math.sin(0)
        # int_marker.pose.orientation.y = ay * math.sin(0)
        # int_marker.pose.orientation.z = az * math.sin(0)
        int_marker.pose.orientation.w = pydrake_quat.w()
        int_marker.pose.orientation.x = pydrake_quat.x()
        int_marker.pose.orientation.y = pydrake_quat.y()
        int_marker.pose.orientation.z = pydrake_quat.z()

        joint_control = InteractiveMarkerControl()
        joint_control.always_visible = True
        joint_control.name = f'rotate_axis_{revolute_joint.name()}'
        joint_control.interaction_mode = InteractiveMarkerControl.ROTATE_AXIS

        # TODO (sloretz) Orientation needs to match joint axis
        int_marker.controls.append(joint_control)
        return int_marker