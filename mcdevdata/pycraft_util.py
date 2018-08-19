import re

import minecraft as pycraft
import minecraft.networking.connection as pycraft_connection
from minecraft.networking import packets as pycraft_packets

from .util import PACKET_STATE_VALUES, PACKET_BOUND_VALUES
from .cache import from_page
from .matrix import version_packet_ids

__all__ = ('pycraft_packet_classes',)


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
