from collections import namedtuple

from .util import id_str

__all__ = ('MatrixID', 'PRE', 'Vsn', 'VersionDiff', 'PrePacket', 'RelPacket',
           'PacketClass')

class MatrixID(namedtuple('MatrixID', (
'id', 'base_ver', 'changed', 'html', 'url'))):
    """Represents an individual cell in the matrix of packet IDs per protocol
       version per packet; used to generate a <td> element.
       - 'id'       is an integer giving the packet ID.
       - 'base_ver' is the Vsn relative to which difference info is available.
       - 'changed'  is True if the packet format has changed since base_ver,
                      or otherwise False.
       - 'html'     is a hash of the HTML describing the packet's structure,
                      intended to be compared with other such hashes, or None.
       - 'url'      is a URL linking to a section of the wiki giving the
                      structure of the packet, or None.
    """
    def __new__(cls, id, base_ver, changed=None, html=None, url=None):
        return super(MatrixID, cls).__new__(
            cls, id, base_ver, changed, html, url)
    def __repr__(r):
        return 'MatrixID(id=%s, base_ver=%r, changed=%r)' % (
            id_str(r.id), r.base_ver, r.changed)

# This bit flag occurs in the protocol version numbers of pre-release versions after 1.16.3.
PRE = 1 << 30

class Vsn(namedtuple('Vsn', ('name', 'protocol'))):
    """Represents a named Minecraft version with a protocol number."""
    def __repr__(r):
        return 'Vsn(%r, %s)' % (r.name, self.protocol_repr(r.protocol))

    @staticmethod
    def protocol_repr(protocol):
        if protocol & PRE:
            return 'PRE|%d' % (protocol & ~PRE)
        else:
            return repr(protocol)

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
    def patch(self, other):
        return other and self._replace(
            name=other.name, old_id=other.old_id, new_id=other.new_id,
            changed=other.changed, state=other.state, bound=other.bound)

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
    def patch(self, other):
        return other and self._replace(
            name=other.name, id=other.id, state=other.state, bound=other.bound)

PacketClass = namedtuple('PacketClass', ('name', 'state', 'bound'))
PacketClass.__doc__ = "The label of a row in the packet ID matrix. "\
                      "Represents a class of version-packet-IDs which are "\
                      "conceptually associated with the same 'packet'." \

