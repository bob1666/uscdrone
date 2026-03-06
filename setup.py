from setuptools import setup

setup(
    name="uscdrone",
    version="0.1",
    py_modules=["uscdrone"],
    install_requires=[
        "paho-mqtt==1.6.1",
    ],
)