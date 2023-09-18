import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arinfopy",
    version="3.2.1",
    author="Giuseppe Carlino",
    author_email="g.carlino@simularia.it",
    description="A package to read and write ADSO/BIN data files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU GPLv2",
    url="https://github.com/Simularia/arinfopy",
    install_requires=[
        "numpy>=1.14.3",
        "pytz>=2023.3.post1"
    ],
    packages=[
        "arinfopy",
        "arinfopy.cli"],
    entry_points={
        "console_scripts":
        [
            "arinfopy=arinfopy.cli.arinfopy:arinfopy"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)
