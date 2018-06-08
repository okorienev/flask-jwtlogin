from setuptools import setup

setup(name='flask_jwtlogin',
      version='0.1',
      description='flask extension to handle login users in APIs',
      url='https://github.com/AlexPraefectus/flask-jwtlogin',
      author='Alex Korienev',
      author_email='alexkorienev@gmail.com',
      license='BSD',
      packages=['flask_jwtlogin'],
      zip_safe=False,
      install_requires=['flask'])
