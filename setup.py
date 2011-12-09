# vim set fileencoding=utf-8
from setuptools import setup

with open('README.txt') as f:
    long_description = f.read()

setup(
      name = 'Elephantoplasty',
      version = '0.0.2',
      author = 'Szymon Pyżalski',
      author_email = 'zefciu <szymon@pythonista.net>',
      description = 'A PostgreSQL ORM',
      license = 'BSD',
      url = 'http://github.com/zefciu/Elephantoplasty',
      keywords = 'orm postgresql psql pg persistence sql relational database',
      long_description = long_description,
      
      install_requires = ['psycopg2>=2.4.1'],
      tests_require = ['nose>=1.0', 'nose-cov>=1.0'],
      test_suite = 'nose.collector',
      package_dir = {'': 'src'},
      packages = [
          'eplasty', 'eplasty.field', 'eplasty.object', 'eplasty.relation',
          'eplasty.relation.listlike'
      ],
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: SQL',
          'Topic :: Database :: Front-Ends',
      ]
    
)
