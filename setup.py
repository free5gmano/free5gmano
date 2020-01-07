from setuptools import setup

setup(
    name='nm',
    version='0.1',
    py_modules=['nm'],
    install_requires=[
        'Click',
        'requests',
        'beautifulsoup4',
    ],
    entry_points='''
        [console_scripts]
        nm=cli:cli
    ''',
)