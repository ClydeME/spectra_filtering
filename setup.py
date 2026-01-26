from setuptools import setup, find_packages

setup(
    name='TARDIS_Spectrum_Filtering',
    version='1.0',

    url='https://github.com/ClydeME/spectra_filtering',
    author='Clyde Watson',
    author_email='clyde.n.watson@gmail.com',

    packages=find_packages(),

    install_requires=[
        "matplotlib",
        "numpy",
        "astropy",
        "networkx",
        "requests",
        "pyyaml",
    ],
)