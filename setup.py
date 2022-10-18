from setuptools import setup

setup(
    name='Halio Cycle Tester CLI Tool',
    version='0.0.1',
    py_modules=['hcycle'],
    install_requires=[
        'Click',
        'pydantic',
        'requests',
        'attrs',
        'toml'
    ],
    entry_points={
        'console_scripts': [
            'hcycle = hcycle:cli',
        ],
    },
)
