from setuptools import setup, find_packages

setup(
    name="vryndara",
    version="0.1.0",
    packages=find_packages(), # Automatically finds 'kernel', 'agents', etc.
    install_requires=[
        "grpcio",
        "grpcio-tools",
        "protobuf",
    ],
)