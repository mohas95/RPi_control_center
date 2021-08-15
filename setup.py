import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RPI-control-center",
    version="0.0.2",
    author="Mohamed Debbagh",
    author_email="moha7108@protonmail.com",
    description="Python library for interfacing Raspberry pi with connected relays/Actuator in a non-blocking multiprocess threading manor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/moha7108/rpi-control-center",
    project_urls={
        "Bug Tracker": "https://gitlab.com/moha7108/rpi-control-center/README.md",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Other OS",
        "Development Status :: 2 - Pre-Alpha",
    ],
    license='GNU GPLv3',
    packages=['rpi_control_center'],
    python_requires=">=3.6",
    install_requires=[
          'logzero',
          'RPi.GPIO'
      ],

)
