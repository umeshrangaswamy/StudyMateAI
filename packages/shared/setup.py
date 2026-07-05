from setuptools import setup, find_packages

setup(
    name="studymateai-shared",
    version="1.0.0",
    packages=find_packages(),
    description="Shared models and database configurations for StudyMateAI.",
    install_requires=[
        "pydantic>=2.0",
        "sqlalchemy>=2.0"
    ],
)
