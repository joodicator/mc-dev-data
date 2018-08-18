#!/usr/bin/env python3

import bs4
import bs4.element

from urllib.request import urlopen
from contextlib import closing
from collections import namedtuple
import traceback
import hashlib
import os.path
import inspect
import pickle
import os
import sys
import re
import math

import minecraft as pycraft
import minecraft.networking.connection as pycraft_connection
from minecraft.networking import packets as pycraft_packets


PACKET_STATE_VALUES = 'Handshaking', 'Login', 'Play', 'Status'
PACKET_BOUND_VALUES = 'Client', 'Server'

class MatrixID(namedtuple('MatrixID', ('id', 'changed', 'html', 'url'))):
    """Represents an individual cell in the matrix of packet IDs
       per protocol version per packet; used to generate a <td> element."""
    def __new__(cls, id, changed=None, html=None, url=None):
        return super(MatrixID, cls).__new__(cls, id, changed, html, url)
    def __repr__(r):
        return 'MatrixID(id=%s, changed=%r)' % (id_str(r.id), r.changed)

Vsn = namedtuple('Vsn', ('name', 'protocol'))
Vsn.__doc__ = "Represents a named Minecraft version with a protocol number."

VersionDiff = namedtuple('VersionDiff', ('old', 'new'))
VersionDiff.__doc__ = "Represents two Minecraft versions being compared."

class PrePacket(namedtuple('PrePacket', (
'name', 'old_id', 'new_id', 'changed', 'state', 'bound', 'html', 'url'))):
    """Represents a packet extracted from a pre-release protocol wiki page."""
    __slots__ = ()
    def __new__(cls, name, old_id, new_id, changed, state, bound, html=None, url=None):
        return super(PrePacket, cls).__new__(cls,
            name, old_id, new_id, changed, state, bound, html, url)
    def __eq__(self, other):
        if not isinstance(other, PrePacket): return False
        return super(PrePacket, self._reduce()).__eq__(other._reduce())
    def __hash__(self):
        return super(PrePacket, self._reduce()).__hash__()
    def _reduce(self):
        return self._replace(html=None, url=None)
    def __repr__(r):
        return 'PrePacket(name=%r, old_id=%s, new_id=%s, changed=%r, state=%r, bound=%r)' \
        % (r.name, id_str(r.old_id), id_str(r.new_id), r.changed, r.state, r.bound)

class RelPacket(namedtuple('RelPacket', ('name', 'id', 'state', 'bound', 'url'))):
    """Represents a packet extracted from a release protocol wiki page."""
    def __new__(cls, name, id, state, bound, url=None):
        return super(RelPacket, cls).__new__(cls, name, id, state, bound, url)
    def __eq__(self, other):
        if not isinstance(other, RelPacket): return False
        return super(RelPacket, self._reduce()).__eq__(other._reduce())
    def __hash__(self):
        return super(RelPacket, self._reduce()).__hash__()
    def _reduce(self):
        return self._replace(url=None)
    def __repr__(r):
        return 'RelPacket(name=%r, id=%s, state=%r, bound=%r)' \
               % (r.name, id_str(r.id), r.state, r.bound)

PacketClass = namedtuple('PacketClass', ('name', 'state', 'bound'))
PacketClass.__doc__ = "The label of a row in the packet ID matrix. "\
                      "Represents a class of version-packet-IDs which are "\
                      "conceptually associated with the same 'packet'." \

def id_str(id):
    """Returns the canonical string representation of a packet ID."""
    if isinstance(id, int):
        return '0x%02X' % id
    return str(id)


"""A dict mapping each Minecraft version to the URL of the corresponding
   pre-release or release wiki page. Pre-release pages are preferred, when
   available, as they contain more information about protocol changes."""
