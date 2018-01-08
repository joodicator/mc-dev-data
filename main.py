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

import minecraft as pycraft
import minecraft.networking.connection as pycraft_connection
from minecraft.networking import packets as pycraft_packets


MatrixID = namedtuple(
    'MatrixID', ('id', 'changed'))
MatrixID.__str__ = lambda r: \
    'MatrixID(id=%s, changed=%r)' \
    % (id_str(r.id), r.changed)

Vsn = namedtuple(
    'Vsn', ('name', 'protocol'))

VersionDiff = namedtuple(
    'VersionDiff', ('old', 'new'))

PrePacket = namedtuple(
    'PrePacket', ('name', 'old_id', 'new_id', 'changed', 'state', 'bound'))
PrePacket.__str__ = lambda r: \
    'PrePacket(name=%r, old_id=%s, new_id=%s, changed=%r, state=%r, bound=%r)' \
    % (r.name, id_str(r.old_id), id_str(r.new_id), r.changed, r.state, r.bound)

RelPacket = namedtuple(
    'RelPacket', ('name', 'id', 'state', 'bound'))
RelPacket.__str__ = lambda r: \
    'RelPacket(name=%r, id=%s, state=%r, bound=%r)' \
    % (r.name, id_str(r.id), r.state, r.bound)

PacketClass = namedtuple(
    'PacketClass', ('name', 'state', 'bound'))

def id_str(id):
    if isinstance(id, int):
        return '0x%02X' % id
    return str(id)

version_urls = {
    Vsn('18w01a',      352): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13576',
    Vsn('17w50a',      351): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13556',
    Vsn('17w49b',      350): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13524',
    Vsn('17w49a',      349): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13516',
    Vsn('17w48a',      348): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13512',
    Vsn('17w47b',      347): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13487',
    Vsn('17w47a',      346): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13476',
    Vsn('17w46a',      345): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13472',
    Vsn('17w45b',      344): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13414',
    Vsn('17w45a',      343): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13413',
    Vsn('17w43b',      342): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13398',
    Vsn('17w43a',      341): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13396',
    Vsn('1.12.2',      340): 'http://wiki.vg/index.php?title=Protocol&oldid=13488',
    Vsn('1.12.2-pre2', 339): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13355',
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
    Vsn('1.10-pre2',   205): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7961',
    Vsn('1.10-pre1',   204): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7950',
    Vsn('16w21b',      203): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7935',
    Vsn('16w21a',      202): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7877',
    Vsn('16w20a',      201): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7859',
    Vsn('1.9.4',       110): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7804',
    Vsn('1.9.2',       109): 'http://wiki.vg/index.php?title=Protocol&oldid=7817',
    Vsn('1.9.1',       108): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7552',
    Vsn('1.9',         107): 'http://wiki.vg/index.php?title=Protocol&oldid=7617',
    Vsn('1.9-pre4',    106): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7412',
    Vsn('16w04a',      97):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7374',
    Vsn('16w02a',      95):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7313',
    Vsn('15w51b',      94):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7261',
    Vsn('15w40b',      76):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7122',
    Vsn('15w38b',      73):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6965',
    Vsn('15w38a',      72):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6932',
    Vsn('15w36d',      70):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6925',
    Vsn('15w36c',      69):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6883',
#    Vsn('15w35e',      66):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6851',
#    Vsn('15w35b',      63):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6829',
#    Vsn('15w34a',      58):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6809',
#    Vsn('15w33c',      57):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6806',
#    Vsn('15w33b',      56):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6796',
#    Vsn('15w33a',      55):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6790',
#    Vsn('15w32c',      54):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6788',
#    Vsn('15w32a',      52):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6785',
#    Vsn('15w31c',      51):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6780',
#    Vsn('15w31b',      50):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6746',
    Vsn('1.8.9',       47):  'http://wiki.vg/index.php?title=Protocol&oldid=7368',
}

