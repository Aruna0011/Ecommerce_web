import os
from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="ecommerce",
    version="0.1.0",
    packages=find_packages(include=['ecommerce*', 'truckbrand*', 'cart*']),
    include_package_data=True,
    package_data={
        '': ['*.html', '*.css', '*.js', '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.py'],
    },
    install_requires=required,
    python_requires=">=3.10,<3.11",
    author="Your Name",
    author_email="your.email@example.com",
    description="E-commerce website for TruckBrand",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Aruna0011/Ecommerce_web",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Framework :: Django :: 4.2",
        "Operating System :: OS Independent",
    ],
)
