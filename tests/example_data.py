import os
import pkg_resources

try:
    from pathlib2 import Path
except ImportError:
    from pathlib import Path

class ExampleData(object):
    def __init__(self, *path_components):
        self.path_components = path_components

    @property
    def path(self):
        return pkg_resources.resource_filename(__name__, os.path.join('data', *self.path_components))

    @property
    def text_content(self, encoding=None):
        return Path(self.path).read_text(encoding=encoding)
