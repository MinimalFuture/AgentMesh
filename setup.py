from setuptools import setup, find_namespace_packages
import os

# 读取 README 文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentmesh-sdk",
    version="0.0.1.dev2",
    author="Minimal Future",
    author_email="zyj@zhayujie.com",
    description="An open-source multi-agent framework for building agent teams with LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MinimalFuture/AgentMesh",
    packages=find_namespace_packages(include=["agentmesh*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "urllib3",
        "requests",
        "pyyaml",
        "pydantic"
    ],
    extras_require={
        "full": ["browser-use>=0.1.40"],
    },
    include_package_data=True,
)
