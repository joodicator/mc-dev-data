from urllib.request import urlopen
import os.path
import pickle
import traceback
import inspect
import sys 
import math

import bs4

from .util import get_url_hash


__all__ = ('get_page', 'from_page', 'get_soup', 'refresh_names', 'get_cacheable',
           'unused_func_cache_files', 'unused_www_cache_files')

refresh_min_proto = -math.inf
refresh_max_proto =  math.inf
refresh_names = set()


def get_cacheable():
    from . import parsers, matrix, pycraft_util
    return {name: f
            for module in (parsers, matrix, pycraft_util)
            for name in module.__all__ for f in (module.__dict__[name],)
            if inspect.isfunction(f) and f.__name__ == 'from_page_func'}


def from_page(*page_args, dep=(), no_cache=False, rdoc=None, doc_order=0, **page_kwds):
    """A decorator for functions whose arguments and return values may be,
       retrieved from and saved in a global cache, in the context of a `page',
       which is a subdivision of the cache, usually specific to a wiki page.

       For each function argument whose value is computed by another @from_page
       function, say `f', `page_args' or `page_kwds' should contain `f' in the
       corresponding position.

       Any other @from_page functions whose outputs are used by the function
       must be explicitly declared as dependencies in the `dep' tuple. (This
       is only necessary when these data are explicitly retrieved from the
       the cache by the function, e.g. using `get_page'.)

       If `no_cache' is given as `True', the output won't be saved to disk
       between runs, but will be cached in memory during each run.

       If `rdoc' is given, it should be a string documenting the corresponding
       RFLAG given in the command-line help.
    """
    def from_page_decorator(func):
        def from_page_func(page, *args, **kwds):
            refresh = False
            if any(dep in refresh_names for dep in from_page_func.depends):
                bound_args = inspect.signature(func).bind(*(page_args+args), **kwds)
                vsn = bound_args.arguments.get('vsn')
                refresh = not vsn or (vsn.protocol >= refresh_min_proto and \
                                      vsn.protocol <= refresh_max_proto)

            if func.__name__ not in page or refresh \
            and func.__name__ not in page.get('__refreshed__', set()):
                args = tuple(a(page) for a in page_args) + args
                kwds.update({k:k(page) for k in page_kwds})
                result = func(*args, **kwds)
                if inspect.isgenerator(result):
                    result = list(result)
                page[func.__name__] = result
                if no_cache:
                    if '__no_cache__' not in page: page['__no_cache__'] = set()
                    page['__no_cache__'].add(func.__name__)
                if refresh:
                    if '__refreshed__' not in page: page['__refreshed__'] = set()
                    page['__refreshed__'].add(func.__name__)

            return page[func.__name__]

        from_page_func.depends = {func.__name__}
        for arg_func in page_args + tuple(page_kwds.keys()) + dep:
            if arg_func.__name__ == 'from_page_func':
                from_page_func.depends |= arg_func.depends

        from_page_func.__doc__ = func.__doc__
        from_page_func.rdoc = rdoc
        from_page_func.doc_order = doc_order
        from_page_func.refreshable = not no_cache
        return from_page_func

    return from_page_decorator


func_cache_dir = os.path.join(os.path.dirname(__file__), '..', 'func-cache')
unused_func_cache_files = set(os.listdir(func_cache_dir)) - {'.gitignore'}
warned_unknown_func_cache_keys = set()
class get_page(object):
    """A context manager for code operating on data stored in the func-cache.
       The func-cache is a mapping from arbitrary string keys (given by `url')
       to dicts mapping further keys to cached data items.

       The `url's are usually the URLs of wiki pages, but may also be the
       string '__global__' for data which are not particular to a wiki page.
       The dict keys are usually the names of the @from_page functions that
       their corresponding values are calculated with, or may also be special
       double-underscored names giving metadata used by the cache system.

       On entry, this context manager produces the dict corresponding to the
       given key, which is referred to as the `page'. This value may be given
       as the first argument to functions decorated with @from_page, which will
       then operate in the context of the selected `url'.

       On exit, this context manager saves the selected cache section again to
       disk.
    """
    __slots__ = 'page', 'func_cache_file'
    def __init__(self, url):
        url_hash = get_url_hash(url)
        self.func_cache_file = os.path.join(func_cache_dir, url_hash)
        if os.path.exists(self.func_cache_file):
            unused_func_cache_files.discard(url_hash)
            with open(self.func_cache_file, 'rb') as file:
                self.page = pickle.load(file)
            assert isinstance(self.page, dict), repr(self.page)
            assert self.page['url'] == url, repr(self.page)
            cacheable = get_cacheable() 
            for key in list(self.page.keys()):
                if key != 'url' and not inspect.isfunction(cacheable.get(key)):
                    if key not in warned_unknown_func_cache_keys:
                        print('Warning: discarding unknown func-cache key: %r.'
                              % key, file=sys.stderr)
                        warned_unknown_func_cache_keys.add(key)
                    del self.page[key]
        else:
            self.page = {'url': url}

    def __enter__(self):
        if self.page is None:
            raise ValueError('get_page.__enter__ called after __exit__.')
        return self.page

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if (exc_type, exc_val, exc_tb) == (None, None, None):
                if '__no_cache__' in self.page:
                    no_cache = self.page.pop('__no_cache__')
                    for key in no_cache: del self.page[key]
                if '__refreshed__' in self.page:
                    del self.page['__refreshed__']
                with open(self.func_cache_file, 'wb') as file:
                    pickle.dump(self.page, file)
        except IOError:
            traceback.print_exc()
        finally:
            self.page = None
        return False


www_cache_dir = os.path.join(os.path.dirname(__file__), '..', 'www-cache')
unused_www_cache_files = set(os.listdir(www_cache_dir))
@from_page(lambda page: page['url'], no_cache=True)
def get_soup(url):
    """Return a BeautifulSoup instance giving the parsed HTML structure
       of the selected page. If the page does not exist in www-cache,
       it is downloaded first and saved there. It is intended that the
       www-cache is permanent and kept under version control, to reduce
       load on the wiki's web server."""
    url_hash = get_url_hash(url)
    www_cache_file = os.path.join(www_cache_dir, url_hash)
    if os.path.exists(www_cache_file):
        with open(www_cache_file) as file:
            charset = 'utf8'
            data = file.read().encode(charset)
    else:
        print('Downloading %s...' % url, file=sys.stderr)
        with urlopen(url) as stream:
            charset = stream.info().get_param('charset')
            data = stream.read()
        with open(www_cache_file, 'w') as file:
            file.write(data.decode(charset))
    return bs4.BeautifulSoup(data, 'lxml', from_encoding=charset)
