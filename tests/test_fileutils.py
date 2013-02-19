from unipath import FSPath as Path
from chucks import fileutils
from .utils import ls

def test_merge_trees(tmpdir):
    # Set up and merge two directory trees:
    #   src1/
    #       file1.txt
    #       dir1/
    #           file2.txt
    #           file3.txt
    #   src2/
    #       file1.txt
    #       dir1/
    #           file3.txt
    #           file4.txt
    #           dir2/
    #               file5.txt
    #
    # Expected output should be:
    #
    #   src1/
    #       file1.txt           <-- from src2
    #       dir1/
    #           file2.txt       <-- from src1
    #           file3.txt       <-- from src2
    #           file4.txt       <-- from src2
    #           dir2/
    #               file5.txt   <-- from src2

    src1 = Path(str(tmpdir)).child('src1')
    src1.mkdir()
    src1.child('file1.txt').write_file('src1: file1')
    src1.child('dir1').mkdir()
    src1.child('dir1', 'file2.txt').write_file('src1: file2')
    src1.child('dir1', 'file3.txt').write_file('src1: file3')

    src2 = Path(str(tmpdir)).child('src2')
    src2.mkdir()
    src2.child('file1.txt').write_file('src2: file1')
    src2.child('dir1').mkdir()
    src2.child('dir1', 'file3.txt').write_file('src2: file3')
    src2.child('dir1', 'file4.txt').write_file('src2: file4')
    src2.child('dir1', 'dir2').mkdir()
    src2.child('dir1', 'dir2', 'file5.txt').write_file('src2: file5')

    dest = Path(str(tmpdir)).child('dest')
    dest.mkdir()

    fileutils.merge_trees([src1, src2], dest)
    assert ls(dest) == ['dir1', 'file1.txt']
    assert dest.child('file1.txt').read_file() == 'src2: file1'
    assert ls(dest.child('dir1')) == ['dir2', 'file2.txt', 'file3.txt', 'file4.txt']
    assert dest.child('dir1', 'file2.txt').read_file() == 'src1: file2'
    assert dest.child('dir1', 'file3.txt').read_file() == 'src2: file3'
    assert ls(dest.child('dir1', 'dir2')) == ['file5.txt']
