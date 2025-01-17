from setuptools import setup

long_description = open('README.md', "rt").read()

setup(
    name='l4py',
    version='0.1.7',
    description='l4py is a Python library that simplifies logging configuration with features like JSON formatting, file rotation, and dynamic log levels via environment variables. It integrates seamlessly with Django and leverages the Python standard logging module for easy customization.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/roymanigley/l4py',
    author='Roy Manigley',
    author_email='roy.manigley@gmail.com',
    license='MIT',
    packages=['l4py'],
    install_requires=[],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.11',
    ],
)
