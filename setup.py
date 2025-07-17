#!/usr/bin/env python3
"""
Setup script for AITop - Agentic System Monitor
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'src', 'aitop', '__init__.py')
    with open(init_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

# Read requirements from requirements.txt
def get_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read long description from README.md
def get_long_description():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "An AI agent designed to collect system information and provide intelligent system status reports"

setup(
    name='aitop',
    version=get_version(),
    description='An AI agent designed to collect system information and provide intelligent system status reports',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='AITop Team',
    author_email='team@aitop.dev',
    url='https://github.com/hualet/aitop',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.9',
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'pre-commit>=3.0.0',
        ],
        'ai': [
            'scikit-learn>=1.3.0',
            'tensorflow>=2.13.0',
            'transformers>=4.30.0',
            'torch>=2.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'aitop=aitop.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
    ],
    keywords='system monitoring ai performance analysis',
    project_urls={
        'Homepage': 'https://github.com/hualet/aitop',
        'Repository': 'https://github.com/hualet/aitop',
        'Issues': 'https://github.com/hualet/aitop/issues',
        'Documentation': 'https://aitop.readthedocs.io',
    },
)
