from setuptools import setup, find_packages

setup(
    name="askwiseai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.103.1",
        "uvicorn>=0.23.2",
        "httpx>=0.24.1",
        "pydantic>=2.3.0",
        "pydantic-settings>=2.0.3",
        "python-dotenv>=1.0.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-Powered Q&A System with Tool Integration",
    keywords="ai, llm, chatbot, tools, api",
    url="https://github.com/yourusername/askwiseai",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 