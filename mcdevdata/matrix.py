from .types import Vsn, MatrixID, PacketClass
from .patches import patch
from .cache import from_page, get_page
from .sources import version_urls
from .parsers import pre_versions, pre_packets, rel_version, rel_packets
from .parsers import first_heading

__all__ = ('version_packet_ids',)


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
                        packet = packet.patch(patch[v, packet])
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
                        if packet_class not in matrix[from_v]:
                            msg = '[%s] [0x%02X] %r not in matrix[%r]' % (
                                  v.name, packet.old_id, packet_class, from_v)
                            for from_pcls, from_mid in matrix[from_v].items():
                                if (from_pcls.state, from_pcls.bound, from_mid.id) \
                                == (packet_class.state, packet_class.bound, packet.old_id):
                                    msg += '\n(however, matrix[%r][%r].id == 0x%02X)' % (
                                           from_v, from_pcls, packet.old_id)
                                    break
                            raise AssertionError(msg)
                        assert packet.old_id == matrix[from_v][packet_class].id, \
                            '[%s] 0x%02x != matrix[%r][%r].id == 0x%02x' % (
                            v.name, packet.old_id, from_v, packet_class,
                            matrix[from_v][packet_class].id)
                    if packet.url is not None:
                        url = packet.url
                    elif not packet.changed and from_v and packet_class in matrix[from_v]:
                        url = matrix[from_v][packet_class].url
                    else:
                        url = None
                    if packet.new_id is not None:
                        matrix[v][packet_class] = MatrixID(
                            id=packet.new_id, base_ver=from_v,
                            changed=packet.changed, html=packet.html, url=url)
                for packet_class, id in matrix[from_v].items():
                    if packet_class.name in seen_names: continue
                    matrix[v][packet_class] = id._replace(
                        base_ver=from_v, changed=False)
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
                        packet = packet.patch(patch[v, packet])
                    if packet is None: continue
                    assert packet.name not in seen_names, \
                        '[%s] Duplicate packet name:\n%s\n%s.' \
                        % (v.name, seen_names[packet.name], packet)
                    seen_names[packet.name] = packet

                    packet_class = PacketClass(
                        name=packet.name, state=packet.state, bound=packet.bound)
                    if packet.name not in packet_classes:
                        packet_classes[packet.name] = packet_class
                    assert packet_classes[packet.name] == packet_class, \
                        '[%s] %r != %r' % (v.name,
                        packet_classes[packet.name], packet_class)

                    matrix[v][packet_class] = MatrixID(
                        id=packet.id, base_ver=v, changed=False, url=packet.url)
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
