from setuptools import setup, find_packages

setup(
    name="comps",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "protobuf>=4.21.0",
        "grpcio>=1.50.0"
    ]
)
