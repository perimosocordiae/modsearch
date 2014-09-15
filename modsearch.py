import importlib
from argparse import ArgumentParser

from indexer import get_index, index_docstrings, search_docstrings
from scraper import crawl_pythonpath


def main():
  ap = ArgumentParser()
  ap.add_argument('query', nargs='?', help='Query string.')
  ap.add_argument('--indexdir', default='indexdir',
                  help='Index directory. [%(default)s]')
  ap.add_argument('--index', metavar='module', nargs='+',
                  help='Module(s) to index.')
  ap.add_argument('--index-all', action='store_true',
                  help='Index all accessible modules. (May take a while.)')
  ap.add_argument('-v', '--verbose', action='store_true')
  args = ap.parse_args()
  if args.index_all:
    mods = crawl_pythonpath(verbose=args.verbose)
  elif args.index:
    mods = map(importlib.import_module, args.index)
  else:
    mods = []

  ix = get_index(args.indexdir)

  if mods:
    index_docstrings(ix, *mods, verbose=args.verbose)

  if args.query:
    search_docstrings(ix, args.query, verbose=int(args.verbose))


if __name__ == '__main__':
  main()
