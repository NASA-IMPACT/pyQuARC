import setuptools
from distutils.util import convert_path

version_path = convert_path('pyQuARC/version.txt')
with open(version_path) as version_file:
    __version__ = version_file.read().strip()

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()


with open("requirements.txt", "r", encoding="utf-8") as requirement_file:
    requirements = requirement_file.readlines()


setuptools.setup(
    name="pyQuARC",
    version=__version__,
    author="NASA IMPACT",
    author_email="teamimpact@uah.edu",
    description="The pyQuARC tool is an open source library for Earth Observation Metadata quality and assessment. The pyQuARC tool reads and evaluates metadata records with a focus on the consistency and robustness of the metadata. pyQuARC flags opportunities to improve or add to contextual metadata information in order to help the user connect to relevant data products. pyQuARC also ensures that information common to both the data product and the file-level metadata are consistent and compatible. pyQuARC frees up human evaluators to make more sophisticated assessments such as whether an abstract accurately describes the data and provides the correct contextual information. The base pyQuARC package assesses descriptive metadata used to catalog Earth observation data products and files. As open source software, pyQuARC can be adapted and customized by data providers to allow for quality checks that evolve with their needs, including checking metadata not covered in base package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NASA-IMPACT/pyQuARC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache License, Version 2.0",
        "Operating System :: OS Independent",
    ],
    keywords='validation metadata cmr quality',
    python_requires='>=3.8',
    install_requires=requirements,
    package_data={'pyQuARC': ['schemas/*', '*.txt'], 'tests': ['fixtures/*']},
    include_package_data=True,
)
