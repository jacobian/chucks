import zipfile
import lxml.etree

#
# Helpers for keyxml parsing
# TODO: move this into a class - module, course classes, etc.
# These hardcoded bits need to move into course.yaml or something.
#
TOC_MASTERS = ['Title & Subtitle', 'Title & Bullets', 'Title - Top',
               'Title - Center', 'Code + Title', 'Fancy bullets']
SKIP_TITLES = ['Documentation', 'Exercise', 'Bonus:']

def extract_toc(filename):
    """
    Extract the toc entries from a keynote doc.

    Yields (title, slide_num) pairs.
    """
    doc = lxml.etree.parse(zipfile.ZipFile(filename).open('index.apxl'))
    presentation = doc.getroot()
    important_masters = find_important_masters(presentation)
    slides = xp(presentation, "//key:slide[not(@key:hidden = 'true')]")
    for i, slide in enumerate(slides):
        master = xp(slide, 'key:master-ref/@sfa:IDREF')
        if master in important_masters:
            title = ''.join(xp(slide, 'key:title-placeholder//sf:p//text()')).strip()
            if not any(t in title for t in SKIP_TITLES):
                yield (title, i+1)

def find_important_masters(presentation):
    master_ids = []
    for master in xp(presentation, '//key:master-slide'):
        if xp(master, '@key:name')[0] in TOC_MASTERS:
            master_ids.append(xp(master, '@sfa:ID'))
    return master_ids

def xp(elem, path):
    return elem.xpath(path, namespaces=elem.nsmap)
