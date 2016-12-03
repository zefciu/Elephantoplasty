# vim set fileencoding=utf-8
from setuptools import setup, find_packages


with open('README.txt') as f:
    long_description = f.read()


setup(
      name = 'Elephantoplasty',
      version = '0.2',
      author = 'Szymon Pyżalski',
      author_email = 'zefciu <szymon@pythonista.net>',
      description = 'A PostgreSQL asyncio ORM',
      license = 'BSD',
      url = 'http://github.com/zefciu/Elephantoplasty',
      keywords = 'asyncio orm postgresql psql pg persistence sql relational database',
      long_description = long_description,
      
      install_requires = ['aiopg>=0.12.0'],
      # tests_require = ['nose>=1.0', 'nose-cov>=1.0'],
      # test_suite = 'nose.collector',
      package_dir = {'': 'src'},
      packages = find_packages('src'),
      classifiers = [
          'Development Status :: 3 - Planning',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: SQL',
          'Topic :: Database :: Front-Ends',
      ]
    
)
