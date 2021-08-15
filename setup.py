import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RPI-control-center",
    version="0.0.1",
    author="Mohamed Debbagh",
    author_email="moha7108@protonmail.com",
    description="Python library for interfacing Raspberry pi with connected relays/Actuator in a non-blocking multiprocess threading manor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/moha7108/3-channel-control",
    project_urls={
        "Bug Tracker": "https://gitlab.com/moha7108/3-channel-control/README.md",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPLv3",
        "Operating System :: Raspbian GNU/Linux 10 (buster)",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
          'logzero',
          'RPi.GPIO'
      ],

)
