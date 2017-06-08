#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.request import urlopen
from contextlib import closing
from collections import namedtuple
import hashlib
import os.path
import sys
import re


matrix_id = namedtuple(
    'matrix_id', ('id', 'changed'))
vsn = namedtuple(
    'vsn', ('name', 'protocol'))
version_diff = namedtuple(
    'version_diff', ('old', 'new'))
pre_packet = namedtuple(
    'pre_packet', ('name', 'old_id', 'new_id', 'changed'))
rel_packet = namedtuple(
    'rel_packet', ('name', 'id'))


version_urls = {
    vsn('1.12',      335): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12924',
    vsn('1.12-pre7', 334): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12918',
    vsn('1.12-pre6', 333): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12909',
    vsn('1.12-pre5', 332): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10809',
    vsn('1.12-pre4', 331): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10804',
    vsn('1.12-pre3', 330): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10803',
    vsn('1.12-pre2', 329): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10418',
    vsn('1.12-pre1', 328): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=9819',
    vsn('17w18b',    327): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8548',
    vsn('17w18a',    326): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8546',
    vsn('17w17b',    325): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8536',
    vsn('17w17a',    324): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8528',
    vsn('17w16b',    323): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8519',
    vsn('17w16a',    322): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8515',
    vsn('17w15a',    321): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8499',
    vsn('17w14a',    320): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8490',
    vsn('17w13b',    319): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8475',
    vsn('17w13a',    318): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8454',
    vsn('17w06a',    317): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8414',
    vsn('1.11.2',    316): 'http://wiki.vg/index.php?title=Protocol&oldid=8543',
}


patch = {
    (vsn('17w13a', 318), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w13b', 319), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w14a', 320), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w15a', 321), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w16a', 322), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w16b', 323), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w17a', 324), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w17b', 325), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w18a', 326), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('17w18b', 327), pre_packet('Particle', 0x24, 0x25, False)):
                         pre_packet('Map',      0x24, 0x25, False),
    (vsn('1.12-pre1', 328), pre_packet('Particle', 0x24, 0x25, False)):
                            pre_packet('Map',      0x24, 0x25, False),
    (vsn('1.12-pre2', 329), pre_packet('Particle', 0x24, 0x25, False)):
                            pre_packet('Map',      0x24, 0x25, False),
    (vsn('1.12-pre3', 330), pre_packet('Particle', 0x24, 0x25, False)):
                            pre_packet('Map',      0x24, 0x25, False),
    (vsn('1.12-pre4', 331), pre_packet('Particle', 0x24, 0x25, False)):
                            pre_packet('Map',      0x24, 0x25, False),
}


def matrix_html():
    matrix = version_packet_ids()
    versions = sorted(matrix.keys(), key=lambda v: v.protocol)
    packet_names = sorted({n for pis in matrix.values() for n in pis.keys()})

    print('<!DOCTYPE html>')
    print('<html>')
    print('    <head>')
    print('        <meta charset="utf-8">')
    print('        <title></title>')
    print('        <link rel="stylesheet" href="style.css">')
    print('    </head>')
    print('    <body>')
    print('      <table class="packet-id-matrix">')

    print('          <colgroup>' + ' <col>'*(len(versions)+1))

    print('          <tr> <th></th>', end='')
    for version in versions:
        print(' <th>%s<br>%s</th>' % (version.name, version.protocol), end='')
    print(' </tr>')

    for packet_name in packet_names:
        print('          <tr> <th>%s</th>' % packet_name, end='')
        prev_cell = None
        for version in versions:
            if packet_name in matrix[version]:
                cell = matrix[version][packet_name]
                classes = []
                if prev_cell and cell.id != prev_cell.id:
                    classes.append('packet-id-changed')
                if cell.changed:
                    classes.append('packet-format-changed')
                print(' <td%s>0x%02X</td>' % (
                    ' class="%s"' % ' '.join(classes) if classes else '', cell.id),
                    end='')
                prev_cell = cell
            else:
                print(' <td></td>', end='')
                prev_cell = None
        print('</tr>')

    print('      </table>')
    print('   </body>')
    print('</html>')


def version_packet_ids():
    matrix = {}
    for v, url in sorted(version_urls.items(), key=lambda i: i[0].protocol):
        soup = get_soup(url)
        heading = soup.find(id='firstHeading').text.strip() 
        if heading == 'Pre-release protocol':
            from_v, to_v = pre_versions(soup)
            assert v == to_v, '%r != %r' % (v, to_v)
            matrix[v] = {}
            seen_names = set()
            for packet in pre_packets(soup):
                packet = patch.get((v, packet), packet)
                if packet is None: continue
                assert packet.name not in seen_names, \
                    '[%s] Duplicate packet name: %r.' % (v.name, packet.name)
                seen_names.add(packet.name)
                if packet.old_id is None:
                    assert packet.name not in matrix[from_v]
                else:
                    assert packet.name in matrix[from_v], \
                        '[%s] %r not in matrix[%r]' % (v.name, packet.name, from_v)
                    assert packet.old_id == matrix[from_v][packet.name].id, \
                        '[%s] 0x%02x != matrix[%r][%r].id == 0x%02x' % (
                        v.name, packet.old_id, from_v, packet.name,
                        matrix[from_v][packet.name].id)
                matrix[v][packet.name] = matrix_id(
                    id = packet.old_id if packet.new_id is None else packet.new_id,
                    changed = packet.changed)
            for packet, id in matrix[from_v].items():
                if packet in matrix[v]: continue
                matrix[v][packet] = matrix_id(id=id.id, changed=False)
        elif heading == 'Protocol':
            rel_v = rel_version(soup)
            assert v == rel_v, '%r != %r' % (v, rel_v)
            matrix[v] = {}
            for packet in rel_packets(soup):
                packet = patch.get((v, packet), packet)
                if packet is None: continue
                matrix[v][packet.name] = matrix_id(packet.id, None)
        else:
            raise AssertionError('Unrecognised article title: %r' % heading)
    return matrix


