# modsearch

Search docstrings of installed Python modules.

Start by indexing all the modules accessible to your Python interpreter:

    python modsearch.py --index-all --verbose

Then, run queries!

    python modsearch.py "http request"
```
Result 1 (17.8017): tornado.httpclient.HTTPRequest
Result 2 (16.7368): DocXMLRPCServer.DocXMLRPCRequestHandler.do_GET
Result 3 (16.7368): DocXMLRPCServer.DocCGIXMLRPCRequestHandler.handle_get
Result 4 (16.7065): tornado.httpserver.HTTPConnection
Result 5 (16.6473): pip.download.HTTPBasicAuth
```

## Usage

```
usage: modsearch.py [-h] [--indexdir INDEXDIR] [--index module [module ...]]
                    [--index-all] [-v]
                    [query]

positional arguments:
  query                 Query string.

optional arguments:
  -h, --help            show this help message and exit
  --indexdir INDEXDIR   Index directory. [indexdir]
  --index module [module ...]
                        Module(s) to index.
  --index-all           Index all accessible modules. (May take a while.)
  -v, --verbose
```
