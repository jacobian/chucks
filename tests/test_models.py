import yaml
from unipath import FSPath as Path
from chucks.models import Module
from .utils import ls

def test_module_create(tmpdir):
    p = Path(str(tmpdir))
    m = Module(p)
    m.create()
    assert ls(p) == ['exercises', 'module.yaml']
    assert yaml.safe_load(open(p.child('module.yaml'))) == {'title': p.name.replace('_', ' ').title()}
