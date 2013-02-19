extensions = ['sphinx.ext.intersphinx', 'sphinx.ext.todo']

templates_path = ['_templates']
source_suffix = '.txt'
master_doc = 'index'

project = "{{ course.title }}"
copyright = "{{ library.copyright }}"
version = release = '1.0'

html_theme = 'default'
html_style = 'rtd.css'
html_title = "{{ course.title }}"
html_static_path = ['_static']
html_show_sourcelink = False
pygments_style = 'sphinx'

{# FIXME: make this customizable in the course/library/module? #}
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'django': ('http://docs.djangoproject.com/en/1.5', 'http://docs.djangoproject.com/en/1.5/_objects'),
    'south':  ('http://south.readthedocs.org/en/latest/', None),
}
