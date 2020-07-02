import setuptools


name = "jig-py"
version = "0.0.2"
description = "Jig for Python"
dependencies = []

with open("README.md", "r") as fh:
    long_description = fh.read()

packages = [
    package for package in setuptools.find_packages() if package.startswith("jig")
]

namespaces = ["jig"]

setuptools.setup(
    name=name,
    version=version,
    author="Jig-Py Project Team",
    author_email="dev+jig-py-contact@levii.co.jp",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/levii/jig-py",
    packages=packages,
    namespaces=namespaces,
    entry_points={"console_scripts": ["jig-py = jig.cli.main:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=dependencies,
)