version_urls = {
    Vsn('1.13',        393): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14132',
    Vsn('1.13-pre10',  392): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14126',
    Vsn('1.13-pre9',   391): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14124',
    Vsn('1.13-pre8',   390): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14117',
    Vsn('1.13-pre7',   389): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14107',
    Vsn('1.13-pre6',   388): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14095',
    Vsn('1.13-pre5',   387): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14088',
    Vsn('1.13-pre4',   386): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14072',
    Vsn('1.13-pre3',   385): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14045',
    Vsn('1.13-pre2',   384): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14030',
    Vsn('1.13-pre1',   383): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13971',
    Vsn('18w22c',      382): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13965',
    Vsn('18w22b',      381): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13951',
    Vsn('18w22a',      380): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13947',
    Vsn('18w21b',      379): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13930',
    Vsn('18w21a',      378): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13926',
    Vsn('18w20c',      377): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13917',
    Vsn('18w20b',      376): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13913',
    Vsn('18w20a',      375): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13910',
    Vsn('18w19b',      374): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13905',
    Vsn('18w19a',      373): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13896',
    Vsn('18w16a',      372): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13891',
    Vsn('18w15a',      371): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13824',
    Vsn('18w14b',      370): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13744',
    Vsn('18w14a',      369): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13741',
    Vsn('18w11a',      368): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13724',
    Vsn('18w10d',      367): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13702',
    Vsn('18w10c',      366): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13699',
    Vsn('18w10b',      365): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13693',
    Vsn('18w10a',      364): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13692',
    Vsn('18w09a',      363): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13671',
    Vsn('18w08b',      362): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13666',
    Vsn('18w08a',      361): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13662',
    Vsn('18w07c',      360): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13658',
    Vsn('18w07b',      359): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13653',
    Vsn('18w07a',      358): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13648',
    Vsn('18w06a',      357): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13636',
    Vsn('18w05a',      356): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13628',
    Vsn('18w03b',      355): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13623',
    Vsn('18w02a',      353): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13582',
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
# These commented-out pages use a format that isn't supported by the current parser:
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


"""A dict mapping (version, data) tuples to a new data object containing
   corrections to mistakes or inconsistencies present in the old wiki pages."""
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
    (Vsn('17w13a', 318), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w13b', 319), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w14a', 320), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w15a', 321), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w16a', 322), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w16b', 323), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w17a', 324), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w17b', 325), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w18a', 326), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('17w18b', 327), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                         PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre1', 328), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                            PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre2', 329), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                            PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre3', 330), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
                            PrePacket('Map',      0x24, 0x25, False, 'Play', 'Client'),
    (Vsn('1.12-pre4', 331), PrePacket('Spawn Particle', 0x24, 0x25, False, 'Play', 'Client')):
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


"""A dict mapping variations on certain packet names to the canonical name.
   Instead of just a name, the key may also be a `(name, context)' pair,
   where `context' is one of PACKET_STATE_VALUES or PACKET_BOUND_VALUES."""
