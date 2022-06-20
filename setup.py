import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='koi-core',
    version='0.3.8',
    packages=setuptools.find_packages(),
    scripts=['koi-worker.py'],
    install_requires=[
        "requests",
        "configargparse",
        "colorama",
    ],
    python_requires=">=3.6",
    url="https://github.com/koi-learning/koi-core",
    project_urls={
        "Github": "https://github.com/koi-learning/koi-core",
        "Bug Tacker": "https://github.com/koi-learning/koi-core/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
 )
