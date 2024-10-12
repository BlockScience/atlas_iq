from setuptools import setup, find_packages

setup(
    name='atlas',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add your project dependencies here
    ],
    entry_points={
        'console_scripts': [
            'atlas=atlas.interfaces.cli:main',
        ],
    },
)
