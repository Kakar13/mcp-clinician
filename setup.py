from setuptools import setup, find_packages

setup(
    name="clinical-decision-support",
    version="0.1.0",
    packages=find_packages(),
    py_modules=['clinical_launcher'],
    install_requires=[
        "mcp>=0.1.0",
        "httpx>=0.24.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "aiohttp>=3.8.0",
        "tenacity>=8.0.0",
        "pydantic>=1.8.0",
        "python-dateutil>=2.8.2",
        "anthropic>=0.7.0",
    ],
    entry_points={
        'console_scripts': [
            'clinical-assistant=clinical_launcher:cli_main',
        ],
    },
) 