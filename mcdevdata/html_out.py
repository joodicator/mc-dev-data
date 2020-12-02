import minecraft as pycraft

from .cache import get_page
from .matrix import version_packet_ids
from .sources import version_urls, versions, PRE
from .pycraft_util import pycraft_packet_classes
from .types import Vsn

__all__ = ('matrix_html',)


def matrix_html(show_versions=None, pycraft_only=False):
    """Print to stdout an HTML document displaying the matrix of packet IDs
       with each row giving a packet class and each column giving a version."""
    with get_page('__global__') as page:
        matrix = version_packet_ids(page)
        pycraft_classes = pycraft_packet_classes(page, show_versions)

    show_versions = versions if show_versions is None else show_versions

    packet_classes = sorted({p for ids in matrix.values() for p in ids.keys()
                             if any(p in matrix[v] for v in show_versions)
                             and (not pycraft_only or p in pycraft_classes)})

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
    for version in show_versions:
        psv = version.protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS
        pv_repr = Vsn.protocol_repr(version.protocol, html=False)
        pv_html = Vsn.protocol_repr(version.protocol, html=True)
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
    for packet_class in packet_classes:
        print('          <tr> <th></th>', end='')
        for i in range(len(show_versions)):
            prev_cell = matrix[show_versions[i+1]].get(packet_class) \
                        if i < len(show_versions)-1 else None
            if packet_class in matrix[show_versions[i]]:
                cell = matrix[show_versions[i]][packet_class]
                classes = ['pkt-present']

                changed = False
                if i < len(show_versions)-1 and prev_cell:
                    j = versions.index(show_versions[i])
                    k = versions.index(show_versions[i+1])
                    cell_k = matrix[versions[k]][packet_class]
                    while True:
                        cell_j = matrix[versions[j]][packet_class]
                        if cell_j.html == cell_k.html and cell_k.html is not None:
                            break
                        elif cell_j.base_ver == cell_k.base_ver:
                            if cell_j.changed != cell_k.changed:
                                changed = True
                            elif cell_j.changed == cell_k.changed == True \
                            and cell_j is not cell_k:
                                if cell_j.html is None or cell_k.html is None:
                                    changed = changed or None
                                else:
                                    changed = True
                            break
                        elif versions.index(cell_j.base_ver) <= k \
                        and cell_j.base_ver != versions[j]:
                            if cell_j.changed:
                                changed = True
                                break
                            j = versions.index(cell_j.base_ver)
                        else:
                            changed = changed or None
                            j += 1

                if not prev_cell:
                    if i < len(show_versions) - 1:
                        classes.append('pkt-added')
                else:
                    if cell.id != prev_cell.id:
                        classes.append('pkt-id-chg')
                    if changed is None:
                        classes.append('pkt-chg-unk')
                    elif changed:
                        classes.append('pkt-fmt-chg')

                if show_versions[i].protocol in pycraft.SUPPORTED_PROTOCOL_VERSIONS:
                    classes.append('pycraft-version')
                if packet_class in pycraft_classes:
                    classes.append('pycraft-pkt-cls')
                    if show_versions[i] in pycraft_classes[packet_class].versions:
                        classes.append('pycraft-pkt')

                content = '0x%02X' % cell.id
                if cell.url: content = '<a href="%s">%s</a>' % (cell.url, content)
                print(' <td%s>%s</td>' % (' class="%s"' % ' '.join(classes)
                      if classes else '', content), end='')
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
