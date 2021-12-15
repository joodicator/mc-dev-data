#!/usr/bin/env python3

from urllib.request import urlopen
import sys
import os.path

import bs4

if len(sys.argv) == 3:
    min_rel_name, max_rel_name = sys.argv[1:]
elif len(sys.argv) == 2:
    min_rel_name, max_rel_name = sys.argv[1], None
else:
    self = os.path.basename(sys.argv[0])
    print('Usage: %s MIN_REL_NAME [MAX_REL_NAME]' % self, file=sys.stderr)
    sys.exit(2)

with urlopen('https://wiki.vg/Protocol_version_numbers') as stream:
    charset = stream.info().get_param('charset')
    soup = bs4.BeautifulSoup(stream, 'lxml', from_encoding=charset)

rows = iter(soup.find('table', class_='wikitable').find_all('tr'))
header = tuple(th.get_text().strip() for th in next(rows).find_all('th'))
rows = (dict(zip(header, row.find_all('td'))) for row in rows)
REL_NAME, VSN_NUM, LAST_DOC = \
    'Release name', 'Version number', 'Last known documentation'

if max_rel_name is not None:
    for row in rows:
        if row[REL_NAME].get_text().strip() == max_rel_name:
            break
    else:
        raise ValueError('No release name of %r was found.' % max_rel_name)

for row in rows:
    name = row[REL_NAME].get_text().strip()
    pv = row[VSN_NUM].get_text().strip().replace('Snapshot ', 'PRE|')
    if row[LAST_DOC].a is None:
        continue

    url = row[LAST_DOC].a['href']
    if url.startswith('/'):
        url = 'https://wiki.vg' + url
    pad = ' '*(26 - len(repr(name)) - len(pv))
    print('    (Vsn(%r,%s%s), %r),' % (name, pad, pv, url))

    if name == min_rel_name:
        break
else:
    raise ValueError('No release name of %r was found', min_rel_name)
