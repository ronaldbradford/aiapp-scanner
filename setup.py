from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aiapp-scanner",
    version="0.2.0",
    author="Ronald Braford",
    author_email="me@ronaldbradford.com",
    description="Scan macOS for installed AI applications and CLI tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ronaldbradford/aiapp-scanner",
    py_modules=["aiapp_scanner", "compliance_report"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "aiapp-scanner=aiapp_scanner:main",
            "aiapp-compliance-report=compliance_report:main",
        ],
    },
    data_files=[
        ('share/aiapp-scanner', ['scanner_config.json']),
    ],
)
