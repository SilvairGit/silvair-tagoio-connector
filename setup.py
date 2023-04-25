#!python
import os

from setuptools import find_packages, setup

setup(
    name="silvair-tagio-connector",
    author_email="michal.lowas-rzechonek@silvair.com",
    description=("Bridge between Silvair's Low-Latency API and tago.io"),
    url="https://github.com/SilvairGit/silvair-tagoio-connector.git",
    packages=find_packages(exclude=("test*",)),
    include_package_data=True,
    python_requires=">=3.8.0",
    setup_requires=[
        "pip-pin>=0.0.9",
    ],
    install_requires=[
        "pycapnp",
        "requests",
        "websockets",
    ],
    tests_require=[],
    develop_requires=[
        "black",
        "isort",
    ],
    entry_points=dict(
        console_scripts=[
            "tagio_connector = tagoio_connector.main:main",
        ]
    ),
)
