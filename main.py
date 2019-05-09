#!/usr/bin/env python3

import inspect
import sys

from mcdevdata.sources import version_urls
from mcdevdata.util import get_url_hash
from mcdevdata.cache import unused_www_cache_files, unused_func_cache_files
from mcdevdata.cache import refresh_names, get_cacheable
from mcdevdata.html_out import matrix_html
import mcdevdata.cache

refresh_min_proto_arg = '--r-min-proto='
refresh_max_proto_arg = '--r-max-proto='

if __name__ == '__main__':
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        print('Usage: main.py [-h|--help] [-p|--pycraft-only] [VERSIONS...] [RFLAGS...]\n'
              '\n'
              'This script generates and prints to stdout the contents of index.htm.\n'
              'If the -p flag is given, the displayed rows will be restricted to those\n'
              'packets present in the local installation of pyCraft.\n'
              '\n'
              'VERSIONS: to restrict the displayed Minecraft versions to a subset of those,\n'
              'available, version names or protocol numbers, or ranges of the form START..END,\n'
              'may be given on the command line. E.g. "main.py 1.12.2 1.13" shows only the\n'
              'difference between releases 1.12.2 and 1.13; and "main.py 315..340" shows all\n'
              'versions with protocol numbers between 315 and 340, inclusive.\n'
              '\n'
              'RFLAGS: To save time, intermediate data are saved under the "func-cache"\n'
              'directory. When the script or source data are changed, RFLAGS may be given to\n'
              'tell which data need to be recalculated. Alternatively, all (non-dot)files in\n'
              'the func-cache may be deleted, to recalculate everything.\n'
              '\n'
              'The possible RFLAGS are:', file=sys.stderr)

        rflags = [
            (val.doc_order, '-r%s' % key, val.rdoc)
            for (key, val) in get_cacheable().items()
            if getattr(val, 'refreshable', False)
        ] + [
            (1, refresh_min_proto_arg + 'VER',
             'Recalculate only for protocol versions >= this value.'),
            (2, refresh_max_proto_arg + 'VER',
             'Recalculate only for protocol versions <= this value.')
        ]
        for _, arg, doc in sorted(a for a in rflags if a[0] is not None):
            print(' '*3 + '\33[1m%s\33[0m' % arg, file=sys.stderr)
            for line in doc.split('\n'): print(' '*6 + line, file=sys.stderr)
        sys.exit(0)

    show_versions = []
    pycraft_only = False
    for arg in sys.argv[1:]:
        if arg.startswith(refresh_min_proto_arg):
            cache.refresh_min_proto = int(arg[len(refresh_min_proto_arg):])
        elif arg.startswith(refresh_max_proto_arg):
            cache.refresh_max_proto = int(arg[len(refresh_max_proto_arg):])
        elif arg.startswith('-r'):
            refresh_names.add(arg[2:])
        elif arg in ('-p', '--pycraft-only'):
            pycraft_only = True
        elif arg.startswith('-'):
            print('Error: unrecognised flag: %s.' % arg, file=sys.stderr)
            sys.exit(2)
        else:
            def protocol(spec):
                for ver in version_urls.keys():
                    if spec in (ver.name, str(ver.protocol)):
                        return ver.protocol
                print('Error: unrecognised Minecraft version: %s.' % spec,
                      file=sys.stderr)
                sys.exit(2)

            if '..' in arg:
                start, end = sorted(map(protocol, arg.split('..', 1)))
            else:
                start = protocol(arg)
                end = start

            for ver in sorted(version_urls.keys(), key=lambda v: -v.protocol):
                if ver.protocol > end: continue
                if ver.protocol < start: break
                show_versions.append(ver)

    show_versions = sorted(show_versions, key=lambda v: v.protocol,
                           reverse=True) if show_versions else None
    matrix_html(show_versions=show_versions, pycraft_only=pycraft_only)

    for vsn, url in version_urls.items():
        unused_func_cache_files.discard(get_url_hash(url))
        unused_www_cache_files.discard(get_url_hash(url))
    if unused_www_cache_files:
        print('Unused www-cache files:', file=sys.stderr)
        print('  ' + ' '.join(sorted(unused_www_cache_files)), file=sys.stderr)
    if unused_func_cache_files:
        print('Unused func-cache files:', file=sys.stderr)
        print('  ' + ' '.join(sorted(unused_func_cache_files)), file=sys.stderr)
