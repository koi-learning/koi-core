import setuptools

setuptools.setup(
    name='koi-core',
    version='0.3.7',
    packages=setuptools.find_packages(),
    scripts=['koi-worker.py'],
    install_requires=[
        "requests",
        "configargparse",
        "colorama",
    ]
 )
