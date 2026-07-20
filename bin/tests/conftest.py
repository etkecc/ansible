"""Puts bin/ on sys.path so the tests import the package the same way the
scripts do (`from lib import ...`). Without this, pytest's rootdir is the repo
and the import misses; with it, tests and real invocation resolve identically.
"""

import importlib.util
import os
import sys

BIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')


def load_script(filename):
    """Import one of the CLI entrypoints (versions.diff.py and friends) by path.
    Their names carry dots, so a plain `import` can't reach them; this loads the
    module without tripping its `if __name__ == '__main__'` block.
    """
    path = os.path.join(BIN_DIR, filename)
    mod_name = filename.replace('.py', '').replace('.', '_')
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
