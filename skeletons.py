'''Utility functions and values for dealing with NiTE skeletons'''

# Copied from the primesense python module because NiTE can be hard to find
NITE_JOINT_HEAD = 0
NITE_JOINT_NECK = 1
NITE_JOINT_LEFT_SHOULDER = 2
NITE_JOINT_RIGHT_SHOULDER = 3
NITE_JOINT_LEFT_ELBOW = 4
NITE_JOINT_RIGHT_ELBOW = 5
NITE_JOINT_LEFT_HAND = 6
NITE_JOINT_RIGHT_HAND = 7
NITE_JOINT_TORSO = 8
NITE_JOINT_LEFT_HIP = 9
NITE_JOINT_RIGHT_HIP = 10
NITE_JOINT_LEFT_KNEE = 11
NITE_JOINT_RIGHT_KNEE = 12
NITE_JOINT_LEFT_FOOT = 13
NITE_JOINT_RIGHT_FOOT = 14


def filter_calibrating(skeleton_data):
  '''Remove frames where NiTE is calibrating the skeleton
  Args:
    skeleton_data ((skeleton, timestamp) list): The skeletons to filter

  Returns:
    The filtered list of (skeleton, timestamp) pairs
  '''
  # Value taken from the NiTE source
  skeleton_tracked_state = 2
  return [(s, t) for (s, t) in skeleton_data if s.state == skeleton_tracked_state]


def timestamps_to_deltas(skeleton_data, start):
  '''Change timestamps to offsets into the recording
  Args:
    skeleton_data ((skeleton, timestamp) list): The timestamps to transform
    start (int): The timestamp from the first frame including calibration frames

  Returns:
    The list of (skeleton, offset) pairs
  '''
  return [(s, t - start) for (s, t) in skeleton_data]
