from itertools import takewhile
from warnings import warn
import hashlib
import re

import bs4.element

from .util import id_str
from .sources import version_urls, protocols
from .patches import (
    patch_pre_body_min_pv, patch_pre_body, patch_links, norm_packet_name,
)
from .types import Vsn, VersionDiff, PrePacket, RelPacket
from .cache import from_page, get_soup

__all__ = ('first_heading', 'pre_versions', 'pre_packets',
           'rel_version', 'rel_packets')


@from_page(get_soup, rdoc=
"Recalculate first_heading(). Give if its code has changed.")
def first_heading(soup):
    """The text of the element with id "firstHeading" on this page. This is
       used to identify the type (e.g. release or pre-release) of page."""
    return soup.find(id='firstHeading').text.strip() 


PRE_VER_RE = re.compile(
    r'(?P<name>\d[^,]*), protocol (?P<snapshot>Snapshot )?(?P<protocol>\d+)')

@from_page(get_soup, rdoc=
"Recalculate pre_versions(). Give if its code has changed.")
def pre_versions(soup, vsn):
    """Return a VersionDiff instance containing the old and new versions
       being compared in this pre-release protocol wiki page."""
    vs = []
    body = soup.find(id='mw-content-text')
    if len(body.contents) == 1 and body.contents[0].name == 'div':
        body = body.contents[0]
    para = body.find('p', recursive=False)
    for a in para.find_all('a'):
        m = PRE_VER_RE.match(a.text.strip())
        if m is None: continue
        pv = int(m.group('protocol')) + ((1<<30) if m.group('snapshot') else 0)
        vs.append(Vsn(
            name     = m.group('name'),
            protocol = pv))
    if len(vs) == 2:
        return VersionDiff(*vs)
    else:
        raise AssertionError('[%s] Found %d versions, %r, where 2 are expected'
            ' in the first paragraph: %s' % (vsn.name, len(vs), vs, para))


def html_digest(head, name, packet_id_cell):
    text = []
    def scan(part):
        if part is packet_id_cell:
            text.append('{packet-id}')
        elif isinstance(part, bs4.element.Tag):
            style = part.attrs.get('style', '')
            if 'text-decoration: line-through;' in style: return
            for part in part.children: scan(part)
        elif type(part) in (bs4.element.NavigableString,
                            bs4.element.PreformattedString):
            text.append(str(part))
        else:
            assert isinstance(part, bs4.element.PageElement), repr(html) 

    for part in head.next_siblings:
        if part.name in ('h4', 'h3', 'h2', 'h1'): break
        scan(part)

    text = re.sub(r'\s+', ' ', ' '.join(text).strip())
    if name == 'Handshake':
        text = re.sub(r'See\s*protocol version numbers\s*\(currently.*?\)',
                      '{proto-ver}', text)

    return hashlib.sha256(text.encode('utf8')).digest()


@from_page(get_soup, rdoc=
'Recalculate pre_packets(). Give if its code has changed.')
def pre_packets(soup, vsn):
    """Returns an iterator over the `PrePacket' instance for each packet documented
       on this pre-release protocol wiki page. `vsn' should be the canonical `Vsn'
       instance associated with this page."""
    seen_names = set()
    table = soup.find(id='Packets').findNext('table', class_='wikitable')
    if table is None: return

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

        frag = None
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
            head = head.find_parent('h4')
           
            table = head.find_next_sibling('table', class_='wikitable')
            ths = table.findChildren('tr')[0].findChildren('th')
            tds = table.findChildren('tr')[1].findChildren('td')
            table_old_id, table_new_id, table_state, table_bound \
                = None, None, None, None
            for th, td in zip(ths, tds):
                if th.text.strip() == 'Packet ID':
                    packet_id_cell = td
                    if td.find('del'):
                        table_new_id = int(td.find('ins').text.strip(), 16)
                        table_old_id = int(td.find('del').text.strip(), 16)
                    else:
                        table_new_id = int(td.text.strip(), 16)
                elif th.text.strip() == 'State':
                    table_state = td.text.strip()
                elif th.text.strip() == 'Bound To':
                    table_bound = td.text.strip()

            html = html_digest(head, name, packet_id_cell)
            url = version_urls[vsn] + frag
        else:
            html, url = None, None

        if frag is not None and protocols.index(vsn.protocol) \
        <= protocols.index(patch_pre_body_min_pv):
            pb = patch_pre_body.get((vsn, PrePacket(
                name=name, old_id=table_old_id, new_id=table_new_id,
                changed=True, state=table_state, bound=table_bound)))
            if pb:
                table_old_id, table_new_id, table_state, table_bound \
                    = pb.old_id, pb.new_id, pb.state, pb.bound
            if table_old_id is None and old_id is not None:
                table_old_id = table_new_id

            if table_new_id != new_id: warn(
                '[%r, %s] New ID is 0x%02X in Contents, 0x%02X in %s.'
                % (vsn, name, new_id, table_new_id, frag))
            if table_old_id != old_id: warn(
                '[%r, %s] Old ID is %s in Contents, %s in %s.' \
                % (vsn, name, id_str(old_id), id_str(table_old_id), frag))
            if table_state != state: warn(
                '[%r, %s] State is "%s" in Contents, "%s" in %s.' \
                % (vsn, name, state, table_state, frag))
            if table_bound != bound: warn(
                '[%r, %s] Direction is is "%s" in Contents, "%s" in %s.' \
                % (vsn, name, bound, table_bound, frag))

        yield PrePacket(
            name=name, old_id=old_id, new_id=new_id, changed=changed,
            state=state, bound=bound, html=html, url=url)

REL_VER_RE = re.compile(
    r'\(currently (?P<protocol>\d+)( in Minecraft (?P<name>\d[^)]*))?\)')

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
                packet_id_cell = td
                id = int(td.text.strip(), 16)
            elif th.text.strip() == 'State':
                state = td.text.strip()
            elif th.text.strip() == 'Bound To':
                bound = td.text.strip()
        if id is None:
            continue
        head = table.findPreviousSibling('h4')
        name = norm_packet_name(head.text.strip(), state, bound)
        html = html_digest(head, name, packet_id_cell)
        url = '%s#%s' % (version_urls[vsn], head.find('span')['id'])

        yield RelPacket(name=name, id=id, state=state, bound=bound,
                        html=html, url=url)
