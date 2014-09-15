import importlib
import os.path
import pkgutil
import sys
import time
import types
import warnings
from collections import deque, Hashable

__all__ = ['crawl_pythonpath', 'scrape_docstrings']


def crawl_pythonpath(verbose=False):
  """Returns a list of all accessible modules, as module objects.
  Includes builtin modules, stdlib modules, and anything else on sys.path."""
  mod_names = set(sys.builtin_module_names)
  blacklist = set(['this','antigravity'])  # Don't import joke modules.
  error_cb = lambda name: blacklist.add(name)

  tic = time.time()
  with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    for mod_finder, name, ispkg in pkgutil.walk_packages(onerror=error_cb):
      if not ispkg and '.' in name:
        continue
      mod_names.add(name)
  mod_names -= blacklist
  if verbose:
    print 'Found %d modules in %g secs.' % (len(mod_names), time.time() - tic)

  tic = time.time()
  mods = []
  for m in sorted(mod_names):
    try:
      mods.append(importlib.import_module(m))
    except ImportError:
      pass
  if verbose:
    print 'Imported %d modules in %g secs.' % (len(mods), time.time() - tic)
  return mods


def scrape_docstrings(*root_modules):
  """Given a python module, produces a sequence of (name, docstring) pairs.
  Submodules are visited in breadth-first order,
  which produces names with the least nesting.
  Note: submodules not imported by the root will not be visited!
  """
  docs = {}
  seen = set()
  for root in root_modules:
    if hasattr(root, '__file__'):
      root_dir = os.path.dirname(root.__file__)
    else:
      root_dir = ''
    queue = deque([(root, root.__name__)])
    while queue:
      mod, name = queue.popleft()
      # have we seen it before?
      try:
        if mod in seen:
          continue
      except:
        continue  # Unhashable type. Don't bother with it.
      # We haven't seen it before.
      seen.add(mod)
      # Does it have a docstring?
      if hasattr(mod, '__doc__'):
        d = mod.__doc__
        if d and isinstance(d, basestring):
          docs[name] = d
      # Does it have sub-fields?
      if (not hasattr(mod, '__dict__') or
          not isinstance(mod.__dict__, types.DictType)):
        continue
      # iterate over sub-fields
      for k,v in mod.__dict__.iteritems():
        if k.startswith('__') or not dir(v) or not isinstance(v, Hashable):
          continue
        if isinstance(v, types.ModuleType):
          # Make sure it's a submodule of the root module.
          if not hasattr(v, '__file__') or not v.__file__.startswith(root_dir):
            continue
        field_name = name + '.' + k
        queue.append((v, field_name))
  return docs.iteritems()


if __name__ == '__main__':
  from argparse import ArgumentParser
  ap = ArgumentParser()
  ap.add_argument('module', nargs='*', help='Module(s) to scrape.')
  args = ap.parse_args()
  if args.module:
    mods = map(importlib.import_module, args.module)
  else:
    mods = crawl_pythonpath(verbose=True)
  for k, v in sorted(scrape_docstrings(*mods)):
    print k, len(v)
