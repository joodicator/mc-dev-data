#!/usr/bin/env python3

import inspect
import sys
import math

from mcdevdata.sources import version_urls
from mcdevdata.util import get_url_hash
from mcdevdata.cache import unused_www_cache_files, unused_func_cache_files
from mcdevdata.cache import refresh_names, get_cacheable
from mcdevdata.html_out import matrix_html

refresh_min_proto, refresh_min_proto_arg = -math.inf, '--r-min-proto='
refresh_max_proto, refresh_max_proto_arg =  math.inf, '--r-max-proto='

if __name__ == '__main__':
    args = [
        (val.doc_order, '-r%s' % key, val.rdoc)
        for (key, val) in get_cacheable().items()
        if getattr(val, 'refreshable', False)
    ] + [
        (1, refresh_min_proto_arg + 'VER',
         'Recalculate only for protocol versions >= this value.'),
        (2, refresh_max_proto_arg + 'VER',
         'Recalculate only for protocol versions <= this value.'),
    ]

    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        print('Usage: main.py [-h|--help] [VERSIONS...] [RFLAGS...]\n'
              '\n'
              'This script generates and prints to stdout the contents of index.htm.\n'
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
        for _, arg, doc in sorted(args):
            print(' '*3 + '\33[1m%s\33[0m' % arg, file=sys.stderr)
            for line in doc.split('\n'): print(' '*6 + line, file=sys.stderr)
        sys.exit(0)

    show_versions = []
    for arg in sys.argv[1:]:
        if arg.startswith(refresh_min_proto_arg):
            refresh_min_proto = int(arg[len(refresh_min_proto_arg):])
        elif arg.startswith(refresh_max_proto_arg):
            refresh_max_proto = int(arg[len(refresh_max_proto_arg):])
        elif arg.startswith('-r'):
            refresh_names.add(arg[2:])

        if arg.startswith('-'):
            for arg_spec in args:
                if arg_spec[1].startswith('--'):
                    if arg.startswith(arg_spec[1].split('=', 1)[0]): break
                elif arg_spec[1].startswith('-'):
                    if arg == arg_spec[1]: break
            else:
                print('Error: unrecognised flag: %s.' % arg, file=sys.stderr)
                sys.exit(2)
            continue

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

        for ver in version_urls.keys():
            if ver.protocol > end: continue
            if ver.protocol < start: break
            show_versions.append(ver)

    show_versions = sorted(show_versions, key=lambda v: v.protocol,
                           reverse=True) if show_versions else None
    matrix_html(show_versions=show_versions)

    for vsn, url in version_urls.items():
        unused_func_cache_files.discard(get_url_hash(url))
        unused_www_cache_files.discard(get_url_hash(url))
    if unused_www_cache_files:
        print('Unused www-cache files:', file=sys.stderr)
        print('  ' + ' '.join(sorted(unused_www_cache_files)), file=sys.stderr)
    if unused_func_cache_files:
        print('Unused func-cache files:', file=sys.stderr)
        print('  ' + ' '.join(sorted(unused_func_cache_files)), file=sys.stderr)
