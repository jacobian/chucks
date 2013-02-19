#!/usr/bin/env python -u

import datetime
import docopt
import envoy
import io
import jinja2
import json
import os
import pyPdf
import shutil
import sys
import tempfile
import yaml
from unipath import FSPath as Path, DIRS
from . import keyxml
from . import sphinxfile
from . import fileutils
from .models import Course, Library, Module

class CLI(object):
    """
    Usage:
        chucks library <name>
        chucks module <name>
        chucks course <name>
        chucks build [<course>...]
        chucks deploy
        chucks clean
    """

    def __init__(self, stdout=None, stderr=None, libpath=None):
        self.out = stdout or sys.stdout
        self.err = stderr or sys.stderr
        self.library = Library(libpath) if libpath else None
        self.support_path = Path(__file__).parent.child('support')
        self._modules = {}

    def run(self, *argv):
        commands = [line.split()[1] for line in CLI.__doc__.strip().split('\n')[1:]]
        arguments = docopt.docopt(CLI.__doc__, argv=argv, version='Chucks 1.0')
        for command in commands:
            if arguments[command]:
                try:
                    getattr(self, 'do_' + command)(arguments)
                except CLIError as e:
                    self.err.write(e.message)
                    self.rv = 1
                self.rv = 0
        return self.rv

    def do_library(self, arguments):
        """
        Create a new library.
        """
        # FIXME: author, copyright should be flags and/or interactive prompts.
        library = Library(Path(arguments['<name>']).absolute())
        library.create()

    def do_module(self, arguments):
        """
        Create a new module.
        """
        mod = Module(self.library.module_path.child(arguments['<name>']))
        mod.create()

    def do_course(self, arguments):
        """
        Create a new course.
        """
        # FIXME: title, modules from flags/prompt
        course = Course(self.library.course_path.child('%s.yaml' % arguments['<name>']))
        course.create(modules=[str(d.name) for d in self.library.module_path.listdir(filter=DIRS)])

    def do_build(self, arguments):
        # If no course arguments are given, build all the courses.
        if arguments['<course>']:
            try:
                courses = [self.library.courses[c] for c in arguments['<course>']]
            except KeyError:
                raise CLIError("No such course:", c)
        else:
            courses = self.library.courses.values()

        for course in courses:
            self.out.write(u'Building %s\n' % course.title)

            # Make the dest directory.
            dest = self.library.build_path.child(course.slug)
            if dest.exists():
                dest.rmtree()
            dest.mkdir(parents=True)

            # Create the sphinx support directories (_static, _templates) by
            # merging directories from the internal chucks-support directory
            # and from the library's theme if it exists. This has to happen
            # before building the handounts and Sphinx docs because both those
            # steps uses these components.
            for subdir in ('_static', '_templates'):
                chucksdir = self.support_path.child(subdir)
                themedir = self.library.theme_path.child(subdir)
                sources = [d for d in (chucksdir, themedir) if d.exists()]
                if not dest.child(subdir).exists():
                    dest.child(subdir).mkdir()
                fileutils.merge_trees(sources, dest.child(subdir))

            # Write out an auth.json for the deployment step. This should
            # probably actually become part of the deployment step at some point.
            if hasattr(course, 'auth'):
                json.dump(course.auth, open(dest.child('auth.json'), 'w'))

            # Handouts have to go first: Sphinx links to the handouts.
            self._build_handouts(course)
            self._build_sphinx(course)

            # Copy over any extra files to be downloaded. FIXME: This is a nasty
            # hack. Inject these into toc.html as download links?
            for fname in getattr(course, 'downloads', []):
                p = Path(fname)
                if p.isabsolute():
                    src = p
                else:
                    src = self.library.path.child(*p.components())
                shutil.copy(src, dest.child('html'))

    def _build_sphinx(self, course):
        self.out.write(u'  compiling exercises... ')
        dest = self.library.build_path.child(course.slug)

        # conf.py
        confpy = self._get_template('conf.py').render(course=course, library=self.library)
        dest.child('conf.py').write_file(confpy)

        # Index document
        index = sphinxfile.SphinxFile(dest.child('index.txt'))
        index.h1(course.title)
        if hasattr(course, 'subtitle'):
            index.p(course.subtitle)

        index.h2('Handouts')
        index.p(":download:`Download handouts (PDF) <%s.pdf>`" % course.title)

        index.h2('Exercises')

        # Start the toctree; the contents will be written while reading each module.
        index.write('.. toctree::\n   :maxdepth: 2\n   :numbered:\n   :glob:\n\n')

        # For each module collect the exercises.
        for module_name in course.modules:
            module = self.library.modules[module_name]
            exercise_dir = module.path.child('exercises')
            if exercise_dir.exists():
                shutil.copytree(module.path.child('exercises'), dest.child(module_name))
                index.writeline('   %s/index' % module_name)

                # If an index document for the exercise doesn't exist create one
                mod_index_path = dest.child(module_name).child('index.txt')
                if not mod_index_path.exists():
                    mod_index = sphinxfile.SphinxFile(mod_index_path)
                    mod_index.h1(module.title)
                    mod_index.write('.. toctree::\n   :glob:\n\n   *\n\n')
                    mod_index.close()

        index.write('\n')
        index.close()

        self.out.write(u'ok\n')

        # Build us some sphinx.
        self.out.write(u'  building sphinx... ')
        dest.child('html').mkdir()
        r = envoy.run('sphinx-build -b html %s %s/html' % (dest, dest))
        if r.status_code == 0:
            self.out.write(u'ok\n')
            if r.std_err:
                self.out.write(u'  warnings:\n')
                self.out.write(u'\n'.join('    %s' % line for line in r.std_err.split('\n')))
        else:
            self.out.write(u'FAILED:\n')
            self.out.write(r.std_err)

    def _build_handouts(self, course):
        dest = self.library.build_path.child(course.slug)
        modules = [self.library.modules[name] for name in course.modules]

        # Gather the TOC entries by parsing the keynote xml
        self.out.write(u'  gathering toc ... ')
        sections = []
        for module in modules:
            toc = []
            for keydoc in module.path.listdir("*.key"):
                for title, slide_num in keyxml.extract_toc(keydoc):
                    # FIXME: convert slide num to page num - divide by two, but
                    # a bit more than that 'cause of partial pages at the end
                    # of the document. Also see the FIXME below about the
                    # slide numbers.
                    toc.append({'title': title, 'page': slide_num})
            sections.append({'title': module.title, 'toc': toc})
        self.out.write(u'ok\n')

        # Generate a toc.html from the toc.html template, then prince it
        # into a pdf. FIXME: technically I'm violating the prince license
        # here. Will Pisa work? Worth buyting a prince license?
        self.out.write(u'  building toc.pdf ... ')
        toc_html = dest.child('toc.html')
        toc_pdf = dest.child('toc.pdf')
        tmpl = self._get_template('toc.html')
        with io.open(toc_html, 'w', encoding='utf8') as fp:
            fp.write(tmpl.render(
                library = self.library,
                course = course,
                sections = sections,
                today = datetime.date.today(),
            ))

        toc_css = self._get_theme_file('toc.css')
        r = envoy.run('prince %s -s %s -o %s' % (toc_html, toc_css, toc_pdf))
        if r.status_code == 0:
            self.out.write(u'ok\n')
            if r.std_err:
                self.out.write(u'  warnings:\n')
                self.out.write(u'\n'.join('    %s' % line for line in r.std_err.strip().split('\n')))
        else:
            self.out.write(u'FAILED:\n')
            self.out.write(r.std_err)

        # Create a handout pdf
        self.out.write(u'  building handout ... ')
        handouts = pyPdf.PdfFileWriter()

        # FIXME: a great thing to do here would be to add real page numbers
        # (instead of slide numbers) to each section. This is technically
        # possible by creating a "page number" PDF, then "merging" it with the
        # PDFs produced by Keynote. pdfgrid
        # (http://pypi.python.org/pypi/pdfgrid/) does something like this and
        # it looks fairly streightforward. Not sure how fast it'd be, but
        # it'd certainly be pretty awesome for the TOC.

        # Start by adding the doc document.
        pr = pyPdf.PdfFileReader(open(toc_pdf))
        for i in xrange(pr.numPages):
            handouts.addPage(pr.getPage(i))

        # Now add each module's slides. It'd be great if we could automate key
        # -> pdf, but I can't seem to figure out how without requireing UI
        # scripting, which is super brittle. So for now modules need to be
        # exported to PDF by hand :(
        for module in modules:
            for module_pdf in module.path.listdir('*.pdf'):
                pr = pyPdf.PdfFileReader(open(module_pdf))
                for i in xrange(pr.numPages):
                    handouts.addPage(pr.getPage(i))
        handouts.write(open(dest.child('%s.pdf' % course.title), 'w'))

        self.out.write(u'ok\n')

    def _get_template(self, name):
        """
        Load a Jinja template, letting the theme override the default.
        """
        return jinja2.Template(self._get_theme_file(name).read_file())

    def _get_theme_file(self, name):
        """
        Find a file in the theme, falling back to the support dir.
        """
        if self.library.theme_path.child(name).exists():
            return self.library.theme_path.child(name)
        else:
            return self.support_path.child(name)

    def _get_module(self, name):
        if name not in self._modules:
            self._modules[name] = Module(self.library.module_path.child(name))
        return self._modules[name]

    def do_deploy(self, arguments):
        # FIXME: this assumes the app's created and set up and auth works and
        # everything; it would be pretty grand if this command could do that
        # for you. heroku.py would probably help here a lot.
        try:
            app = self.library.app
        except AttributeError:
            raise CLIError("Must define 'app' in library.yaml to deploy.")

        self.out.write(u'Deploying to %s.herokuapp.com...\n' % app)

        # Copy the build dir to a temp location so we can do git-fu without
        # leaving a trail.
        self.out.write(u'  staging files for deploy... ')
        tempdir = Path(tempfile.mkdtemp()).child('chucks')
        shutil.copytree(self.library.build_path, tempdir)

        # Copy over the heroku bits
        for app_bit in self.support_path.child('heroku').listdir():
            shutil.copy(app_bit, tempdir)

        # Now make this thing into a git repo. I don't know how to make
        # this work without changing the cwd...
        os.chdir(tempdir)
        envoy.run('git init')
        envoy.run('git add .')
        envoy.run('git commit -m "deploy"')
        envoy.run('git remote add heroku git@heroku.com:%s.git' % app)
        self.out.write(u' ok\n')

        # Push that bad boy.
        self.out.write(u'  pushing to heroku ... ')
        r = envoy.run(u'git push --force heroku master')
        if r.status_code == 0:
            self.out.write(u' ok\n')
        else:
            self.out.write(u' FAILED:\n')
            self.out.write(r.std_err)

        # Clean up.
        shutil.rmtree(tempdir.parent)

    def do_clean(self, arguments):
        self.library.build_path.rmtree()
        self.library.build_path.mkdir()

class CLIError(EnvironmentError):
    pass

def main():
    sys.exit(CLI().run(*sys.argv[1:]))
