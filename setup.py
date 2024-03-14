# requirements
# Usage: pip install -e .
from distutils.core import setup

install_requires=[
    'opencv-python',
],

setup(
   name='webcam_recorder_app',
   version='0.1',
   packages=['webcam_recorder_app'],
   license='MIT',
   install_requires=install_requires,
)