patch = {
    (Vsn('1.8.9', 47), RelPacket('Sound Effect', 0x29, 'Play', 'Client')):
                       RelPacket('Named Sound Effect', 0x29, 'Play', 'Client'),
    (Vsn('15w36c', 69), PrePacket('Sound Effect', 0x29, 0x29, False, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x29, False, 'Play', 'Client'),
    (Vsn('15w36d', 70), PrePacket('Sound Effect', 0x29, 0x23, False, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x23, False, 'Play', 'Client'),
    (Vsn('15w38a', 72), PrePacket('Sound Effect', 0x29, 0x23, False, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x23, False, 'Play', 'Client'),
    (Vsn('15w38b', 73), PrePacket('Sound Effect', 0x29, 0x23, False, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x23, False, 'Play', 'Client'),
    (Vsn('15w40b', 76), PrePacket('Sound Effect', 0x29, 0x23, False, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x23, False, 'Play', 'Client'),
    (Vsn('15w36c', 69), VersionDiff(Vsn('1.8.8', 47), Vsn('15w36c', 69))):
                        VersionDiff(Vsn('1.8.9', 47), Vsn('15w36c', 69)),
    (Vsn('15w36d', 70), VersionDiff(Vsn('1.8.8', 47), Vsn('15w36d', 70))):
                        VersionDiff(Vsn('1.8.9', 47), Vsn('15w36d', 70)),
    (Vsn('15w38a', 72), VersionDiff(Vsn('1.8.8', 47), Vsn('15w38a', 72))):
                        VersionDiff(Vsn('1.8.9', 47), Vsn('15w38a', 72)),
    (Vsn('15w38b', 73), VersionDiff(Vsn('1.8.8', 47), Vsn('15w38b', 73))):
                        VersionDiff(Vsn('1.8.9', 47), Vsn('15w38b', 73)),
    (Vsn('15w40b', 76), VersionDiff(Vsn('1.8.8', 47), Vsn('15w40b', 76))):
                        VersionDiff(Vsn('1.8.9', 47), Vsn('15w40b', 76)),
    (Vsn('15w51b', 94), PrePacket('Chat Message (serverbound)', 0x02, 0x02, False, 'Play', 'Server')):
                        PrePacket('Chat Message (serverbound)', 0x01, 0x02, False, 'Play', 'Server'),
    (Vsn('16w02a', 95), PrePacket('Chat Message (serverbound)', 0x02, 0x02, False, 'Play', 'Server')):
                        PrePacket('Chat Message (serverbound)', 0x01, 0x02, False, 'Play', 'Server'),
    (Vsn('15w51b', 94), PrePacket('Named Sound Effect', 0x2F, 0x19, False, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x19, False, 'Play', 'Client'),
    (Vsn('16w02a', 95), PrePacket('Named Sound Effect', 0x2F, 0x19, True, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x19, True, 'Play', 'Client'),
    (Vsn('16w04a', 97), PrePacket('Named Sound Effect', 0x2F, 0x19, True, 'Play', 'Client')):
                        PrePacket('Named Sound Effect', 0x29, 0x19, True, 'Play', 'Client'),
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
    'Maps':                             'Map',
    'Chunk data':                       'Chunk Data',
    'Entity effect':                    'Entity Effect',
    'Confirm Transation (clientbound)': 'Confirm Transaction (clientbound)',
    'Unlock Recipe':                    'Unlock Recipes',
    'Advancement Progress':             'Select Advancement Tab',
    'Recipe Displayed':                 'Crafting Book Data',
    'Prepare Crafting Grid':            'Craft Recipe Request',
    'Sign Editor Open':                 'Open Sign Editor',
    'Player List Header/Footer':        'Player List Header And Footer',
    'Vehicle Move (Serverbound)':       'Vehicle Move (serverbound)',
    ('Vehicle Move?', 'Server'):        'Vehicle Move (serverbound)',   
}
for name in 'Animation', 'Chat Message', 'Keep Alive', 'Plugin Message', \
'Player Position And Look', 'Held Item Change', 'Close Window', 'Vehicle Move', \
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
    pycraft_classes = pycraft_packet_classes(matrix)

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
        psv = version.protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS
        print(' <th%(c)s><a href="%(u)s" title="%(n)s">%(n)s</a><br>%(v)s</th>'
            % {'u':version_urls[version], 'n':version.name, 'v':version.protocol,
               'c':' class="pycraft-supported-version"' if psv else ''}, end='')
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
                classes = ['packet-present']

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

                if versions[i].protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS:
                    classes.append('pycraft-supported-version')
                if packet_class in pycraft_classes:
                    classes.append('pycraft-supported-packet-class')
                    if versions[i] in pycraft_classes[packet_class]:
                        classes.append('pycraft-supported-packet')

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
        classes = ['packet-state-%s' % packet_class.state.lower(),
                   'packet-bound-%s' % packet_class.bound.lower()]
        if packet_class in pycraft_classes:
            classes.append('pycraft-supported-packet-class')
        print('          <tr><th class="%s">%s</th></tr>' % (
            ' '.join(classes), packet_class.name), end='')
    print('      </table>')

    print('   </div>')
    print('   </body>')
    print('</html>')


# Returns matrix with matrix[version][packet_class] = matrix_id
def version_packet_ids():
    used_patches = set()
    packet_classes = {}
    matrix = {}
    for v, url in sorted(version_urls.items(), key=lambda i: i[0].protocol):
        soup = get_soup(url)
        heading = soup.find(id='firstHeading').text.strip() 
        if heading == 'Pre-release protocol':
            vdiff = pre_versions(soup, v)
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
                        '[%s] [0x%02X] %r not in matrix[%r]' % (
                        v.name, packet.old_id, packet_class, from_v)
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

        state_bound_ids = {}
        for packet_class, matrix_id in matrix[v].items():
            key = (packet_class.state, packet_class.bound, matrix_id.id)
            assert key not in state_bound_ids, '[%s] Duplicate packet ID: ' \
                '%s is used by packets %r and %r.' % (v.name,
                '(%s, %s, 0x%02X)' % key, state_bound_ids[key], packet_class.name)
            state_bound_ids[key] = packet_class.name

        unused_patches = set(k for k in patch.keys() if k[0] == v and k not in used_patches)
        if unused_patches:
            raise AssertionError('Unused patches:\n'
            + '\n'.join('%s -> %s' % (p, patch[p]) for p in unused_patches))

    unused_patches = set(k for k in patch.keys() if k not in used_patches)
    if unused_patches:
        raise AssertionError('Unused patches:\n'
        + '\n'.join('%s -> %s' % (p, patch[p]) for p in unused_patches))

    return matrix


def pycraft_packet_category(name):
    return {
        'Client':      'clientbound',
        'Server':      'serverbound',
        'Handshaking': 'handshake',
    }.get(name, name).lower()

def pycraft_packet_name(name):
    name = {
        'Handshake':                              'HandShake',
        'Chat Message (serverbound)':             'Chat',
        'Player Position And Look (serverbound)': 'PositionAndLook',
        'Pong':                                   'PingResponse',
    }.get(name, name)
    return '%sPacket' % re.sub(r' +|\([^)]+\)$', '', name)

pycraft_ignore_errors = {
    "[17w06a] pyCraft: (0x10, 'ChatMessagePacket'), wiki: (0x0F, 'Chat Message (clientbound)')",
    "[17w06a] pyCraft: (0x10, 'ChatMessagePacket'), wiki: (0x10, 'Multi Block Change')",
    "[17w06a] pyCraft: (0x0A, 'PluginMessagePacket'), wiki: (0x09, 'Plugin Message (serverbound)')",
    "[17w06a] pyCraft: (0x0A, 'PluginMessagePacket'), wiki: (0x0A, 'Use Entity')",
    "[17w13a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w13a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w13b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w13b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w14a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w14a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w15a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w15a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w16a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w16a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w16b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w16b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w17a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w17a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w17b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w17b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w18a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w18a] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[17w18b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[17w18b] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[1.12-pre1] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[1.12-pre1] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[1.12-pre2] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[1.12-pre2] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[1.12-pre3] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[1.12-pre3] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[1.12-pre4] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3B, 'Entity Metadata')",
    "[1.12-pre4] pyCraft: (0x3B, 'EntityVelocityPacket'), wiki: (0x3D, 'Entity Velocity')",
    "[1.12-pre5] pyCraft: (0x25, 'MapPacket'), wiki: (0x25, 'Entity')",
    "[1.12-pre5] pyCraft: (0x25, 'MapPacket'), wiki: (0x24, 'Map')",
    "[1.12-pre6] pyCraft: (0x25, 'MapPacket'), wiki: (0x25, 'Entity')",
    "[1.12-pre6] pyCraft: (0x25, 'MapPacket'), wiki: (0x24, 'Map')",
}

# Returns classes where classes[packet_class] = {ver1, ver2, ...}
def pycraft_packet_classes(matrix):
    classes = {}
    all_packets = set()
    errors = []
    for ver, ver_matrix in matrix.items():
        if ver.protocol not in pycraft.SUPPORTED_PROTOCOL_VERSIONS: continue
        assert pycraft.SUPPORTED_MINECRAFT_VERSIONS[ver.name] == ver.protocol

        context = pycraft_connection.ConnectionContext()
        context.protocol_version = ver.protocol
        packets = {}
        for bound in 'Client', 'Server':
            for state in 'Handshaking', 'Login', 'Play', 'Status':
                module = getattr(pycraft_packets, pycraft_packet_category(bound))
                module = getattr(module, pycraft_packet_category(state))
                state_packets = module.get_packets(context)
                all_packets |= state_packets
                packets[bound, state] = state_packets

        for packet_class, matrix_id in ver_matrix.items():
            pycraft_name = pycraft_packet_name(packet_class.name)
            for packet in packets[packet_class.bound, packet_class.state]:
                expected = (matrix_id.id, pycraft_packet_name(packet_class.name))
                actual = (packet.get_id(context), packet.__name__)
                if all(x != y for (x, y) in zip(actual, expected)): continue
                if actual != expected:
                    error = '[%s] pyCraft: (0x%02X, %r), wiki: (0x%02X, %r)' % \
                            ((ver.name,) + actual + (matrix_id.id, packet_class.name))
                    if error not in pycraft_ignore_errors: errors.append(error)
                    continue
                all_packets.discard(packet)
                if packet_class not in classes: classes[packet_class] = set()
                classes[packet_class].add(ver)

    errors.extend('Packet not accounted for: %r' % p for p in all_packets)
    assert not errors, 'Errors found with pyCraft packets:\n' + '\n'.join(errors)

    return classes


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
def pre_versions(soup, vsn):
    vs = []
    para = soup.find(id='mw-content-text').find('p', recursive=False)
    for a in para.findAll('a'):
        m = PRE_VER_RE.match(a.text.strip())
        if m is None: continue
        vs.append(Vsn(
            name     = m.group('name'),
            protocol = int(m.group('protocol'))))
    if len(vs) == 2:
        return VersionDiff(*vs)
    else:
        raise AssertionError('[%s] Found %d versions, %r, where 2 are expected'
            ' in the first paragraph: %s' % (vsn.name, len(vs), vs, para))


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
                    assert changed
                    new_id = None
                else:
                    # Existing packet without changed packet ID.
                    new_id = old_id
                assert tds[cols[c_doc]].text.strip() == 'Current', \
                    '[%s] [%s] not %r or %r != %r' % (vsn.name,
                    tds[cols[c_name]].text.strip(), changed,
                    tds[cols[c_doc]].text.strip(), 'Current')

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
