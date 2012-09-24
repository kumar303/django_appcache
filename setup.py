from setuptools import setup, find_packages


setup(name='django_appcache',
      version='1.3',
      description='Build and serve an appcache manifest from Django.',
      long_description='',
      author='Kumar McMillan',
      author_email='kumar.mcmillan@gmail.com',
      license='BSD',
      url='https://github.com/kumar303/django_appcache',
      include_package_data=True,
      classifiers=[],
      packages=find_packages(exclude=['tests']),
      install_requires=[])