norm_packet_name_dict = {
    'Maps':                                 'Map',
    'Chunk data':                           'Chunk Data',
    'Entity effect':                        'Entity Effect',
    'Confirm Transation (clientbound)':     'Confirm Transaction (clientbound)',
    'Unlock Recipe':                        'Unlock Recipes',
    'Advancement Progress':                 'Select Advancement Tab',
    'Recipe Displayed':                     'Recipe Book Data',
    'Crafting Book Data':                   'Recipe Book Data',
    'Prepare Crafting Grid':                'Craft Recipe Request',
    'Sign Editor Open':                     'Open Sign Editor',
    'Player List Header/Footer':            'Player List Header And Footer',
    'Vehicle Move (Serverbound)':           'Vehicle Move (serverbound)',
    ('Vehicle Move?', 'Server'):            'Vehicle Move (serverbound)',
    'Particle':                             'Spawn Particle',
    'Plugin message (serverbound)':         'Plugin Message (serverbound)',
    'Login Plugin Message (clientbound)':   'Login Plugin Request',
    'Login Plugin Message (serverbound)':   'Login Plugin Response',
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
    """Return the normalised version of a given packet name, optionally in
       the context of a given game state (one of PACKET_STATE_VALUES) and
       direction (one of PACKET_BOUND_VALUES)."""
    n_names = set()
    for query in (name, (name, state), (name, bound)):
        if query in norm_packet_name_dict:
            n_names.add(norm_packet_name_dict[query])
    assert len(n_names) <= 1, \
           'Multiple normalisations for %r: %s.' % (name, n_names)
    return n_names.pop() if n_names else name


def matrix_html():
    """Print to stdout an HTML document displaying the matrix of packet IDs
       with each row giving a packet class and each column giving a version."""
    with get_page('__global__') as page:
        matrix = version_packet_ids(page)
        pycraft_classes = pycraft_packet_classes(page)

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
    print('    <div class="pkt-grid-container">')

    print('      <table class="pkt-grid top-header">')
    print('          <colgroup>' + ' <col>'*(len(versions)+1))
    print('          <tr> <th></th>', end='')
    for version in versions:
        psv = version.protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS
        print(' <th%(c)s><a href="%(u)s" title="%(n)s">%(n)s</a><br>%(v)s</th>'
            % {'u':version_urls[version], 'n':version.name, 'v':version.protocol,
               'c':' class="pycraft-version"' if psv else ''}, end='')
    print(' </tr>')
    print('      </table>')

    print('      <table class="pkt-grid contents">')
    print('          <colgroup>' + ' <col>'*(len(versions)+1))
    for packet_class in packet_classes:
        print('          <tr> <th></th>', end='')
        for i in range(len(versions)):
            prev_cell = matrix[versions[i+1]].get(packet_class) \
                        if i<len(versions)-1 else None
            if packet_class in matrix[versions[i]]:
                cell = matrix[versions[i]][packet_class]
                classes = ['pkt-present']

                if cell.changed is None:
                    classes.append('pkt-base')
                if not prev_cell:
                    if i < len(versions) - 1:
                        classes.append('pkt-added')
                else:
                    if cell.id != prev_cell.id:
                        classes.append('pkt-id-chg')
                    if cell.changed:
                        classes.append('pkt-fmt-chg')

                if versions[i].protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS:
                    classes.append('pycraft-version')
                if packet_class in pycraft_classes:
                    classes.append('pycraft-pkt-cls')
                    if versions[i] in pycraft_classes[packet_class]:
                        classes.append('pycraft-pkt')

                content = '0x%02X' % cell.id
                if cell.url: content = '<a href="%s">%s</a>' % (cell.url, content)
                print(' <td%s>%s</td>' % (' class="%s"' % ' '.join(classes)
                      if classes else '', content), end='')
            elif prev_cell:
                print(' <td class="pkt-removed"></td>')
            else:
                print(' <td></td>', end='')
        print('</tr>')
    print('      </table>')

    print('      <table class="pkt-grid left-header">')
    print('          <colgroup> <col> </colgroup>')
    for packet_class in packet_classes:
        classes = ['state-%s' % packet_class.state.lower(),
                   'bound-%s' % packet_class.bound.lower()]
        if packet_class in pycraft_classes:
            classes.append('pycraft-pkt-cls')
        print('          <tr><th class="%s">%s</th></tr>' % (
            ' '.join(classes), packet_class.name), end='')
    print('      </table>')

    print('      <table class="pkt-grid legend-min">')
    print('          <colgroup> <col></col> </colgroup>')
    print('          <tr><th>')
    print(              '<div class="l-spacer">&nbsp;<br>&nbsp;</div>')
    print('              <div class="l-text"></div>', end='')
    print(              '<div class="l-spacer">&nbsp;<br>&nbsp;</div>')
    print('          </th></tr>')
    print('      </table>')

    print('     <div class="legend">')
    print('         <div class="l-column">')
    print('             <div class="l-header">Packet categories:</div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-state l-state-handshaking"></div>')
    print('                 Handshake')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-state l-state-login"></div>')
    print('                 Login')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-state l-state-play"></div>')
    print('                 Play')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-state l-state-status"></div>')
    print('                 Status')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-bound l-bound-client"></div>')
    print('                 Clientbound')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-bound l-bound-server"></div>')
    print('                 Serverbound')
    print('             </div>')
    print('         </div>')
    print('         <div class="l-column">')
    print('             <div class="l-header">Protocol changes:</div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id">0x00</div>')
    print('                 No change')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pkt-id-chg">0x00</div>')
    print('                 ID changed')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pkt-fmt-chg">0x00</div>')
    print('                 Format <abbr title="(possibly)">changed</abbr>')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pkt-base">0x00</div>')
    print('                 Change unknown')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pkt-added">0x00</div>')
    print('                 Added')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pkt-removed"></div>')
    print('                 Removed')
    print('             </div>')
    print('         </div>')
    print('         <div class="l-column">')
    print('             <div class="l-header">')
    print('                 Implementation status in <a href="https://github.com/ammaraskar/pyCraft">pyCraft</a>:')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-version pycraft-version">111</div>')
    print('                 Version supported (for some packets)')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-cls pycraft-pkt-cls">Aa</div>')
    print('                 Packet class supported (for some versions)')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pycraft-pkt">0x00</div>')
    print('                 Packet supported')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pycraft-pkt-cls pycraft-version">0x00</div>')
    print('                 Packet not supported (version and class are)')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id pycraft-pkt-cls">0x00</div>')
    print('                 Packet not supported (class is)')
    print('             </div>')
    print('             <div class="l-item">')
    print('                 <div class="l-sample l-pkt-id">0x00</div>')
    print('                 Packet not supported')
    print('             </div>')
    print('         </div>')
    print('     </div>')

    print('   </div>')
    print('   </body>')
    print('</html>')


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


def get_url_hash(url):
    return hashlib.new('sha1', url.encode('utf8')).hexdigest()


func_cache_dir = os.path.join(os.path.dirname(__file__), 'func-cache')
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
            for key in list(self.page.keys()):
                if key != 'url' and not inspect.isfunction(globals().get(key)):
                    if key not in warned_unknown_func_cache_keys:
                        print('Warning: discarding unknown func-cache key: %r.'
                              % key, file=sys.stderr)
                        warned_unknown_func_cache_keys.add(key)
                    del page[key]
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


www_cache_dir = os.path.join(os.path.dirname(__file__), 'www-cache')
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


@from_page(get_soup, rdoc=
    "Recalculate first_heading(). Give if its code has changed.")
def first_heading(soup):
    """The text of the element with id "firstHeading" on this page. This is
       used to identify the type (e.g. release or pre-release) of page."""
    return soup.find(id='firstHeading').text.strip() 


PRE_VER_RE = re.compile(r'(?P<name>\d[^,]*), protocol (?P<protocol>\d+)')
@from_page(get_soup, rdoc=
    "Recalculate pre_versions(). Give if its code has changed.")
def pre_versions(soup, vsn):
    """Return a VersionDiff instance containing the old and new versions
       being compared in this pre-release protocol wiki page."""
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


"""A dict mapping `(version, url_fragment)' pairs to corrected URL fragments,
   to patch errors occurring in section hyperlinks. If `version' is None, the
   corresponding patch applies to all versions. If the value is None, the link
   is declared to have no corresponding section on the page."""
patch_links = {
    (Vsn('15w51b', 94),  '#Vehicle_Move.3F'):           None,
    (Vsn('15w51b', 94),  '#Steer_Boat'):                None,
    (Vsn('16w02a', 95),  '#Steer_Boat'):                None,
    (Vsn('1.9.4', 110),  '#Chunk_data'):                '#Chunk_Data',
    (Vsn('17w13a', 318), '#Advancements'):              None,
    (Vsn('17w13a', 318), '#Unlock_Recipe'):             None,
    (Vsn('17w13a', 318), '#Unknown'):                   None,
    (Vsn('17w13a', 318), '#Recipe_Displayed'):          None,
    (Vsn('17w13a', 318), '#Use_Item'):                  None,
    (Vsn('17w13b', 319), '#Recipe_Displayed'):          '#Recipe_displayed',
    (None, '#Plugin_message_.28serverbound.29'):        '#Plugin_Message_.28serverbound.29',
    (Vsn('1.13-pre3', 385), '#Login_Plugin_Message_.28clientbound.29'):
                                                        '#Login_Plugin_Message_.28clientbound.29',
    (Vsn('1.13-pre3', 385), '#Login_Plugin_Message_.28serverbound.29'):
                                                        '#Login_Plugin_Message_.28serverbound.29',
    (Vsn('1.13-pre4', 386), '#Login_Plugin_Message_.28clientbound.29'):
                                                        '#Login_Plugin_Message_.28clientbound.29',
    (Vsn('1.13-pre4', 386), '#Login_Plugin_Message_.28serverbound.29'):
                                                        '#Login_Plugin_Message_.28serverbound.29',
    (None, '#Login_Plugin_Message_.28clientbound.29'):  '#Login_Plugin_Request',
    (None, '#Login_Plugin_Message_.28serverbound.29'):  '#Login_Plugin_Response',
}

@from_page(get_soup, rdoc=
    'Recalculate pre_packets(). Give if its code has changed.')
def pre_packets(soup, vsn):
    """Returns an iterator over the `PrePacket' instance for each packet documented
       on this pre-release protocol wiki page. `vsn' should be the canonical `Vsn'
       instance associated with this page."""
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
            if len(ths) == 1 and abs(int(ths[0].get('colspan', '1')) - ncols) <= 1:
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

            if changed and new_id is not None:
                a = tds[cols[c_doc]+1].find('a')
                assert a is not None, '[%s] [%s] No <a> found in %s' % (
                    vsn.name, tds[cols[c_name]].text.strip(), tds[cols[c_doc]+1])
                parts = tds[cols[c_doc]+1].find('a').get('href').split('#', 1)
                assert len(parts) == 2 and parts[0] == '/Pre-release_protocol', \
                    '[%s] [%s] %s' % (vsn.name, tds[cols[c_name]].text.strip(), parts)
                frag = '#' + parts[1]
                frag = patch_links.get((vsn, frag), patch_links.get((None, frag), frag))
                if frag is not None:
                    head = soup.find(id=frag[1:])
                    assert head is not None, \
                           '[%s] Cannot find "%s".' % (vsn.name, frag)
                    html = []
                    for el in head.find_parent('h4').next_siblings:
                        if el.name in ('h4', 'h3', 'h2', 'h1'): break
                        if isinstance(el, bs4.element.Tag):
                            html.extend(el.stripped_strings)
                        elif type(el) in (bs4.element.NavigableString,
                                          bs4.element.PreformattedString):
                            html.append(str(el).strip())
                        else:
                            assert isinstance(el, bs4.element.PageElement), repr(el)
                    html = ''.join(html).replace(id_str(new_id), '{packet-id}')
                    if name == 'Handshake':
                        html = re.sub(r'See\s*protocol version numbers\s*\(currently.*?\)',
                                      '{proto-ver}', html)
                    #if name == 'Login Plugin Response':
                    #    __import__('pdb').set_trace()
                    html = hashlib.sha1(html.encode('utf8')).hexdigest()
                    url = version_urls[vsn] + frag
            else:
                html, url = None, None

            yield PrePacket(
                name=name, old_id=old_id, new_id=new_id, changed=changed,
                state=state, bound=bound, html=html, url=url)


@from_page(get_soup, rdoc=
    'Recalculate rel_packets(). Give if its code has changed.')
def rel_packets(soup, vsn):
    """Return an iterator over the `RelPacket' instance for each packet
       documented on this release protocol wiki page. `vsn' should be the
       canonical `Vsn' instance associated with this page."""
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
        head = table.findPreviousSibling('h4')
        name = norm_packet_name(head.text.strip(), state, bound)
        url = '%s#%s' % (version_urls[vsn], head.find('span')['id'])
        yield RelPacket(name=name, id=id, state=state, bound=bound, url=url)


REL_VER_RE = re.compile(r'\(currently (?P<protocol>\d+)'
                        r'( in Minecraft (?P<name>\d[^)]*))?\)')
@from_page(get_soup, rdoc=
    'Recalculate rel_version(). Give if its code has changed.')
def rel_version(soup):
    """Return a `Vsn' instance giving the Minecraft and protocol version
       specified on this release protocol wiki page."""
    td = soup.find('td', string=re.compile('^\s*Protocol Version\s*$'))
    td = td.findNextSibling('td')
    assert td.text.strip() == 'VarInt'
    td = td.findNextSibling('td')
    m = REL_VER_RE.search(td.text)
    protocol = int(m.group('protocol')) if m.group('protocol') else None
    return Vsn(name=m.group('name'), protocol=protocol)


# Returns matrix with matrix[version][packet_class] = matrix_id
@from_page(dep=(first_heading,pre_versions,pre_packets,rel_version,rel_packets),
    rdoc='Recalculate the packet ID matrix. Give if the version_urls dict\n'
         'or the code of version_packet_ids() have been changed.', doc_order=-2)
def version_packet_ids():
    """Return a dict mapping `Vsn' instances to dicts mapping `PacketClass'
       instances to `MatrixID' instances, giving the matrix of packet IDs as
       they vary across packets and across protocol versions."""
    used_patches = set()
    packet_classes = {}
    matrix = {}
    prev_v = None
    for v, url in sorted(version_urls.items(), key=lambda i: i[0].protocol):
        with get_page(url) as page:
            heading = first_heading(page)
            if heading == 'Pre-release protocol':
                vdiff = pre_versions(page, v)
                if (v, vdiff) in patch:
                    used_patches.add((v, vdiff))
                    vdiff = patch[v, vdiff]
                from_v, to_v = vdiff
                assert v == to_v, '%r != %r' % (v, to_v)
                matrix[v] = {}
                seen_names = {}
                for packet in pre_packets(page, v):
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
                        changed = packet.changed
                        if changed and packet.html and prev_v:
                            prev = matrix[prev_v].get(packet_class)
                            if prev and prev.html == packet.html: changed = False
                        matrix[v][packet_class] = MatrixID(
                            id=packet.new_id, changed=changed,
                            html=packet.html, url=packet.url if changed else None)
                for packet_class, id in matrix[from_v].items():
                    if packet_class.name in seen_names: continue
                    matrix[v][packet_class] = id._replace(
                        changed=False, html=None, url=None)
            elif heading == 'Protocol':
                rel_v = rel_version(page)
                if rel_v.name is None:
                    rel_v = Vsn(v.name, rel_v.protocol)
                assert v == rel_v, '%r != %r' % (v, rel_v)
                matrix[v] = {}
                seen_names = {}
                for packet in rel_packets(page, v):
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

                    matrix[v][packet_class] = MatrixID(id=packet.id, url=packet.url)
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

        prev_v = v

    unused_patches = set(k for k in patch.keys() if k not in used_patches)
    if unused_patches:
        raise AssertionError('Unused patches:\n'
        + '\n'.join('%s -> %s' % (p, patch[p]) for p in unused_patches))

    return matrix


def pycraft_packet_category(name):
    """Given a packet category from PACKET_STATE_VALUES or PACKET_BOUND_VALUES,
       return the corresponding identifier in pyCraft's naming conventions."""
    return {
        'Client':      'clientbound',
        'Server':      'serverbound',
        'Handshaking': 'handshake',
    }.get(name, name).lower()


def pycraft_packet_name(name):
    """Given the canonical name of a packet according to this script, return
       the name of the corresponding packet class in pyCraft."""
    name = {
        'Handshake':                              'HandShake',
        'Chat Message (serverbound)':             'Chat',
        'Player Position And Look (serverbound)': 'PositionAndLook',
        'Pong':                                   'PingResponse',
        'Login Plugin Request':                   'PluginRequest',
        'Login Plugin Response':                  'PluginResponse',
    }.get(name, name)
    return '%sPacket' % re.sub(r' +|\([^)]+\)$', '', name)


"""A set of error strings regarding discrepancies between pyCraft and the wiki
   data which are declared to not be of critical importance, and will be
   ignored instead of causing the process to fail."""
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


@from_page(version_packet_ids, rdoc=
    'Recalculate pyCraft data. Give if the local pyCraft version\n'
    'or the code of pycraft_packet_classes() have changed.', doc_order=-1)
def pycraft_packet_classes(matrix):
    """Returns a dict mapping `PacketClass' instances to sets of `Ver` instances
       giving the protocol versions for which each packet class is supported by
       the locally installed version of the pyCraft library."""
    classes = {}
    all_packets = set()
    errors = []
    for ver, ver_matrix in matrix.items():
        if ver.protocol not in pycraft.SUPPORTED_PROTOCOL_VERSIONS: continue
        assert pycraft.SUPPORTED_MINECRAFT_VERSIONS[ver.name] == ver.protocol

        context = pycraft_connection.ConnectionContext()
        context.protocol_version = ver.protocol
        packets = {}
        for bound in PACKET_BOUND_VALUES:
            for state in PACKET_STATE_VALUES:
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


refresh_names = set()
refresh_min_proto, refresh_min_proto_arg = -math.inf, '--r-min-proto='
refresh_max_proto, refresh_max_proto_arg =  math.inf, '--r-max-proto='
for arg in sys.argv[1:]:
    if arg.startswith(refresh_min_proto_arg):
        refresh_min_proto = int(arg[len(refresh_min_proto_arg):])
    elif arg.startswith(refresh_max_proto_arg):
        refresh_max_proto = int(arg[len(refresh_max_proto_arg):])
    elif arg.startswith('-r'):
        refresh_names.add(arg[2:])

if __name__ == '__main__':
    args = [
        (val.doc_order, '-r%s' % key, val.rdoc)
        for (key, val) in globals().items() if inspect.isfunction(val)
        and getattr(val, 'refreshable', False)
    ] + [
        (1, refresh_min_proto_arg + 'VER',
         'Recalculate only for protocol versions >= this value.'),
        (2, refresh_max_proto_arg + 'VER',
         'Recalculate only for protocol versions <= this value.'),
    ]
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        print('Usage: main.py [-h|--help] [RFLAGS...]\n\n'
              'This script generates and prints to stdout the contents of index.htm.\n'
              'To save time, much intermediate data is saved under the "func-cache" directory.\n'
              'When the script or source data are changed, RFLAGS may be given to tell which\n'
              'data need to be recalculated. Alternatively, the entire func-cache may be\n'
              'deleted, to recalculate everything.\n\n'
              'The possible RFLAGS are:', file=sys.stderr)
        for _, arg, doc in sorted(args):
            print(' '*3 + '\33[1m%s\33[0m' % arg, file=sys.stderr)
            for line in doc.split('\n'): print(' '*6 + line)
        sys.exit(0)

    for arg in sys.argv[1:]:
        if all(not arg.startswith(a) for a in unary_args) and arg not in nullary_args:
            print('Unrecognised argument: %s' % arg, file=sys.stderr)
            sys.exit(2)

    matrix_html()

    for vsn, url in version_urls.items():
        unused_func_cache_files.discard(get_url_hash(url))
        unused_www_cache_files.discard(get_url_hash(url))
    if unused_www_cache_files:
        print('Unused www-cache files:', file=sys.stderr)
        print('  ' + ' '.join(sorted(unused_www_cache_files)), file=sys.stderr)
    if unused_func_cache_files:
        print('Unused func-cache files:', file=sys.stderr)
        print('  ' + ' '.join(sorted(unused_func_cache_files)), file=sys.stderr)
