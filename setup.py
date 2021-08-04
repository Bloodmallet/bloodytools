from setuptools import setup

setup(
    name="bloodytools",
    version="9.1.0.1",
    author="Bloodmallet(EU)",
    author_email="bloodmalleteu@gmail.com",
    description="Allows multiple ways of automated data generation via SimulationCraft for World of Warcraft.",
    install_requires=[
        "requests",
    ],
    license="GNU GENERAL PUBLIC LICENSE",
    packages=[
        "bloodytools",
    ],
    package_data={
        "": [
            "*.md",
            "fallback_profiles/*/*/*.simc",
        ],
    },
    python_requires=">3.7",
    url="https://github.com/Bloodmallet/bloodytools",
)
