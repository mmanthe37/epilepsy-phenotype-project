from setuptools import setup, find_packages

setup(
    name="epilepsy-phenotype-lpa",
    version="1.0.0",
    description="Longitudinal Phenotyping Algorithm (LPA) for Epilepsy — VLEP Framework",
    author="Michael Manthe",
    license="MIT",
    packages=find_packages(exclude=["tests*", "notebooks*"]),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "lpa-demo=algorithm.core.lpa_engine:main",
        ],
    },
)
