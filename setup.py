import os
from setuptools import setup

setup(
    name = "rippleTank",
    version = "0.0.0",
    author = "Juan Barbosa",
    author_email = "js.barbosa10@uniandes.edu.co",
    description = ('Build to serve at UniAndes.'),
    license = "GPL",
    keywords = "example documentation tutorial",
    packages=['rippleTank'],
    install_requires=['matplotlib', 'numpy'],
    long_description="TEMP",#read('README'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
)
