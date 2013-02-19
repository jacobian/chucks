class SphinxFile(object):
    """
    Really simple Sphinx source code writer thingie.
    """
    headers = '==-~'

    def __init__(self, path):
        self.fp = open(path, 'w')

    def __del__(self):
        self.close()

    def __getattr__(self, attr):
        return getattr(self.fp, attr)

    def writeline(self, line=''):
        self.write(line)
        self.write('\n')

    def h1(self, title):
        self._header(title, self.headers[0], top=True)

    def h2(self, title):
        self._header(title, self.headers[1])

    def h3(self, title):
        self._header(title, self.headers[2])

    def h4(self, title):
        self._header(title, self.headers[3])

    def p(self, text):
        self.writeline(text)
        self.writeline()

    def _header(self, title, char, top=False):
        line = char * len(title)
        if top:
            self.writeline(line)
        self.writeline(title)
        self.writeline(line)
        self.writeline()
