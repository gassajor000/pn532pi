import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pn532pi",
    version="1.5",
    author="gassajor000",
    author_email="lgassjsg@example.com",
    description="PN532 library for Raspberry Pi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gassajor000/pn532pi",
    packages=setuptools.find_packages(include=['quick2wire', 'quick2wire.*', 'pn532pi', 'pn532pi.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License ",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.4',
    install_requires=['pyserial', 'spidev', 'typing'],
)