from setuptools import setup, find_packages

setup(
    name='fawkes',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'tensorflow>=2.0.0', # Updated to allow newer versions if needed
        'numpy',
        'Pillow',
        'mtcnn',
        'bleach',
        'matplotlib'
    ],
)
