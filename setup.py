# -- encoding: utf-8 --

from setuptools import setup, find_packages

setup(name='SciSerialize',
      version='0.0dev',
      description='Serialize scientific data to JSON or MessagePack.',
      author='Siegfried Guendert',
      author_email='siegfried.guendert@googlemail.com',
      url='https://github.com/SiggiGue/SciSerialize',
      license='MIT',
      keywords='scientific serialize json msgpack',
      packages=find_packages(exclude=('docs',)),
      install_requires=['msgpack-python'],
)
