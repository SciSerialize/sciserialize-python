# -- encoding: utf-8 --

from distutils.core import setup

setup(name='SciSerialize',
      version='0.0dev',
      description='Serialize scientific data to JSON or MEssagePack',
      author='Siegfried Guendert',
      author_email='siegfried.guendert@googlemail.com',
      url='https://github.com/SiggiGue/SciSerialize',
      packages=['sciserialize'],
      py_modules=['coders', 'serializers'],
)
