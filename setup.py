from setuptools import setup, find_packages

major = 0

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
    url='https://github.com/Lamden/contracting',
    author='Lamden',
    author_email='team@lamden.io',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
    include_package_data=True,
)
