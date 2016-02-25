from setuptools import setup
import os


version_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'VERSION'))
with open(version_file) as v:
    VERSION = v.read().strip()


SETUP = {
    'name': "charms.templating.jinja2",
    'version': VERSION,
    'author': "Cory Johns",
    'author_email': "johnsca@gmail.com",
    'url': "https://github.com/juju-solutions/charms.templating.jinja2",
    'packages': [
        "charms",
        "charms.templating",
    ],
    'install_requires': [
        'jinja2>=2.7.2,<3.0.0',
        'charmhelpers>=0.6.0,<1.0.0',
    ],
    'license': "Apache License 2.0",
    'long_description': open('README.rst').read(),
    'description': 'Framework for writing reactive-style Juju Charms',
}

try:
    from sphinx_pypi_upload import UploadDoc
    SETUP['cmdclass'] = {'upload_sphinx': UploadDoc}
except ImportError:
    pass

if __name__ == '__main__':
    setup(**SETUP)
