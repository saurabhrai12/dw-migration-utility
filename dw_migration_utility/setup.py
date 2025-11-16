"""
Setup script for Data Warehouse Migration Utility.
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="dw_migration_utility",
    version="1.0.0",
    description="Data Warehouse Migration Utility from Oracle/Informatica to Snowflake",
    author="Migration Team",
    author_email="migration@company.com",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dw-migrate=main:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
