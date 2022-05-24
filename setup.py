import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nwrobel-mlu-dev-api",
    version="2022.05.24.1",
    author="Nick Wrobel",
    author_email="nick@nwrobel.com",
    description="Package containing various modules dealing with audio files and music libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nwrobel/mlu-dev-api",
    packages=setuptools.find_packages(),
    install_requires=[], # use to define external packages to install as well as dependencies to this package
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)