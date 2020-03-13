from setuptools import setup

setup(
    name='apitess',
    version='0.1a1',
    description='API for Tesserae v5',
    url='https://github.com/tesserae/apitess',
    author='Nozomu Okuda',
    author_email='Nozomu.Okuda@gmail.com',
    packages=['apitess'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Users',
        'Topic :: Digital Humanities :: Classics',
        'Topic :: Digital Humanities :: Text Processing',
        'Topic :: Digital Humanities :: Intertext Matching',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
    ],
    keywords='text_processing intertext_matching',
    install_requires=[
        'flask>=1.0.2',
        'flask-cors',
        'tesserae @ git+https://github.com/tesserae/tesserae-v5@master',
    ],
)
