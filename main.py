#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.request import urlopen
from contextlib import closing
from collections import namedtuple
import hashlib
import os.path
import os
import sys
import re


MatrixID = namedtuple(
    'MatrixID', ('id', 'changed'))
MatrixID.__str__ = lambda r: \
    'MatrixID(id=0x%02X, changed=%r)' \
    % (r.id, r.changed)

Vsn = namedtuple(
    'Vsn', ('name', 'protocol'))

VersionDiff = namedtuple(
    'VersionDiff', ('old', 'new'))

PrePacket = namedtuple(
    'PrePacket', ('name', 'old_id', 'new_id', 'changed', 'state', 'bound'))
PrePacket.__str__ = lambda r: \
    'PrePacket(name=%r, old_id=0x%02X, new_id=0x%02X, changed=%r, state=%r, bound=%r)' \
    % (r.name, r.old_id, r.new_id, r.changed, r.state, r.bound)

RelPacket = namedtuple(
    'RelPacket', ('name', 'id', 'state', 'bound'))
RelPacket.__str__ = lambda r: \
    'RelPacket(name=%r, id=0x%02X, state=%r, bound=%r)' \
    % (r.name, r.id, r.state, r.bound)

PacketClass = namedtuple(
    'PacketClass', ('name', 'state', 'bound'))

version_urls = {
    Vsn('1.12.1',      338): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13287',
    Vsn('1.12.1-pre1', 337): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13267',
    Vsn('17w31a',      336): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13265',
    Vsn('1.12',        335): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12929',
    Vsn('1.12-pre7',   334): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12918',
    Vsn('1.12-pre6',   333): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12909',
    Vsn('1.12-pre5',   332): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10809',
    Vsn('1.12-pre4',   331): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10804',
    Vsn('1.12-pre3',   330): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10803',
    Vsn('1.12-pre2',   329): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10418',
    Vsn('1.12-pre1',   328): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=9819',
    Vsn('17w18b',      327): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8548',
    Vsn('17w18a',      326): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8546',
    Vsn('17w17b',      325): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8536',
    Vsn('17w17a',      324): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8528',
    Vsn('17w16b',      323): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8519',
    Vsn('17w16a',      322): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8515',
    Vsn('17w15a',      321): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8499',
    Vsn('17w14a',      320): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8490',
    Vsn('17w13b',      319): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8475',
    Vsn('17w13a',      318): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8454',
    Vsn('17w06a',      317): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8414',
    Vsn('1.11.2',      316): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8356',
    Vsn('1.11',        315): 'http://wiki.vg/index.php?title=Protocol&oldid=8405',
    Vsn('1.11-pre1',   314): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8249',
    Vsn('16w44a',      313): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8246',
    Vsn('16w42a',      312): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8225',
    Vsn('16w41a',      311): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8218',
    Vsn('16w40a',      310): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8204',
    Vsn('16w39c',      309): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8177',
    Vsn('16w39b',      308): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8149',
    Vsn('16w39a',      307): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8141',
    Vsn('16w38a',      306): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8118',
    Vsn('16w36a',      305): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8099',
    Vsn('16w35a',      304): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8094',
    Vsn('16w33a',      303): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8084',
    Vsn('16w32b',      302): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8063',
    Vsn('16w32a',      301): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8062',
    Vsn('1.10.2',      210): 'http://wiki.vg/index.php?title=Protocol&oldid=8235',
    Vsn('1.9.4',       110): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7804',
    Vsn('1.9.2',       109): 'http://wiki.vg/index.php?title=Protocol&oldid=7817',
    Vsn('1.9.1',       108): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7552',
    Vsn('1.9',         107): 'http://wiki.vg/index.php?title=Protocol&oldid=7617',
    Vsn('1.8.9',       47):  'http://wiki.vg/index.php?title=Protocol&oldid=7368',
}

