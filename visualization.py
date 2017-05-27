'''Functions for generating visualizations from NiTE skeletons'''

import logging
from math import inf

from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from skeletons import (NITE_JOINT_HEAD, NITE_JOINT_LEFT_ELBOW,
                       NITE_JOINT_LEFT_FOOT, NITE_JOINT_LEFT_HAND,
                       NITE_JOINT_LEFT_HIP, NITE_JOINT_LEFT_KNEE,
                       NITE_JOINT_LEFT_SHOULDER, NITE_JOINT_NECK,
                       NITE_JOINT_RIGHT_ELBOW, NITE_JOINT_RIGHT_FOOT,
                       NITE_JOINT_RIGHT_HAND, NITE_JOINT_RIGHT_HIP,
                       NITE_JOINT_RIGHT_KNEE, NITE_JOINT_RIGHT_SHOULDER,
                       NITE_JOINT_TORSO)

# pylint: disable=C0103
log = logging.getLogger(__name__)

links = [
    (NITE_JOINT_HEAD, NITE_JOINT_NECK),
    (NITE_JOINT_NECK, NITE_JOINT_LEFT_SHOULDER),
    (NITE_JOINT_NECK, NITE_JOINT_RIGHT_SHOULDER),
    (NITE_JOINT_LEFT_SHOULDER, NITE_JOINT_LEFT_ELBOW),
    (NITE_JOINT_LEFT_ELBOW, NITE_JOINT_LEFT_HAND),
    (NITE_JOINT_RIGHT_SHOULDER, NITE_JOINT_RIGHT_ELBOW),
    (NITE_JOINT_RIGHT_ELBOW, NITE_JOINT_RIGHT_HAND),
    (NITE_JOINT_NECK, NITE_JOINT_TORSO),
    (NITE_JOINT_TORSO, NITE_JOINT_LEFT_HIP),
    (NITE_JOINT_LEFT_HIP, NITE_JOINT_LEFT_KNEE),
    (NITE_JOINT_LEFT_KNEE, NITE_JOINT_LEFT_FOOT),
    (NITE_JOINT_TORSO, NITE_JOINT_RIGHT_HIP),
    (NITE_JOINT_RIGHT_HIP, NITE_JOINT_RIGHT_KNEE),
    (NITE_JOINT_RIGHT_KNEE, NITE_JOINT_RIGHT_FOOT)
]


def find_bounds(skeleton_data):
  '''Utility function to find the limits of each dimension
  Args:
    skeleton_data ((skeleton, offset) list): The data to animate

  Returns:
    ((x min, x_max), (y min, y max), (z min, z max))
  '''
  x_min = inf
  x_max = -inf
  y_min = inf
  y_max = -inf
  z_min = inf
  z_max = -inf
  for frame in skeleton_data:
    for joint in frame[0].joints:
      x_min, x_max = min(x_min, joint.position.x), max(x_max, joint.position.x)
      y_min, y_max = min(y_min, joint.position.y), max(y_max, joint.position.y)
      z_min, z_max = min(z_min, joint.position.z), max(z_max, joint.position.z)
  return ((x_min, x_max), (y_min, y_max), (z_min, z_max))


def initialize_plots(skeleton_data):
  '''Utility function to find the limits of each dimension
  Args:
    skeleton_data ((skeleton, offset) list): The data to animate

  Returns:
    figure, axes, plots
  '''
  fig = plt.figure()
  axes = fig.add_subplot(111, projection='3d')
  axes.view_init(elev=270, azim=90)
  (x_min, x_max), (y_min, y_max), (z_min, z_max) = find_bounds(skeleton_data)
  # We do seemingly weird assignments of bounds here, but it's due to the conventions used by NiTE
  axes.set_xlabel('X')
  axes.set_ylabel('Y')
  axes.set_zlabel('Z')
  axes.set_xlim(left=x_max, right=x_min)
  axes.set_ylim(bottom=y_min, top=y_max)
  axes.set_zlim(bottom=z_max, top=z_min)
  log.info('Making inital plots')
  plots = {link: axes.plot([0], [0], [0], 'bo-')[0] for link in links}
  return fig, axes, plots


def make_video(skeleton_data, out_filename):
  '''Creates an animation from skeleton data
  Args:
    skeleton_data ((skeleton, offset) list): The data to animate
    out_filename (string): The file in which to save the video

  Returns:
    Nothing
  '''
  # Note that we make the assumption that the interval between frames is equal throughout. This
  # seems to hold mostly true, empirically.
  interval_microseconds = skeleton_data[1][1] - skeleton_data[0][1]
  interval = int(interval_microseconds / 1e3)
  fig, axes, plots = initialize_plots(skeleton_data)

  def init():
    '''Initializes the animation'''
    for link in links:
      plots[link].set_xdata([0])
      plots[link].set_ydata([0])
      plots[link].set_3d_properties([0])
    return tuple(plots.values())

  def animate(i):
    '''Render each frame'''
    frame = skeleton_data[i][0]
    skel = {link: None for link in links}
    for joint in frame.joints:
      skel[joint.jointType] = joint.position

    for link in links:
      top, bottom = link
      if skel[top] and skel[bottom]:
        xs = (skel[top].x, skel[bottom].x)
        ys = (skel[top].y, skel[bottom].y)
        zs = (skel[top].z, skel[bottom].z)
        plots[link].set_xdata(xs)
        plots[link].set_ydata(ys)
        plots[link].set_3d_properties(zs)
    return tuple(plots.values())

  log.info('Creating animation')
  video = animation.FuncAnimation(
      fig,
      animate,
      init_func=init,
      frames=len(skeleton_data),
      interval=interval,
      blit=True
  )

  plt.show()
  log.info(f'Saving video to {out_filename}')
  video.save(out_filename, fps=30, extra_args=['-vcodec', 'libx264'])


def make_image(skeleton_data, out_filename):
  '''Generate a static image of the skeleton
  Args:
    skeleton_data ((skeleton, offset) list): The data to visualize. The first provided frame is
    chosen.

    out_filename (string): The file in which to save the image.

  Returns:
    Nothing
  '''
  fig, axes, plots = initialize_plots(skeleton_data)
  frame = skeleton_data[0][0]
  skel = {link: None for link in links}
  for joint in frame.joints:
    skel[joint.jointType] = joint.position

  for link in links:
    top, bottom = link
    if skel[top] and skel[bottom]:
      xs = (skel[top].x, skel[bottom].x)
      ys = (skel[top].y, skel[bottom].y)
      zs = (skel[top].z, skel[bottom].z)
      plots[link].set_xdata(xs)
      plots[link].set_ydata(ys)
      plots[link].set_3d_properties(zs)
  plt.show()
  log.info(f'Saving image to {out_filename}')
  plt.savefig(out_filename)
