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
                all_packets.discard(packet)
                if actual != expected:
                    error = '[%s] pyCraft: (0x%02X, %r), wiki: (0x%02X, %r)' % \
                            ((ver.name,) + actual + (matrix_id.id, packet_class.name))
                    if error not in pycraft_ignore_errors: errors.append(error)
                    continue
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
    "[17w13a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w13a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w13b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w13b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w14a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w14a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w15a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w15a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w16a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w16a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w16b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w16b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w17a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w17a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w17b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w17b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w18a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w18a] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w18b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[17w18b] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[1.12-pre1] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[1.12-pre1] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[1.12-pre2] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[1.12-pre2] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[1.12-pre3] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[1.12-pre3] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[1.12-pre4] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[1.12-pre4] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[1.12-pre5] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[1.12-pre5] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[1.12-pre6] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[1.12-pre6] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[1.12-pre7] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x47, 'Title')",
    "[1.12-pre7] pyCraft: (0x47, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Player List Header And Footer')",
    "[17w31a] pyCraft: (0x49, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Sound Effect')",
    "[17w31a] pyCraft: (0x49, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Player List Header And Footer')",
    "[1.12.1-pre1] pyCraft: (0x49, 'PlayerListHeaderAndFooterPacket'), wiki: (0x49, 'Sound Effect')",
    "[1.12.1-pre1] pyCraft: (0x49, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Player List Header And Footer')",
    "[17w45a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Sound Effect')",
    "[17w45a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4B, 'Player List Header And Footer')",
    "[17w45b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Sound Effect')",
    "[17w45b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4B, 'Player List Header And Footer')",
    "[17w46a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Stop Sound')",
    "[17w46a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4C, 'Player List Header And Footer')",
    "[17w47a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Stop Sound')",
    "[17w47a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4C, 'Player List Header And Footer')",
    "[17w47b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Stop Sound')",
    "[17w47b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4C, 'Player List Header And Footer')",
    "[17w48a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Stop Sound')",
    "[17w48a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4C, 'Player List Header And Footer')",
    "[17w49a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Stop Sound')",
    "[17w49a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4C, 'Player List Header And Footer')",
    "[17w49b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Stop Sound')",
    "[17w49b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4C, 'Player List Header And Footer')",
    "[17w50a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Stop Sound')",
    "[17w50a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4C, 'Player List Header And Footer')",
    "[18w01a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w01a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w02a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w02a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w03b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w03b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w05a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w05a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w06a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w06a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w07a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w07a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w07b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w07b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w07c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w07c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w08a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w08a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w08b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w08b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w09a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w09a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w10a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w10a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w10b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w10b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w10c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w10c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w10d] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w10d] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w11a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w11a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w14a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w14a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w14b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w14b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w15a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w15a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w16a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w16a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w19a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w19a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w19b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w19b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w20a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w20a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w20b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w20b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w20c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w20c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w21a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w21a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w21b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w21b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w22a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w22a] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w22b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w22b] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[18w22c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[18w22c] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[1.13-pre1] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[1.13-pre1] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[1.13-pre2] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[1.13-pre2] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[1.13-pre3] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[1.13-pre3] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[1.13-pre4] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[1.13-pre4] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[1.13-pre5] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[1.13-pre5] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[1.13-pre6] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Title')",
    "[1.13-pre6] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4D, 'Player List Header And Footer')",
    "[1.13-pre7] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Time Update')",
    "[1.13-pre7] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4E, 'Player List Header And Footer')",
    "[1.13-pre8] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Time Update')",
    "[1.13-pre8] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4E, 'Player List Header And Footer')",
    "[1.13-pre9] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Time Update')",
    "[1.13-pre9] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4E, 'Player List Header And Footer')",
    "[1.13-pre10] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4A, 'Time Update')",
    "[1.13-pre10] pyCraft: (0x4A, 'PlayerListHeaderAndFooterPacket'), wiki: (0x4E, 'Player List Header And Footer')",
}