patch = {
    (Vsn('1.9.1', 108), VersionDiff(Vsn('1.9', 107), Vsn('1.9.1-pre3', 108))):
                        VersionDiff(Vsn('1.9', 107), Vsn('1.9.1', 108)),
    (Vsn('1.9.4', 110), VersionDiff(Vsn('1.9.2', 109), Vsn('1.9.3-pre3', 110))):
                        VersionDiff(Vsn('1.9.2', 109), Vsn('1.9.4', 110)),

    (Vsn('17w13a', 318), PrePacket('Unknown', None, 0x01, True, 'Play', 'Server')):
                         PrePacket('Craft Recipe Request', None, 0x01, True, 'Play', 'Server'),
    (Vsn('17w13b', 319), PrePacket('Unknown', None, 0x01, True, 'Play', 'Server')):
                         PrePacket('Craft Recipe Request', None, 0x01, True, 'Play', 'Server'),
    (Vsn('17w13a', 318), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w13b', 319), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w14a', 320), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w15a', 321), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w16a', 322), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w16b', 323), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w17a', 324), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w17b', 325), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w18a', 326), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w18b', 327), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre1', 328), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                            PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre2', 329), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                            PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre3', 330), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                            PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre4', 331), PrePacket('Particle', 0x24, 0x25, False, 'Play', 'Client')):
                            PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w31a', 336), PrePacket('Craft Recipe Request', 0x01, None, True, 'Play', 'Server')):
                         None,
    (Vsn('17w31a', 336), PrePacket('Unknown (serverbound)', None, 0x12, True, 'Play', 'Server')):
                         PrePacket('Craft Recipe Request', 0x01, 0x12, True, 'Play', 'Server'),
    (Vsn('17w31a', 336), PrePacket('Unknown (clientbound)', None, 0x2B, True, 'Play', 'Client')):
                         PrePacket('Craft Recipe Response', None, 0x2B, True, 'Play', 'Client'),
    (Vsn('1.12.1-pre1', 337), PrePacket('Unknown (serverbound)', None, 0x12, True, 'Play', 'Server')):
                              PrePacket('Craft Recipe Request', 0x01, 0x12, True, 'Play', 'Server'),
    (Vsn('1.12.1-pre1', 337), PrePacket('Unknown (clientbound)', None, 0x2B, True, 'Play', 'Client')):
                              PrePacket('Craft Recipe Response', None, 0x2B, True, 'Play', 'Client'),
    (Vsn('1.12.1-pre1', 337), PrePacket('Craft Recipe Request', 0x01, None, True, 'Play', 'Server')):
                              None,
    (Vsn('1.12.1', 338), VersionDiff(Vsn('1.12', 335), Vsn('1.12.1-pre1', 338))):
                         VersionDiff(Vsn('1.12', 335), Vsn('1.12.1', 338)),
    (Vsn('1.12.1', 338), PrePacket('Craft Recipe Request', 0x01, None, True, 'Play', 'Server')):
                         None,
    (Vsn('1.12.1', 338), PrePacket('Craft Recipe Request', None, 0x12, True, 'Play', 'Server')):
                         PrePacket('Craft Recipe Request', 0x01, 0x12, True, 'Play', 'Server'),
}


norm_packet_name_dict = {
    'Chunk data':                           'Chunk Data',
    'Entity effect':                        'Entity Effect',
    'Confirm Transation (clientbound)':     'Confirm Transaction (clientbound)',
    'Unlock Recipe':                        'Unlock Recipes',
    'Advancement Progress':                 'Select Advancement Tab',
    'Recipe Displayed':                     'Crafting Book Data',
    'Prepare Crafting Grid':                'Craft Recipe Request',
}
for name in 'Animation', 'Chat Message', 'Keep Alive', 'Plugin Message', \
'Player Position And Look', 'Held Item Change', 'Close Window', \
'Confirm Transaction', 'Player Abilities', 'Tab-Complete', 'Update Sign':
    norm_packet_name_dict[(name, 'Client')] = '%s (clientbound)' % name
    norm_packet_name_dict[(name, 'Server')] = '%s (serverbound)' % name
for name in 'Disconnect', 'Set Compression':
    norm_packet_name_dict[(name, 'Login')] = '%s (login)' % name
    norm_packet_name_dict[(name, 'Play')] = '%s (play)' % name

def norm_packet_name(name, state=None, bound=None):
    n_names = set()
    for query in (name, (name, state), (name, bound)):
        if query in norm_packet_name_dict:
            n_names.add(norm_packet_name_dict[query])
    assert len(n_names) <= 1, \
           'Multiple normalisations for %r: %s.' % (name, n_names)
    return n_names.pop() if n_names else name

