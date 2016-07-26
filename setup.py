from setuptools import setup

requires = [
    'django',
    'mysqlclient',
]

setup(
    name='raiseforms',
    version='0.0',
    packages=['forms', 'forms.migrations', 'raiseforms'],
    install_requires=requires,
    url='',
    license='',
    author='Raise',
    author_email='raisedev1@gmail.com',
    description='Automator for Raise onboarding process.'
)
