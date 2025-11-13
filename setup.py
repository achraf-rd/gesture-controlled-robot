from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gesture-controlled-robot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive hand gesture recognition system for robotic control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gesture-controlled-robot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "flake8>=3.8.0",
            "black>=21.0.0",
            "isort>=5.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gesture-control=gesture_control_simple:main",
            "gesture-control-gui=gesture_control_gui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
    keywords="gesture control, computer vision, robotics, mediapipe, opencv, esp32",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/gesture-controlled-robot/issues",
        "Source": "https://github.com/yourusername/gesture-controlled-robot",
        "Documentation": "https://github.com/yourusername/gesture-controlled-robot/wiki",
    },
)