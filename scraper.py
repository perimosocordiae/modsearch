import importlib
import types
import os.path
from collections import Hashable, deque


# TODO: crawl the PYTHONPATH


def scrape_docstrings(*root_modules):
  """Given a python module, produces a sequence of (name, docstring) pairs.
  Submodules are visited in breadth-first order,
  which produces names with the least nesting.
  Note: submodules not imported by the root will not be visited!
  """
  docs = {}
  seen = set()
  queue = deque([(m, m.__name__) for m in root_modules])
  root_dirs = set(os.path.dirname(m.__file__) for m in root_modules)
  while queue:
    mod, name = queue.popleft()
    # have we seen it before?
    try:
      if mod in seen:
        continue
    except TypeError:
      continue  # Unhashable type. Don't bother with it.
    # We haven't seen it before.
    seen.add(mod)
    # Does it have a docstring?
    if hasattr(mod, '__doc__'):
      d = mod.__doc__
      if d and isinstance(d, basestring):
        docs[name] = d
    # Does it have sub-fields?
    if not hasattr(mod, '__dict__'):
      continue
    # iterate over sub-fields
    for k,v in mod.__dict__.iteritems():
      if k.startswith('__') or not isinstance(v, Hashable):
        continue
      if isinstance(v, types.ModuleType):
        # Make sure it's a submodule of one of the roots.
        if (not hasattr(v, '__file__') or
            not any(v.__file__.startswith(md) for md in root_dirs)):
          continue
      field_name = name + '.' + k
      queue.append((v, field_name))
  return docs.iteritems()


if __name__ == '__main__':
  from argparse import ArgumentParser
  ap = ArgumentParser()
  ap.add_argument('module', nargs='+', help='Module(s) to scrape.')
  args = ap.parse_args()
  mods = map(importlib.import_module, args.module)
  for k, v in sorted(scrape_docstrings(*mods)):
    print k, len(v)