def matrix_html():
    matrix = version_packet_ids()
    versions = sorted(matrix.keys(), key=lambda v: v.protocol, reverse=True)
    packet_classes = sorted({p for ids in matrix.values() for p in ids.keys()})

    print('<!DOCTYPE html>')
    print('<html>')
    print('    <head>')
    print('        <meta charset="utf-8">')
    print('        <title></title>')
    print('        <link rel="stylesheet" href="style.css">')
    print('        <script src="main.js" type="text/javascript"></script>')
    print('    </head>')
    print('    <body>')
    print('    <div class="packet-id-matrix-container">')

    print('      <table class="packet-id-matrix top-header">')
    print('          <colgroup>' + ' <col>'*(len(versions)+1))
    print('          <tr> <th></th>', end='')
    for version in versions:
        print(' <th><a href="%s">%s</a><br>%s</th>' % (
            version_urls[version], version.name, version.protocol), end='')
    print(' </tr>')
    print('      </table>')

    print('      <table class="packet-id-matrix contents">')
    print('          <colgroup>' + ' <col>'*(len(versions)+1))
    for packet_class in packet_classes:
        print('          <tr> <th></th>', end='')
        for i in range(len(versions)):
            prev_cell = matrix[versions[i+1]].get(packet_class) \
                        if i<len(versions)-1 else None
            if packet_class in matrix[versions[i]]:
                cell = matrix[versions[i]][packet_class]
                classes = []
                if cell.changed is None:
                    classes.append('packet-base')
                if not prev_cell:
                    if i < len(versions) - 1:
                        classes.append('packet-added')
                else:
                    if cell.id != prev_cell.id:
                        classes.append('packet-id-changed')
                    if cell.changed:
                        classes.append('packet-format-changed')
                print(' <td%s>0x%02X</td>' % (
                    ' class="%s"' % ' '.join(classes) if classes else '', cell.id),
                    end='')
            elif prev_cell:
                print(' <td class="packet-removed"></td>')
            else:
                print(' <td></td>', end='')
        print('</tr>')
    print('      </table>')

    print('      <table class="packet-id-matrix left-header">')
    print('          <colgroup><col></col></colgroup>')
    for packet_class in packet_classes:
        print('          <tr><th class="packet-state-%s packet-bound-%s">%s</th></tr>' % (
            packet_class.state.lower(), packet_class.bound.lower(),
            packet_class.name), end='')
    print('      </table>')

    print('   </div>')
    print('   </body>')
    print('</html>')


def version_packet_ids():
    used_patches = set()
    packet_classes = {}
    matrix = {}
    for v, url in sorted(version_urls.items(), key=lambda i: i[0].protocol):
        soup = get_soup(url)
        heading = soup.find(id='firstHeading').text.strip() 
        if heading == 'Pre-release protocol':
            vdiff = pre_versions(soup)
            if (v, vdiff) in patch:
                used_patches.add((v, vdiff))
                vdiff = patch[v, vdiff]
            from_v, to_v = vdiff
            assert v == to_v, '%r != %r' % (v, to_v)
            matrix[v] = {}
            seen_names = {}
            for packet in pre_packets(soup, v):
                if (v, packet) in patch:
                    used_patches.add((v, packet))
                    packet = patch[v, packet]
                if packet is None: continue
                assert packet.name not in seen_names, \
                    '[%s] Duplicate packet name:\n%s\n%s' % \
                    (v.name, seen_names[packet.name], packet)
                seen_names[packet.name] = packet

                packet_class = PacketClass(
                    name=packet.name, state=packet.state, bound=packet.bound)
                if packet.name not in packet_classes:
                    packet_classes[packet.name] = packet_class
                assert packet_class == packet_classes[packet.name], \
                    '[%s] %r != %r' % (v.name, packet_class, packet_classes[packet.name])

                if packet.old_id is None:
                    assert packet_class not in matrix[from_v], \
                           '[%s] %r in matrix[%r]' % (v.name, packet_class, from_v)
                else:
                    assert packet_class in matrix[from_v], \
                        '[%s] %r not in matrix[%r]' % (v.name, packet_class, from_v)
                    assert packet.old_id == matrix[from_v][packet_class].id, \
                        '[%s] 0x%02x != matrix[%r][%r].id == 0x%02x' % (
                        v.name, packet.old_id, from_v, packet_class,
                        matrix[from_v][packet_class].id)
                if packet.new_id is not None:
                    matrix[v][packet_class] = MatrixID(
                        id = packet.new_id,
                        changed = packet.changed)
            for packet_class, id in matrix[from_v].items():
                if packet_class.name in seen_names: continue
                matrix[v][packet_class] = id._replace(changed=False)
        elif heading == 'Protocol':
            rel_v = rel_version(soup)
            if rel_v.name is None:
                rel_v = Vsn(v.name, rel_v.protocol)
            assert v == rel_v, '%r != %r' % (v, rel_v)
            matrix[v] = {}
            seen_names = {}
            for packet in rel_packets(soup):
                if (v, packet) in patch:
                    used_patches.add((v, packet))
                    packet = patch[v, packet]
                if packet is None: continue
                assert packet.name not in seen_names, \
                    '[%s] Duplicate packet name:\n%s\n%s.' \
                    % (v.name, seen_names[packet.name], packet)
                seen_names[packet.name] = packet

                packet_class = PacketClass(
                    name=packet.name, state=packet.state, bound=packet.bound)
                if packet.name not in packet_classes:
                    packet_classes[packet.name] = packet_class
                assert packet_classes[packet.name] == packet_class

                matrix[v][packet_class] = MatrixID(packet.id, None)
        else:
            raise AssertionError('Unrecognised article title: %r' % heading)

        unused_patches = set(k for k in patch.keys() if k[0] == v and k not in used_patches)
        if unused_patches:
            print(used_patches, file=sys.stderr)
            raise AssertionError('Unused patches:\n'
            + '\n'.join('%s -> %s' % (p, patch[p]) for p in unused_patches))
    
    return matrix


