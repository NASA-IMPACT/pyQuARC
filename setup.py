import setuptools

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", "r", encoding="utf-8") as requirement_file:
    requirements = requirement_file.readlines()
print(requirements)
setuptools.setup(
    name="pyARC", # Replace with your own username
    version="0.0.1",
    author="NASA IMPACT",
    author_email="teamimpact@uah.edu",
    description="Validate and Analyze CMR for Quality Metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NASA-IMPACT/pyARC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='validation metadata cmr quality',
    python_requires='>=3.8',
    install_requires=requirements,
    package_data={'pyARC': ['schemas/*'], 'tests': ['fixtures/*']},
    include_package_data=True,
)