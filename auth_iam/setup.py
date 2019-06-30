from setuptools import setup


setup(
    name='dashboard',
    version='0.2.0',
    install_requires=['dash', 'gunicorn', 'pyjwt'],
    packages=['dashboard', 'dashboard.auth', 'dashboard.callbacks',
              'dashboard.layout'],
    package_data={'dashboard': ['auth/templates/login.html']},
    entry_points={
        'console_scripts': [
            'dashboard_server = dashboard.app:main',
        ]},
)
