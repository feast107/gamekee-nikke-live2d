"""
Setup script for gamekee-nikke-live2d.
"""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gamekee-nikke-live2d",
    version="0.1.0",
    author="",
    author_email="",
    description="Generate standalone GameKee NIKKE Spine live2d demo pages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=["gamekee_nikke_live2d"],
    python_requires=">=3.9",
    install_requires=[
        # Core runtime is browser-based (Spine 4.1). CLI uses stdlib only.
    ],
    entry_points={
        "console_scripts": [
            "gamekee-nikke-live2d=gamekee_nikke_live2d.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
