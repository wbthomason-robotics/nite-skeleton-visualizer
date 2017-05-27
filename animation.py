'''Functions for generating animations from NiTE skeletons'''

import logging

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
log = logging.getLogger('viewer')

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


def make_video(skeleton_data, out_filename):
  '''Creates an animation from skeleton data
  Args:
    skeleton_data ((skeleton, offset) list): The data to animate
    out_filename (string): The file in which to save the video

  Returns:
    Nothing
  '''
  fig = plt.figure()
  axes = Axes3D(fig)
  # Note that we make the assumption that the interval between frames is equal throughout. This
  # seems to hold mostly true, empirically.
  interval_microseconds = skeleton_data[1][1] - skeleton_data[0][1]
  interval = interval_microseconds * 1e3

  plots = {link: axes.plot([], [], zs=[], lw=2)[0] for link in links}
  # plot = {link: axes.plot([], [], zs=[], lw=2)[0] for link in links}

  def init():
    '''Initializes the animation'''
    for link in links:
      plots[link].set_data([], [])
      plots[link].set_3d_properties(zs=[])
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
        plots[link].set_data(xs, ys)
        plots[link].set_3d_properties(zs=zs)
    return tuple(plots.values())

  video = animation.FuncAnimation(
      fig,
      animate,
      init_func=init,
      frames=len(skeleton_data),
      interval=interval,
      blit=True
  )

  video.save(out_filename, fps=30, extra_args=['-vcodec', 'libx264'])
  plt.show()
