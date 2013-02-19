import io
import os
import shutil
from chucks.cli import CLI
from unipath import FSPath as Path

def _make_cli(tmpdir, request):
    """
    Set up a CLI instance pointing to a tmpdir for a library.

    This can't be in the body of cli() itself because we want to call it
    both from the cli fixture and from TestBuild.build.
    """
    cli = TestCLI(
        stdout = io.StringIO(),
        stderr = io.StringIO(),
        libpath = str(tmpdir),
    )

    # Chdir to the temp dir, remembering to restore when we're done.
    oldcwd = Path.cwd()
    os.chdir(str(tmpdir))
    request.addfinalizer(lambda: os.chdir(oldcwd))

    return cli

class TestCLI(CLI):
    def run_test(self, *argv):
        rv = self.run(*argv)
        assert rv == 0, self.err.getvalue()

    def create_library(self):
        self.run_test('library', self.library.path)

    def setup_test_library(self):
        for p in Path(__file__).parent.child('testlib').listdir():
            if p.isdir():
                shutil.copytree(p, self.library.path.child(p.name))
            else:
                shutil.copy(p, self.library.path)

        # Reload the library so we get the new library.yaml
        self.library.load()

def ls(d):
    return sorted(str(p.name) for p in Path(str(d)).listdir())
