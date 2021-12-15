from itertools import count, zip_longest
from copy import copy
import html

import numpy as np
import minecraft as pycraft

from .cache import get_page
from .matrix import version_packet_ids
from .sources import version_urls, versions, PRE
from .pycraft_util import pycraft_packet_classes
from .types import Vsn

__all__ = ('matrix_html',)


def matrix_html(show_versions=None, pycraft_only=False, text=False, debug=False):
    """Print to stdout an HTML document displaying the matrix of packet IDs
       with each row giving a packet class and each column giving a version."""
    with get_page('__global__') as page:
        matrix = version_packet_ids(page)
        pycraft_classes = pycraft_packet_classes(page, show_versions)

    show_versions = versions if show_versions is None else show_versions

    packet_classes = sorted({
        p for ids in matrix.values() for p in ids.keys()
        if any(p in matrix[v] for v in show_versions)
        and (not pycraft_only or p in pycraft_classes)},
        key=lambda p: (
            ('Handshaking', 'Status', 'Login', 'Play').index(p.state),
            ('Server', 'Client').index(p.bound),
            tuple(getattr(matrix[v].get(p), 'id', 0xFFF) for v in show_versions)
        ))

    if text:
        if len(show_versions) != 1: raise ValueError('In plain text mode,'
            ' exactly one Minecraft version must be selected; currently, %d are'
            ' selected.' % len(show_versions))
        column = matrix[show_versions[0]]
        state_bound = None
        for packet_class in packet_classes:
            if state_bound != (packet_class.state, packet_class.bound):
                if state_bound is not None: print('')
                state_bound = packet_class.state, packet_class.bound
                print('// %s %sBOUND' % tuple(map(str.upper, state_bound)))
            print('0x%02X %s' % (column[packet_class].id, packet_class.name))
        return

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
    print('          <colgroup>' + ' <col>'*(len(show_versions)+1))
    print('          <tr> <th></th>', end='')
    any_sup = False
    for version in show_versions:
        psv = version.protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS
        pv_repr = Vsn.protocol_repr(version.protocol, html=False)
        pv_html = Vsn.protocol_repr(version.protocol, html=True)
        any_sup |= '<sup>' in pv_html
        print(' <th%(c)s><a href="%(u)s" title="%(n)s">%(n)s</a><br>'
                        '<span%(w)s>%(v)s</span></th>'
            % {'u': version_urls[version],
               'n': version.name,
               'v': pv_html,
               'w': (' title="%s = %d"' % (pv_repr, version.protocol))
                    if pv_repr != str(version.protocol) else '',
               'c': ' class="pycraft-version"' if psv else ''}, end='')
    print(' </tr>')
    print('      </table>')

    print('      <table class="pkt-grid contents">')
    print('          <colgroup>' + ' <col>'*(len(show_versions)+1))

    # Bit flags for knowledge representation:
    UNK      = 0x00       # unknown equality
    MEQ, MNE = 0x01, 0x10 # maybe equal, maybe not equal
    PEQ, PNE = 0x03, 0x30 # probably equal, probably not equal
    CEQ, CNE = 0x07, 0x70 # certainly equal, certainly not equal

    EQ_NAME = {CEQ: 'CEQ', PEQ: 'PEQ', MEQ: 'MEQ',
               CNE: 'CNE', PNE: 'PNE', MNE: 'MNE', UNK: 'UNK'}
    def eq_name(eq):
        return EQ_NAME[eq & CEQ] if eq & CNE == UNK else \
               EQ_NAME[eq & CNE] if eq & CEQ == UNK else \
               '%s|%s' % (EQ_NAME[eq & CNE], EQ_NAME[eq & CEQ])

    # Knowledge of whether each pair of packet versions have equal formats:
    def get_vsn_diff(vsn1, cell1, vsn2, cell2):
        if vsn1.protocol == vsn2.protocol:
            return CEQ, 'same protocol'
        elif cell1.base_ver == vsn2 and not cell1.changed:
            return CEQ, 'left based on right and not "changed"'
        elif cell2.base_ver == vsn1 and not cell2.changed:
            return CEQ, 'right based on left and not "changed"'
        elif None != cell1.html == cell2.html:
            return CEQ, 'same HTML'
        elif cell1.base_ver == vsn2 and cell1.changed:
            return PNE, 'left based on right and "changed"'
        elif cell2.base_ver == vsn1 and cell2.changed:
            return PNE, 'right based on left and "changed"'
        elif None != cell1.html != cell2.html != None:
            return MNE, 'different HTML'
        else:
            return UNK, 'default case'

    shape = (len(versions), len(versions), len(packet_classes))
    vsn_diff = np.empty(shape, np.ubyte)
    for p, packet_class in enumerate(packet_classes):
        for i, vsn1 in enumerate(versions):
            cell1 = matrix[vsn1].get(packet_class)
            if cell1 is None: continue
            vsn_diff[i, i, p] = CEQ
            for j, vsn2 in zip(count(i+1), versions[i+1:]):
                cell2 = matrix[vsn2].get(packet_class)
                if cell2 is None: continue
                vsn_diff[i, j, p] = vsn_diff[j, i, p] = \
                    get_vsn_diff(vsn1, cell1, vsn2, cell2)[0]

    vsn_diff_init = copy(vsn_diff)
    
    # Apply the Floyd-Warshall algorithm to compute a generalised type of
    # "transitive closure" of the equality matrix, with respect to the
    # following two knowledge-combining operations:
    # 
    # Let "u E v" mean that we possess knowledge represented by E of
    # whether packet versions u and v have the same format; then for all
    # versions u, v, w and bitfields E, F <= 0xFF:
    #  1. if "u E v" and "v F w" then "u t(E,F) v" [transitive conjunction],
    #  2. if "u E v" and "u F v" then "u r(E,F) v" [reflexive conjunction].
    #
    # t and r are determined by, for all bitfields E, F, G <= 0xFF:
    #  3. r(E, F) == E | F,
    #  5. t has the particular values given in the following table:
    #     +-----+-----------------------------+
    #     |  t  | UNK MEQ PEQ CEQ MNE PNE CNE |
    #     +-----+-----------------------------+
    #     | UNK | UNK UNK UNK UNK UNK UNK UNK | [u UNK v UNK w ==> u UNK w]
    #     | MEQ | UNK MEQ MEQ MEQ MNE MNE MNE | [u MEQ v _xx w ==> u Mxx w]
    #     | PEQ | UNK MEQ PEQ PEQ MNE PNE PNE | [u PEQ v Cxx w ==> u Pxx w]
    #     | CEQ | UNK MEQ PEQ CEQ MNE PNE CNE | [u CEQ v xxx w ==> u xxx w]
    #     | MNE | UNK MNE MNE MNE UNK UNK UNK |
    #     | PNE | UNK MNE PNE PNE UNK UNK UNK | [u _NE v _NE w ==> u UNK w]
    #     | CNE | UNK MNE PNE CNE UNK UNK UNK |
    #     +-----+-----------------------------+
    #  4. (a) t(E, F) == t(F, E)                [t is commutative],
    #     (b) t(E, t(F,G)) == t(t(E,F), G)      [t is associative], and
    #     (c) t(E, r(F,G)) == r(t(E,F), t(E,G)) [t distributes over r].
    #
    # It can be shown that the unique operation t determined by the above is:
    #  5. t(E, F) == E & F & CEQ | E<<4 & F | F<<4 & E.
    #
    # t(E, F) and r(E, F) take the roles of "E and F" and "E or F" in the
    # usual Floyd-Warshall transitive closure algorithm, or of "E + F" and
    # "min(E, F)" in the usual Floyd-Warshall shortest path algorithm;
    # the associativity of t and r, commutativity of r, and distributivity
    # of t over r ensure that the algorithm will work equivalently.
    for k in range(len(versions)):
        diff_ik, diff_kj = vsn_diff[:, k:k+1, :], vsn_diff[k:k+1, :, :]
        vsn_diff |= CEQ & diff_ik & diff_kj
        vsn_diff |= diff_ik<<4 & diff_kj
        vsn_diff |= diff_kj<<4 & diff_ik

    # For debugging, find the most confident and then shortest path between
    # versions i and j asserting equality (when mask=CEQ) or inequality
    # (when mask=CNE).
    def best_path(i, j, p, mask):
        memo = {}
        def best_path_ext(i, acc, depth=1):
            if (i, acc) in memo: return memo[i, acc]
            best_diff, best_path = \
                (acc, (j,)) if i == j else (UNK, None)
            memo[i, acc] = best_diff, best_path
            for k in range(len(versions)):
                diff = vsn_diff_init[i, k, p]
                diff = acc & diff & CEQ | acc<<4 & diff | diff<<4 & acc
                if diff == UNK: continue
                diff, path = best_path_ext(k, diff, depth+1)
                if path is None: continue
                if best_path is None or (diff & mask, -(len(path) + 1)) \
                > (best_diff & mask, -len(best_path)):
                    best_diff, best_path = diff, (i,) + path
            memo[i, acc] = best_diff, best_path
            return best_diff, best_path
        return best_path_ext(i, CEQ)[1]

    def best_path_str(i, j, p, mask):
        path = best_path(i, j, p, mask)
        lines = ['    %r' % (versions[path[0]],)]
        for u, v in zip(path, path[1:]):
            u, v = versions[u], versions[v]
            d, c = get_vsn_diff(u, matrix[u][packet_class],
                                v, matrix[v][packet_class])
            lines.append(
                '%s %r # %s' % (eq_name(d), v, c))
        return '\n'.join(lines)

    for p, packet_class in enumerate(packet_classes):
        print('          <tr> <th></th>', end='')

        for ver, prev_ver in zip_longest(show_versions, show_versions[1:]):
            cell = matrix[ver].get(packet_class)
            prev_cell = prev_ver and matrix[prev_ver].get(packet_class)
            if cell is not None:
                classes = ['pkt-present']
                comment = None
                if prev_cell is not None:
                    if cell.id != prev_cell.id:
                        classes.append('pkt-id-chg')

                    i, j = versions.index(ver), versions.index(prev_ver)
                    diff = vsn_diff[i, j, p]
                    if (diff & CNE)>>4 & ~(diff & CEQ):
                        classes.append('pkt-fmt-chg')
                        if debug:
                            cell_html = cell.html if cell.html else \
                                matrix[cell.base_ver][packet_class].html \
                                if packet_class in matrix[cell.base_ver] \
                                and not cell.changed else None
                            prev_cell_html = prev_cell.html if prev_cell.html else \
                                matrix[prev_cell.base_ver][packet_class].html \
                                if packet_class in matrix[prev_cell.base_ver] \
                                and not prev_cell.changed else None
                            if None != cell_html != prev_cell_html != None:
                                comment = '%r\n!=\n%r' % (
                                    cell_html, prev_cell_html)
                            elif vsn_diff_init[i, j, p] & CNE == diff & CNE:
                                comment = '%r %s %r' % (
                                    ver, eq_name(diff & CNE), prev_ver)
                            else:
                                comment = best_path_str(i, j, p, CNE)
                    elif diff == UNK:
                        classes.append('pkt-chg-unk')
                    elif (diff & CNE)>>4 == diff & CEQ:
                        msg_lines = ['%r and %r of %r are both %s and %s:'
                            % (ver, prev_ver, packet_class,
                            eq_name(diff & CEQ), eq_name(diff & CNE))]
                        for mask in CEQ, CNE:
                            msg_lines.extend(('', best_path_str(i, j, p, mask)))
                        raise AssertionError('\n'.join(msg_lines))
                elif ver != show_versions[-1]:
                    classes.append('pkt-added')

                if ver.protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS:
                    classes.append('pycraft-version')
                if packet_class in pycraft_classes:
                    classes.append('pycraft-pkt-cls')
                    if ver in pycraft_classes[packet_class].versions:
                        classes.append('pycraft-pkt')

                content = '0x%02X' % cell.id
                if cell.url: content = '<a href="%s">%s</a>' % (cell.url, content)
                print(' <td%s%s>%s</td>' % (
                    ' class="%s"' % ' '.join(classes)
                        if classes else '',
                    ' title="%s"' % html.escape(comment, quote=True)
                        if comment else '',
                    content,
                ), end='')

            elif prev_cell:
                print(' <td class="pkt-removed"></td>')
            else:
                print(' <td class="pkt-not-present"></td>', end='')
        print('</tr>')
    print('      </table>')

    print('      <table class="pkt-grid left-header">')
    print('          <colgroup> <col> </colgroup>')
    for packet_class in packet_classes:
        classes = ['state-%s' % packet_class.state.lower(),
                   'bound-%s' % packet_class.bound.lower()]
        title = None
        if packet_class in pycraft_classes:
            classes.append('pycraft-pkt-cls')
            title = pycraft_classes[packet_class].py_name
        print('          <tr><th class="%s"%s>%s</th></tr>' % (
            ' '.join(classes),
            (' title="%s"' % title) if title is not None else '',
            packet_class.name),
        end='')
    print('      </table>')

    spacer = '&nbsp;<br>&nbsp;<sup>&nbsp;</sup>' if any_sup else \
             '&nbsp;<br>&nbsp;'
    print('      <table class="pkt-grid legend-min">')
    print('          <colgroup> <col></col> </colgroup>')
    print('          <tr><th>')
    print(              '<div class="l-spacer">%s</div>' % spacer)
    print('              <div class="l-text"></div>', end='')
    print(              '<div class="l-spacer">%s</div>' % spacer)
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
    print('                 <div class="l-sample l-pkt-id pkt-chg-unk">0x00</div>')
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
