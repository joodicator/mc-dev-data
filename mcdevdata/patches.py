from .types import Vsn, VersionDiff, RelPacket, PrePacket

__all__ = ('patch', 'norm_packet_name')


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
