from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='flask_jwtlogin',
      version='0.2.1',
      description='flask extension to handle login users in APIs',
      url='https://github.com/AlexPraefectus/flask-jwtlogin',
      author='Alex Korienev',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author_email='alexkorienev@gmail.com',
      license='BSD',
      download_url='https://github.com/AlexPraefectus/flask-jwtlogin/archive/0.1.tar.gz',
      packages=['flask_jwtlogin'],
      zip_safe=False,
      test_require=['requests'],
      install_requires=['flask', 'pyjwt'])
