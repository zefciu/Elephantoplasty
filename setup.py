# vim set fileencoding = utf-8
from setuptools import setup

setup(
      name = 'Elephantoplasty',
      version = '0.0.1',
      author = u'Szymon Pyżalski',
      author_email = 'zefciu <szymon@pythonista.net>',
      description = 'A PostgreSQL ORM',
      license = 'PSF',
      keywords = 'orm postgresql psql pg persistence sql relational database',
      long_description = """
      An ORM for PostgreSQL database engine. It is aimed to take full advantage
      from PostgreSQL features.""",
      
      install_requires = ['psycopg2>=2.4.1'],
      package_dir = {'': 'src'},
      packages = ['eplasty'],
)