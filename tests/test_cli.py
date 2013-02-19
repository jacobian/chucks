import shutil
import tempfile

import pytest
import yaml
import lxml.html

import chucks.cli
from .utils import ls, _make_cli

@pytest.fixture
def cli(tmpdir, request):
    return _make_cli(tmpdir, request)

def test_library(cli):
    cli.create_library()
    assert ls(cli.library.path) == ['courses', 'library.yaml', 'modules', 'theme']

def test_module(cli):
    cli.create_library()
    cli.run_test('module', 'newmod')
    moddir = cli.library.module_path.child('newmod')
    assert moddir.exists()
    assert ls(moddir) == ['exercises', 'module.yaml']
    assert ls(moddir.child('exercises')) == ['newmod.txt']

def test_course(cli):
    cli.create_library()
    cli.run_test('module', 'mod1')
    cli.run_test('module', 'mod2')
    cli.run_test('course', 'newcourse')
    assert ls(cli.library.course_path) == ['newcourse.yaml']
    course = yaml.load(open(cli.library.course_path.child('newcourse.yaml')))
    assert course['modules'] == ['mod1', 'mod2']

class TestBuild(object):
    """
    Tests for the build command (and stuff that runs after, like deploy).

    This is a class because it's slow, so we only want to do it the building
    part once, hence the class fixture below.
    """

    @pytest.fixture(scope='class')
    def cli(self, request):
        tmpdir = tempfile.mkdtemp()
        request.addfinalizer(lambda: shutil.rmtree(tmpdir))
        cli = _make_cli(tmpdir, request)
        cli.setup_test_library()
        cli.run_test('build', 'course1')
        return cli

    def test_build(self, cli):
        assert (ls(cli.library.build_path.child('course1')) ==
                ['Test Course.pdf', '_static', '_templates', 'conf.py', 'html',
                 'index.txt', 'mod1', 'toc.html', 'toc.pdf'])

    def test_html_toc(self, cli):
        index = lxml.html.parse(open(cli.library.build_path.child('course1', 'html', 'index.html')))
        toc_entries = index.xpath("//div[contains(@class,'toctree-wrapper')]//a/text()")
        assert toc_entries == ['1. Module One', '1.1. Exercise 1']

    def test_deploy(self, cli, monkeypatch):

        # Mock out envoy.run, tracking commands for later checking.
        run_commands = []

        def monkeyrun(cmd):
            class rv(object):
                status_code = 0
            run_commands.append(cmd)
            return rv()
        monkeypatch.setattr(chucks.cli.envoy, 'run', monkeyrun)

        cli.run_test('deploy')
        assert run_commands == [
            'git init',
            'git add .',
            'git commit -m "deploy"',
            'git remote add heroku git@heroku.com:myapp.git',
            'git push --force heroku master',
        ]
