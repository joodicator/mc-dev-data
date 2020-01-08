from .types import Vsn

__all__ = ('version_urls',)


"""A dict mapping each Minecraft version to the URL of the corresponding
   pre-release or release wiki page. Pre-release pages are preferred, when
   available, as they contain more information about protocol changes.

   Each key is of the form `Vsn(version_id_string, protocol_version_int)',
   where `version_id_string' is the key used to identify this version in
   <https://launchermeta.mojang.com/mc/game/version_manifest.json>, which
   for later versions also occurs as the 'id' key in version.json in the
   corresponding .jar file distributed by Mojang. (This is the same version
   string as used by pyCraft, and is used for pyCraft interoperation.)"""
version_urls = {
    Vsn('1.15.1',               575): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15213',
    Vsn('1.15.1-pre1',          574): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15183',
    Vsn('1.15',                 573): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15173',
    Vsn('1.15-pre7',            572): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15164',
    Vsn('1.15-pre6',            571): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15158',
    Vsn('1.15-pre5',            570): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15149',
    Vsn('1.15-pre4',            569): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15140',
    Vsn('1.15-pre3',            567): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15122',
    Vsn('1.15-pre2',            566): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15111',
    Vsn('1.15-pre1',            565): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15101',
    Vsn('19w46b',               564): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15073',
    Vsn('19w46a',               563): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15070',
    Vsn('19w45b',               562): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15056',
    Vsn('19w45a',               561): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15054',
    Vsn('19w44a',               560): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15050',
    Vsn('19w42a',               559): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15044',
    Vsn('19w41a',               558): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15032',
    Vsn('19w40a',               557): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=15013',
    Vsn('19w39a',               556): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14987',
    Vsn('19w38b',               555): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14971',
    Vsn('19w36a',               552): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14970',
    Vsn('19w35a',               551): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14969',
    Vsn('19w34a',               550): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14968',
    Vsn('1.14.4',               498): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14870',
    Vsn('1.14.4-pre7',          497): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14868',
    Vsn('1.14.4-pre6',          496): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14864',
    Vsn('1.14.4-pre5',          495): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14862',
    Vsn('1.14.4-pre4',          494): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14856',
    Vsn('1.14.4-pre3',          493): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14849',
    Vsn('1.14.4-pre2',          492): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14837',
    Vsn('1.14.4-pre1',          491): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14835',
    Vsn('1.14.3',               490): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14826',
    Vsn('1.14.3-pre4',          489): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14824',
    Vsn('1.14.3-pre3',          488): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14820',
    Vsn('1.14.3-pre2',          487): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14816',
    Vsn('1.14.3-pre1',          486): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14806',
    Vsn('1.14.2',               485): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14794',
    Vsn('1.14.2 Pre-Release 4', 484): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14788',
    Vsn('1.14.2 Pre-Release 3', 483): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14785',
    Vsn('1.14.2 Pre-Release 2', 482): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14779',
    Vsn('1.14.2 Pre-Release 1', 481): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14772',
    Vsn('1.14.1',               480): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14764',
    Vsn('1.14.1 Pre-Release 2', 479): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14762',
    Vsn('1.14.1 Pre-Release 1', 478): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14757',
    Vsn('1.14',                 477): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14752',
    Vsn('1.14 Pre-Release 5',   476): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14697',
    Vsn('1.14 Pre-Release 4',   475): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14695',
    Vsn('1.14 Pre-Release 3',   474): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14691',
    Vsn('1.14 Pre-Release 2',   473): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14687',
    Vsn('1.14 Pre-Release 1',   472): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14683',
    Vsn('19w14b',               471): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14670',
    Vsn('19w14a',               470): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14649',
    Vsn('19w13b',               469): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14642',
    Vsn('19w13a',               468): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14639',
    Vsn('19w12b',               467): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14627',
    Vsn('19w12a',               466): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14625',
    Vsn('19w11b',               465): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14613',
    Vsn('19w11a',               464): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14607',
    Vsn('19w09a',               463): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14591',
    Vsn('19w08b',               462): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14586',
    Vsn('19w08a',               461): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14585',
    Vsn('19w07a',               460): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14575',
    Vsn('19w06a',               459): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14562',
    Vsn('19w05a',               458): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14555',
    Vsn('19w04b',               457): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14550',
    Vsn('19w04a',               456): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14548',
    Vsn('19w03c',               455): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14544',
    Vsn('19w03b',               454): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14536',
    Vsn('19w03a',               453): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14530',
    Vsn('19w02a',               452): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14515',
    Vsn('18w50a',               451): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14491',
    Vsn('18w49a',               450): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14467',
    Vsn('18w48b',               449): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14461',
    Vsn('18w48a',               448): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14459',
    Vsn('18w47b',               447): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14452',
    Vsn('18w47a',               446): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14449',
    Vsn('18w46a',               445): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14441',
    Vsn('18w45a',               444): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14418',
    Vsn('18w44a',               443): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14414',
    Vsn('18w43c',               442): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14397',
    Vsn('18w43b',               441): 'https://wiki.vg/index.php?title=Pre-release_protocol&oldid=14381',
    Vsn('1.13.2',               404): 'https://wiki.vg/index.php?title=Protocol&oldid=14643',
    Vsn('1.13.2-pre2',          403): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14359',
    Vsn('1.13.2-pre1',          402): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14357',
    Vsn('1.13.1',               401): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14264',
    Vsn('1.13.1-pre2',          400): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14261',
    Vsn('1.13.1-pre1',          399): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14255',
    Vsn('18w33a',               398): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14252',
    Vsn('18w32a',               397): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14247',
    Vsn('18w31a',               396): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14196',
    Vsn('18w30b',               395): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14189',
    Vsn('18w30a',               394): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14158',
    Vsn('1.13',                 393): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14132',
    Vsn('1.13-pre10',           392): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14126',
    Vsn('1.13-pre9',            391): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14124',
    Vsn('1.13-pre8',            390): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14117',
    Vsn('1.13-pre7',            389): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14107',
    Vsn('1.13-pre6',            388): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14095',
    Vsn('1.13-pre5',            387): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14088',
    Vsn('1.13-pre4',            386): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14072',
    Vsn('1.13-pre3',            385): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14045',
    Vsn('1.13-pre2',            384): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=14030',
    Vsn('1.13-pre1',            383): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13971',
    Vsn('18w22c',               382): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13965',
    Vsn('18w22b',               381): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13951',
    Vsn('18w22a',               380): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13947',
    Vsn('18w21b',               379): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13930',
    Vsn('18w21a',               378): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13926',
    Vsn('18w20c',               377): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13917',
    Vsn('18w20b',               376): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13913',
    Vsn('18w20a',               375): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13910',
    Vsn('18w19b',               374): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13905',
    Vsn('18w19a',               373): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13896',
    Vsn('18w16a',               372): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13891',
    Vsn('18w15a',               371): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13824',
    Vsn('18w14b',               370): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13744',
    Vsn('18w14a',               369): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13741',
    Vsn('18w11a',               368): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13724',
    Vsn('18w10d',               367): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13702',
    Vsn('18w10c',               366): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13699',
    Vsn('18w10b',               365): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13693',
    Vsn('18w10a',               364): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13692',
    Vsn('18w09a',               363): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13671',
    Vsn('18w08b',               362): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13666',
    Vsn('18w08a',               361): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13662',
    Vsn('18w07c',               360): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13658',
    Vsn('18w07b',               359): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13653',
    Vsn('18w07a',               358): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13648',
    Vsn('18w06a',               357): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13636',
    Vsn('18w05a',               356): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13628',
    Vsn('18w03b',               355): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13623',
    Vsn('18w02a',               353): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13582',
    Vsn('18w01a',               352): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13576',
    Vsn('17w50a',               351): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13556',
    Vsn('17w49b',               350): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13524',
    Vsn('17w49a',               349): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13516',
    Vsn('17w48a',               348): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13512',
    Vsn('17w47b',               347): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13487',
    Vsn('17w47a',               346): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13476',
    Vsn('17w46a',               345): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13472',
    Vsn('17w45b',               344): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13414',
    Vsn('17w45a',               343): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13413',
    Vsn('17w43b',               342): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13398',
    Vsn('17w43a',               341): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13396',
    Vsn('1.12.2',               340): 'http://wiki.vg/index.php?title=Protocol&oldid=13488',
    Vsn('1.12.2-pre2',          339): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13355',
    Vsn('1.12.1',               338): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13287',
    Vsn('1.12.1-pre1',          337): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13267',
    Vsn('17w31a',               336): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=13265',
    Vsn('1.12',                 335): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12929',
    Vsn('1.12-pre7',            334): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12918',
    Vsn('1.12-pre6',            333): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=12909',
    Vsn('1.12-pre5',            332): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10809',
    Vsn('1.12-pre4',            331): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10804',
    Vsn('1.12-pre3',            330): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10803',
    Vsn('1.12-pre2',            329): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=10418',
    Vsn('1.12-pre1',            328): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=9819',
    Vsn('17w18b',               327): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8548',
    Vsn('17w18a',               326): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8546',
    Vsn('17w17b',               325): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8536',
    Vsn('17w17a',               324): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8528',
    Vsn('17w16b',               323): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8519',
    Vsn('17w16a',               322): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8515',
    Vsn('17w15a',               321): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8499',
    Vsn('17w14a',               320): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8490',
    Vsn('17w13b',               319): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8475',
    Vsn('17w13a',               318): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8454',
    Vsn('17w06a',               317): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8414',
    Vsn('1.11.2',               316): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8356',
    Vsn('1.11',                 315): 'http://wiki.vg/index.php?title=Protocol&oldid=8405',
    Vsn('1.11-pre1',            314): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8249',
    Vsn('16w44a',               313): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8246',
    Vsn('16w42a',               312): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8225',
    Vsn('16w41a',               311): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8218',
    Vsn('16w40a',               310): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8204',
    Vsn('16w39c',               309): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8177',
    Vsn('16w39b',               308): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8149',
    Vsn('16w39a',               307): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8141',
    Vsn('16w38a',               306): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8118',
    Vsn('16w36a',               305): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8099',
    Vsn('16w35a',               304): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8094',
    Vsn('16w33a',               303): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8084',
    Vsn('16w32b',               302): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8063',
    Vsn('16w32a',               301): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=8062',
    Vsn('1.10.2',               210): 'http://wiki.vg/index.php?title=Protocol&oldid=8235',
    Vsn('1.10-pre2',            205): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7961',
    Vsn('1.10-pre1',            204): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7950',
    Vsn('16w21b',               203): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7935',
    Vsn('16w21a',               202): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7877',
    Vsn('16w20a',               201): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7859',
    Vsn('1.9.4',                110): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7804',
    Vsn('1.9.2',                109): 'http://wiki.vg/index.php?title=Protocol&oldid=7817',
    Vsn('1.9.1',                108): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7552',
    Vsn('1.9',                  107): 'http://wiki.vg/index.php?title=Protocol&oldid=7617',
    Vsn('1.9-pre4',             106): 'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7412',
    Vsn('16w04a',               97):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7374',
    Vsn('16w02a',               95):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7313',
    Vsn('15w51b',               94):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7261',
    Vsn('15w40b',               76):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=7122',
    Vsn('15w38b',               73):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6965',
    Vsn('15w38a',               72):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6932',
    Vsn('15w36d',               70):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6925',
    Vsn('15w36c',               69):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6883',
# These commented-out pages use a format that isn't supported by the current parser:
#    Vsn('15w35e',               66):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6851',
#    Vsn('15w35b',               63):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6829',
#    Vsn('15w34a',               58):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6809',
#    Vsn('15w33c',               57):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6806',
#    Vsn('15w33b',               56):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6796',
#    Vsn('15w33a',               55):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6790',
#    Vsn('15w32c',               54):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6788',
#    Vsn('15w32a',               52):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6785',
#    Vsn('15w31c',               51):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6780',
#    Vsn('15w31b',               50):  'http://wiki.vg/index.php?title=Pre-release_protocol&oldid=6746',
    Vsn('1.8.9',                47):  'http://wiki.vg/index.php?title=Protocol&oldid=7368',
}
