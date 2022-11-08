import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RPI-control-center",
    keywords = 'Raspberry Pi, Raspi, Python, GPIO, USB, Mass storage, API, non-blocking',
    version="0.2.0",
    author="Mohamed Debbagh",
    author_email="moha7108@protonmail.com",
    description="""This package provides additional suite of python based rpi abstraction for handling rpi hardware control.
                    The package currently includes an abstraction layer and API engine for the RPi.GPIO package for python, which allows for multi-process and non-blocking control of GPIO pins.
                    The package also include a module for handling usb mass storage device mounting, data dumping, and unmounting. Finally the Package also includes a module for common sensors.
                    """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moha7108/RPi_control_center",
    project_urls={
        "Bug Tracker": "https://github.com/moha7108/RPi_control_center/issues",
        "Github": "https://github.com/moha7108/RPi_control_center"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
    ],
    license='GNU GPLv3',
    packages=['rpi_control_center','rpi_sensor_monitors','rpi_sensor_monitors.gravity'],
    python_requires=">=3.6",
    install_requires=[
          'logzero',
          'RPi.GPIO',
          'smbus',
          'spidev'
      ]
)
