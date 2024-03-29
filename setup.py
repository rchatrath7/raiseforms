from setuptools import setup

requires = [
    'django',
    'mysqlclient',
    'django-localflavor',
    'hellosign-python-sdk',
    'gunicorn',
    'whitenoise',
    'dj-database-url',
    'requires',
    'django-anymail[mailgun]',
    'celery',
    'redis',
    'django-storages',
    'boto'
    'psycopg2'
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
