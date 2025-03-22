from setuptools import setup, find_packages

setup(
    name="bashCopilot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pyyaml",
    ],
    entry_points={
        'console_scripts': [
            'bcopilot=src.main:main',
        ],
    },
)
