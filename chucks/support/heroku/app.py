import barrel.cooper
import static
import json
from selector import Selector
from unipath import FSPath as Path

app = Selector()
base = Path(__file__).parent
for course in base.listdir(filter=Path.isdir):
    subapp = static.Cling(course.child('html'))
    if course.child('auth.json').exists():
        users = json.load(open(course.child('auth.json')))
        auth = barrel.cooper.basicauth(users=users, realm="Course Material")    # FIXME: worth allowing customization here?
        subapp = auth(subapp)
    app.add("/%s|" % course.name, GET=subapp)