def norm_packet_name(name):
    return {
        'Confirm Transation (clientbound)': 'Confirm Transaction (clientbound)',
        'Unlock Recipe':                    'Unlock Recipes'
    }.get(name, name)


def get_soup(url):
    url_hash = hashlib.new('sha1', url.encode('utf8')).hexdigest()
    cache_file = os.path.join(os.path.dirname(__file__), 'www-cache/%s' % url_hash)
    if os.path.exists(cache_file):
        with open(cache_file) as file:
            charset = 'utf8'
            data = file.read().encode(charset)
    else:
        print('Downloading %s...' % url, file=sys.stderr)
        with urlopen(url) as stream:
            charset = stream.info().get_param('charset')
            data = stream.read()
        with open(cache_file, 'w') as file:
            file.write(data.decode(charset))
    return BeautifulSoup(data, 'lxml', from_encoding=charset)


PRE_VER_RE = re.compile(r'(?P<name>\d[^,]*), protocol (?P<protocol>\d+)')
def pre_versions(soup):
    vs = []
    for a in soup.find(id='mw-content-text').find('p').findAll('a'):
        m = PRE_VER_RE.match(a.text.strip())
        if m is None: continue
        vs.append(vsn(
            name     = m.group('name'),
            protocol = int(m.group('protocol'))))
    if len(vs) == 2:
        return version_diff(*vs)
    else:
        raise AssertionError('Found %d versions in first paragraph where 2'
        ' are expected: %r' % (len(vs), vs))


def pre_packets(soup):
    seen_names = set()
    table = soup.find(id='Packets').findNext('table', class_='wikitable')
    if table is not None:
        cols = {}
        ncols = 0
        for th in table.findChild('tr').findChildren('th'):
            cols[th.text.strip()] = ncols
            ncols += int(th.get('colspan', '1'))

        c_id, c_name, c_doc = 'ID', 'Packet name', 'Documentation'
        assert (cols[c_id], cols[c_name], cols[c_doc], ncols) == (0, 1, 2, 4), \
        '%r != %r' % ((cols[c_id], cols[c_name], cols[c_doc], ncols), (0, 1, 2, 4))

        for tr in table.findChildren('tr'):
            tds = tr.findChildren('td')
            if len(tds) != ncols: continue
            if any(int(td.get('colspan', '1')) != 1 for td in tds): continue

            changed = tds[cols[c_doc]+1].text.strip() != '(unchanged)'
            if changed: assert tds[cols[c_doc]+1].text.strip() == 'Pre'

            if tds[cols[c_id]].find('ins') and tds[cols[c_id]].find('del'):
                # Existing packet with changed packet ID.
                old_id = int(tds[cols[c_id]].find('del').text.strip(), 16)
                new_id = int(tds[cols[c_id]].find('ins').text.strip(), 16)
                assert tds[cols[c_doc]].text.strip() == 'Current'
            elif 'background-color: #d9ead3' in tr.get('style', ''):
                # Newly added packet.
                old_id = None
                new_id = int(tds[cols[c_id]].text.strip(), 16)
                assert changed and tds[cols[c_doc]].text.strip() == ''
            else:
                # Existing packet without changed packet ID.
                old_id = int(tds[cols[c_id]].text.strip(), 16)
                new_id = None
                assert changed and tds[cols[c_doc]].text.strip() == 'Current'

            name = norm_packet_name(tds[cols[c_name]].text.strip())
            yield pre_packet(
                name=name, old_id=old_id, new_id=new_id, changed=changed)


def rel_packets(soup):
    content = soup.find(id='mw-content-text')
    for table in content.findChildren('table', class_='wikitable'):
        if table.findChild('tr').findChild('th').text.strip() != 'Packet ID':
            continue
        id = int(table.findChildren('tr')[1].findChild('td').text.strip(), 16)
        name = norm_packet_name(table.findPreviousSibling('h4').text.strip())
        yield rel_packet(name=name, id=id)


REL_VER_RE = re.compile(r'\(currently (?P<protocol>\d+) in Minecraft'
                        r' (?P<name>\d[^)]*)\)')
def rel_version(soup):
    td = soup.find('td', string=re.compile('^\s*Protocol Version\s*$'))
    td = td.findNextSibling('td')
    assert td.text.strip() == 'VarInt'
    td = td.findNextSibling('td')
    m = REL_VER_RE.search(td.text)
    return vsn(name=m.group('name'), protocol=int(m.group('protocol')))


if __name__ == '__main__':
    matrix_html()

