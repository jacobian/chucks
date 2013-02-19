"""
"Model" classes, representing the various objects manipulated here.
"""

import datetime
import yaml
from unipath import FSPath as Path, DIRS
from . import fileutils

class ConfigDirectory(object):
    """
    This terribly-named class is the parent class for the both Library and
    Module, encapsulating the directory-with-yaml-file-config pattern.
    """
    def __init__(self, path, config_file):
        self.__dict__['path'] = Path(path)
        self.__dict__['config_file'] = self.path.child(config_file)
        self.load()

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.path.name)

    def __getattr__(self, attr):
        try:
            return self.data[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self.data[attr] = value

    def load(self):
        if self.config_file.exists():
            self.__dict__['data'] = yaml.safe_load(open(self.config_file))
        else:
            self.__dict__['data'] = {'title': unicode(self.path.name).replace('_', ' ').title()}

    def save(self):
        yaml.safe_dump(self.data, open(self.config_file, 'w'), default_flow_style=False)

def path_property(config_name, default):
    """
    A property on Library refering to a subdir containing modules, builds, etc.

    See Library below for usage.
    """
    def _fget(self):
        d = Path(getattr(self, config_name, default))
        return self.path.child(*d.components())
    return property(_fget)

class Library(ConfigDirectory):
    """
    A "library" is the main container for a set of modules and courses.
    """
    def __init__(self, path):
        super(Library, self).__init__(path, 'library.yaml')

    def create(self, author=None, copyright=None):
        """
        Create this library. Fails if the library already exists.
        """
        fileutils.create_dir(self.path)
        self.path.child('courses').mkdir()
        self.path.child('modules').mkdir()
        self.path.child('theme').mkdir()
        self.author = author or "Your Name, Esq."
        self.copyright = copyright or "Your Company, LLC"
        self.save()

    module_path = path_property('module_dir', 'modules')
    build_path = path_property('build_dir', 'build')
    course_path = path_property('course_dir', 'courses')
    theme_path = path_property('theme_dir', 'theme')

    @property
    def courses(self):
        return dict(
            (str(f.stem), Course(f))
            for f in self.course_path.listdir('*.yaml')
        )

    @property
    def modules(self):
        return dict(
            (str(d.stem), Module(d))
            for d in self.module_path.listdir(filter=DIRS)
        )

class Module(ConfigDirectory):
    """
    A module is a single "chunk" of course content.
    """

    def __init__(self, path):
        super(Module, self).__init__(path, 'module.yaml')

    def create(self):
        """
        Create this module. Fails if the module already exists.
        """
        fileutils.create_dir(self.path)
        self.path.child('exercises').mkdir()
        self.path.child('exercises', self.path.name + '.txt').write_file('')
        self.save()

class Course(ConfigDirectory):
    """
    A course is a single class, comprised of a list of modules.

    It doesn't have a directory like modules; it's just a simple yaml file.
    XXX maybe it should?
    """
    def __init__(self, path):
        self.__dict__['path'] = path
        self.__dict__['config_file'] = path
        self.load()

    def create(self, title=None, modules=None):
        if self.path.exists():
            raise EnvironmentError("Course at %s already exists." % self.path)
        self.title = title or "My Awesome Class - %s" % datetime.date.today().strftime('%D')
        self.modules = modules or []
        self.save()

    @property
    def slug(self):
        return self.data.get('slug', str(self.path.stem))

    @slug.setter
    def slug(self, value):
        self.data['slug'] = value
