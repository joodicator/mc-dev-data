import hashlib
import re

import bs4.element

from .util import id_str
from .sources import version_urls
from .patches import patch_links, norm_packet_name
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
                    html = hashlib.sha1(html.encode('utf8')).hexdigest()
                    url = version_urls[vsn] + frag
            else:
                html, url = None, None

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
