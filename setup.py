from setuptools import setup, find_packages


setup(
    name='HCycle',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'pydantic',
        'requests',
        'attrs',
        'toml',
        'requests',
        'attr',
        'toml',
        'AWSIoTPythonSDK',
        'PyYAML'

    ],
    entry_points={
        'console_scripts': [
            'hcycle = hcycle:cli',
            'hcy = hcycle:cli'
        ],
    },
)
