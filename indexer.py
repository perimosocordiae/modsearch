import os.path
import sys
from whoosh.fields import ID, KEYWORD, Schema, TEXT
from whoosh.highlight import UppercaseFormatter
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from scraper import scrape_docstrings

__all__ = ['get_index', 'index_docstrings', 'search_docstrings']


def get_index(dirpath, verbose=False):
  try:
    return open_dir(dirpath)
  except:
    pass
  if verbose:
    print 'Creating new index in', dirpath
  if not os.path.exists(dirpath):
    os.mkdir(dirpath)
  schema = Schema(name=ID(stored=True, unique=True),
                  doc=TEXT(stored=True),
                  modulepath=KEYWORD(commas=True))
  return create_in(dirpath, schema)


def index_docstrings(ix, *modules, **kwargs):
  writer = ix.writer()
  verbose = kwargs.get('verbose', False)
  for i, mod in enumerate(modules, start=1):
    if verbose:
      sys.stdout.write('\rIndexing %d of %d...' % (i, len(modules)))
      sys.stdout.flush()
    for mpath, doc in scrape_docstrings(mod):
      writer.update_document(name=unicode(mpath),
                             doc=unicode(doc),
                             modulepath=unicode(mpath.replace('.',',')))
  if verbose:
    print '\rFinished %d of %d. Committing...' % (i, len(modules))
  writer.commit()
  if verbose:
    print 'Done'


def search_docstrings(ix, query_string, verbose=0):
  with ix.searcher() as searcher:
    query = QueryParser('doc', ix.schema).parse(query_string)
    results = searcher.search(query)
    if verbose > 0:
      results.formatter = UppercaseFormatter()
    for r in results:
      print 'Result %d (%g): %s' % (r.rank+1, r.score, r['name'])
      if verbose == 2:
        print r['doc'], '\n'
      elif verbose == 1:
        print r.highlights('doc'), '\n'


if __name__ == '__main__':
  import numpy
  ix = get_index('indexdir')
  index_docstrings(ix, numpy, verbose=False)
  search_docstrings(ix, 'least squares')
