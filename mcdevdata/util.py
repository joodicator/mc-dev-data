import hashlib

__all__ = ('id_str', 'get_url_hash', 'get_page', 'from_page',
           'PACKET_STATE_VALUES', 'PACKET_BOUND_VALUES')


PACKET_STATE_VALUES = 'Handshaking', 'Login', 'Play', 'Status'
PACKET_BOUND_VALUES = 'Client', 'Server'


def id_str(id):
    """Returns the canonical string representation of a packet ID."""
    if isinstance(id, int):
        return '0x%02X' % id
    return str(id)


def get_url_hash(url):
    return hashlib.new('sha1', url.encode('utf8')).hexdigest()
