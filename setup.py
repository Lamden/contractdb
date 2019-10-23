from setuptools import setup, find_packages
from setuptools.extension import Extension

from Cython.Build import cythonize
from Cython.Distutils import build_ext

__version__ = '0.1.1'

requirements = [
    'pyzmq',
    'ecdsa'
]


setup(
    name='contractdb',
    version=__version__,
    description='Python-based smart contract language and interpreter.',
    packages=find_packages(),
    install_requires=requirements,
    author='Lamden',
    author_email='team@lamden.io',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
    include_package_data=True,
    ext_modules=cythonize(
        Extension('contractdb.*', ['contractdb']),
        build_dir='build',
    ),
    cmdclass=dict(
        build_ext=build_ext
    )
)
