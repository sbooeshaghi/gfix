from setuptools import find_packages, setup


def read(path):
    with open(path, "r") as f:
        return f.read()


long_description = read("README.md")

setup(
    name="gfix",
    version="0.0.0",
    url="https://github.com/sbooeshaghi/gfix",
    author="Sina Booeshaghi",
    author_email="sinab@berkeley.edu",
    maintainer="Sina Booeshaghi",
    maintainer_email="sinab@berkeley.edu",
    description="",  # noqa
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="",
    python_requires=">=3.6",
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    zip_safe=False,
    include_package_data=True,
    install_requires=read("requirements.txt").strip().split("\n"),
    entry_points={
        "console_scripts": ["gfix=gfix.main:main"],
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Utilities",
    ],
)
