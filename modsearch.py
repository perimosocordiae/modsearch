import os.path
from whoosh.fields import ID, KEYWORD, Schema, TEXT
from whoosh.highlight import UppercaseFormatter
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from scraper import scrape_docstrings


def get_index(dirpath):
  try:
    return open_dir(dirpath)
  except:
    pass
  print 'Creating new index in', dirpath
  if not os.path.exists(dirpath):
    os.mkdir(dirpath)
  schema = Schema(name=ID(stored=True, unique=True),
                  doc=TEXT(stored=True),
                  modulepath=KEYWORD(commas=True))
  return create_in(dirpath, schema)


def index_docstrings(mod, ix):
  writer = ix.writer()
  for mpath, doc in scrape_docstrings(mod):
    writer.update_document(name=unicode(mpath),
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


if __name__ == '__main__':
  import numpy
  ix = get_index('indexdir')
  index_docstrings(numpy, ix)
  search_docstrings(ix, 'least squares')