cache_dir = os.path.join(os.path.dirname(__file__), 'www-cache')
unused_cache_files = set(os.listdir(cache_dir))
def get_soup(url):
    url_hash = hashlib.new('sha1', url.encode('utf8')).hexdigest()
    cache_file = os.path.join(cache_dir, url_hash)
    if os.path.exists(cache_file):
        with open(cache_file) as file:
            charset = 'utf8'
            data = file.read().encode(charset)
        unused_cache_files.discard(url_hash)
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
        vs.append(Vsn(
            name     = m.group('name'),
            protocol = int(m.group('protocol'))))
    if len(vs) == 2:
        return VersionDiff(*vs)
    else:
        raise AssertionError('Found %d versions in first paragraph where 2'
        ' are expected: %r' % (len(vs), vs))


def pre_packets(soup, vsn):
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

        state, bound = None, None
        for tr in table.findChildren('tr')[1:]:
            ths = tr.findChildren('th')
            if len(ths) == 1 and int(ths[0].get('colspan', '1')) == ncols:
                match = re.match(r'(\S+) (\S+)bound', ths[0].text.strip())
                if match:
                    state = match.group(1).capitalize()
                    bound = match.group(2).capitalize()
                    continue
            tds = tr.findChildren('td')
            if len(tds) != ncols or any(int(td.get('colspan', '1')) != 1 for td in tds):
                raise AssertionError('[%s] Unrecognised table row: %s' % (vsn.name, tr))

            changed = tds[cols[c_doc]+1].text.strip() != '(unchanged)'

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
                old_id = int(tds[cols[c_id]].text.strip(), 16)
                if 'text-decoration: line-through' in tr.get('style', ''):
                    # Removed packet.
                    new_id = None
                else:
                    # Existing packet without changed packet ID.
                    new_id = old_id
                assert changed and tds[cols[c_doc]].text.strip() == 'Current'

            if changed:
                expect = '' if new_id is None else 'Pre'
                assert tds[cols[c_doc]+1].text.strip() == expect, \
                '[%s] [%s] %r != %r' % (vsn.name, tds[cols[c_name]].text.strip(),
                                        tds[cols[c_doc]+1].text.strip(), expect)

            name = tds[cols[c_name]].text.strip()
            name = norm_packet_name(name, state, bound)
            yield PrePacket(
                name=name, old_id=old_id, new_id=new_id, changed=changed,
                state=state, bound=bound)


def rel_packets(soup):
    content = soup.find(id='mw-content-text')
    for table in content.findChildren('table', class_='wikitable'):
        ths = table.findChildren('tr')[0].findChildren('th')
        tds = table.findChildren('tr')[1].findChildren('td')
        id, state, bound = None, None, None
        for th, td in zip(ths, tds):
            if th.text.strip() == 'Packet ID':
                id = int(td.text.strip(), 16)
            elif th.text.strip() == 'State':
                state = td.text.strip()
            elif th.text.strip() == 'Bound To':
                bound = td.text.strip()
        if id is None:
            continue
        name = table.findPreviousSibling('h4').text.strip()
        name = norm_packet_name(name, state, bound)
        yield RelPacket(name=name, id=id, state=state, bound=bound)


REL_VER_RE = re.compile(r'\(currently (?P<protocol>\d+)'
                        r'( in Minecraft (?P<name>\d[^)]*))?\)')
def rel_version(soup):
    td = soup.find('td', string=re.compile('^\s*Protocol Version\s*$'))
    td = td.findNextSibling('td')
    assert td.text.strip() == 'VarInt'
    td = td.findNextSibling('td')
    m = REL_VER_RE.search(td.text)
    protocol = int(m.group('protocol')) if m.group('protocol') else None
    return Vsn(name=m.group('name'), protocol=protocol)


if __name__ == '__main__':
    matrix_html()
    if unused_cache_files:
        print('Unused cache files:', file=sys.stderr)
        print(' '.join(sorted(unused_cache_files)), file=sys.stderr)
