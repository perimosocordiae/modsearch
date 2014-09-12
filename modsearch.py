import os.path
from collections import Hashable
from whoosh.highlight import UppercaseFormatter
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.qparser import QueryParser


def get_index(dirpath):
  try:
    return open_dir(dirpath)
  except:
    pass
  print 'Creating new index in', dirpath
  if not os.path.exists(dirpath):
    os.mkdir(dirpath)
  schema = Schema(name=ID(stored=True), doc=TEXT(stored=True),
                  modulepath=KEYWORD(commas=True))
  return create_in(dirpath, schema)


def index_docstrings(mod, ix):
  writer = ix.writer()
  for mpath, doc in scrape_docstrings(mod):
    writer.add_document(name=unicode(mpath),
                        doc=unicode(doc),
                        modulepath=unicode(mpath.replace('.',',')))
  writer.commit()


def search_docstrings(ix, query_string, verbose=0):
  with ix.searcher() as searcher:
    query = QueryParser('doc', ix.schema).parse(query_string)
    results = searcher.search(query)
    if verbose > 0:
      results.formatter = UppercaseFormatter()
    for r in results:
      print 'Result %d (%g): %s' % (r.rank, r.score, r['name'])
      if verbose == 2:
        print r['doc']
      elif verbose == 1:
        print r.highlights('doc')


def scrape_docstrings(mod, prefix=None, seen=set()):
  if prefix is None:
    prefix = mod.__name__
  if hasattr(mod, '__doc__'):
    d = mod.__doc__
    if d and isinstance(d, basestring):
      yield prefix, d
  if not hasattr(mod, '__dict__'):
    return
  for k,v in vars(mod).iteritems():
    if k.startswith('__') or not isinstance(v, Hashable):
      continue
    try:
      if v in seen:
        continue
    except TypeError:  # Unhashable type
      continue
    seen.add(v)
    for d in scrape_docstrings(v, prefix=prefix+'.'+k, seen=seen):
      yield d

if __name__ == '__main__':
  import numpy
  ix = get_index('indexdir')
  # index_docstrings(numpy, ix)
  search_docstrings(ix, 'least squares')
