#!/usr/bin/env python3
"""Builds story-spine.json: the whole Bible in story order as seasons, episodes and sequences of about 8 minutes.
Each part of an episode is a list of chapter spans split into n sequences balanced by verse count. Edit EPISODES and re-run."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsb
E = []   # (season, episode title, [(spans, n_sequences, note)], also)
def ep(season, title, parts, also=''): E.append((season, title, parts, also))
S = ['', 'Beginnings', 'Patriarchs', 'Exodus and Wilderness', 'Conquest and Judges', 'United Kingdom', 'Divided Kingdom and Prophets', 'Exile and Return', 'Gospels', 'Acts and Letters', 'Revelation']
ep(1, 'Creation and the Fall', [('GEN 1-3', 5, '')])
ep(1, 'Cain to the Flood', [('GEN 4-9', 5, '')])
ep(1, 'Babel and the Nations', [('GEN 10-11', 2, 'Genealogies as a map and family-tree montage.')])
ep(2, 'The Call of Abraham', [('GEN 12-17', 5, '')])
ep(2, 'Sodom and the Son of Promise', [('GEN 18-24', 6, '')])
ep(2, 'Jacob', [('GEN 25-36', 7, '')])
ep(2, 'Joseph', [('GEN 37-45', 6, '')])
ep(2, 'Israel in Egypt', [('GEN 46-50', 3, '')])
ep(2, 'Job', [('JOB 1-42', 4, 'Placement is a logged decision: set in the patriarchal age by tradition; the text gives no date. Speeches by selected verses.')])
ep(3, 'Moses and the Plagues', [('EXO 1-11', 6, '')])
ep(3, 'Passover and the Sea', [('EXO 12-18', 5, '')])
ep(3, 'Sinai', [('EXO 19-24, EXO 32-34', 5, '')])
ep(3, 'Tabernacle and Holiness', [('EXO 25-31, EXO 35-40', 2, 'Show the tabernacle being built to the pattern given.'), ('LEV 1-27', 2, 'Selected laws and the Day of Atonement; Nadab and Abihu.')])
ep(3, 'In the Wilderness', [('NUM 1-36', 7, 'Narrative chapters carry the story; censuses as montage.')])
ep(3, 'The Farewell of Moses', [('DEU 1-34', 4, 'Selected verses from the speeches; the death of Moses.')])
ep(4, 'Joshua', [('JOS 1-24', 6, 'Land allotments as a map montage.')])
ep(4, 'The Judges', [('JDG 1-12', 6, '')])
ep(4, 'Samson and the Days Without a King', [('JDG 13-21', 4, 'Chapters 19-21: violence implied, never shown.')])
ep(4, 'Ruth', [('RUT 1-4', 3, '')])
ep(5, 'Samuel and Saul', [('1SA 1-15', 6, '')])
ep(5, 'David Rises', [('1SA 16-31', 7, 'Reuse refs REF-DAVID, REF-SAUL, REF-GOLIATH and the pilot p02 material for chapter 17.')], also='Psalms tied to these events by their titles (e.g. PSA 34, 52, 54, 56, 57, 59).')
ep(5, 'David the King', [('2SA 1-10', 5, '')], also='1CH 11-17')
ep(5, 'David, Bathsheba and Absalom', [('2SA 11-24', 6, 'Bathsheba: implied, never shown.')], also='PSA 51, PSA 3; 1CH 21-29')
ep(5, 'Songs of Israel', [('PSA 1-150', 4, 'A selection of whole psalms across the five books (e.g. 1, 2, 8, 19, 22, 23, 27, 46, 90, 103, 110, 118, 121, 139, 150). Sung-poem feel: landscape and worship imagery.')])
ep(5, 'Solomon', [('1KI 1-11', 4, ''), ('PRO 1-31', 1, 'Selected proverbs as short vignettes.'), ('ECC 1-12, SNG 1-8', 1, 'Selected verses. Song of Songs: garden and vineyard imagery only.')], also='2CH 1-9')
ep(6, 'The Kingdom Divides; Elijah', [('1KI 12-22', 6, '')], also='2CH 10-20')
ep(6, 'Elisha and the Northern Kings', [('2KI 1-14', 6, ''), ('JON 1-4', 1, ''), ('AMO 1-9, HOS 1-14', 2, 'Selected oracles placed in the reign of Jeroboam II. Hosea: marriage told with restraint.')], also='2CH 21-25')
ep(6, 'The Fall of Israel; Isaiah and Hezekiah', [('2KI 15-20', 3, ''), ('ISA 1-39, MIC 1-7', 3, 'Selected oracles; Isaiah 6, 7, 9, 11; Micah 5-6.')], also='2CH 26-32')
ep(6, 'Comfort My People', [('ISA 40-66', 3, 'Selected passages including Isaiah 40, 52-53, 55, 61, 65.')])
ep(6, 'Josiah to the Fall of Jerusalem', [('2KI 21-25', 3, ''), ('JER 1-52', 3, 'Narrative chapters and selected oracles.'), ('JOL 1-3, NAM 1-3, HAB 1-3, ZEP 1-3, OBA 1', 1, 'One short selection from each. The date of Joel is uncertain; logged decision.'), ('LAM 1-5', 1, '')], also='2CH 33-36')
ep(7, 'Ezekiel by the River', [('EZK 1-48', 4, 'Visions in light and cloud; no face for God. Selected chapters 1-3, 10-11, 34, 36-37, 40-48.')])
ep(7, 'Daniel', [('DAN 1-12', 5, '')])
ep(7, 'The Return', [('EZR 1-10, HAG 1-2, ZEC 1-14', 5, 'Haggai and Zechariah placed at the temple rebuilding (Ezra 5-6).'), ('EST 1-10', 3, '')])
ep(7, 'The Wall and the Last Prophet', [('NEH 1-13, MAL 1-4', 4, 'End on the 400 silent years.')])
ep(8, 'The Word Became Flesh', [('LUK 1-2, MAT 1-2, JHN 1', 4, 'Harmony: Luke 1, Matthew 1, Luke 2, Matthew 2; John 1:1-18 as prologue.')])
ep(8, 'Baptism, Temptation, First Disciples', [('MAT 3-4, JHN 1-4, LUK 3-5', 5, '')])
ep(8, 'The Sermon on the Mount and Galilee', [('MAT 5-9, LUK 6-7', 5, '')])
ep(8, 'Parables and Wonders', [('MAT 10-15, MRK 4-7, LUK 8', 5, '')])
ep(8, 'Who Do You Say I Am', [('MAT 16-20, LUK 9-19, JHN 5-10', 6, '')])
ep(8, 'Lazarus and the Road to Jerusalem', [('JHN 11-12, MAT 21-25', 5, '')])
ep(8, 'The Upper Room to the Cross', [('JHN 13-19, MAT 26-27, LUK 22-23', 6, 'Crucifixion with restraint: no gore.')])
ep(8, 'He Is Risen', [('MAT 28, LUK 24, JHN 20-21, ACT 1', 4, 'Acts 1:1-11 for the ascension only.')])
ep(9, 'Pentecost and the First Church', [('ACT 1-7', 5, ''), ('JAS 1-5', 1, 'Selected verses, placed in the Jerusalem church.')])
ep(9, 'Saul on the Damascus Road', [('ACT 8-12', 4, '')])
ep(9, 'To the Ends of the Earth', [('ACT 13-18', 4, ''), ('GAL 1-6, 1TH 1-5, 2TH 1-3', 2, 'Selected verses, shown being written and read aloud in the churches.')])
ep(9, 'Ephesus to Rome', [('ACT 19-28', 4, ''), ('1CO 1-16, 2CO 1-13, ROM 1-16', 3, 'Selected passages (1 Corinthians 13, 15; Romans 1, 3, 5, 8, 12).')])
ep(9, 'The Last Letters', [('EPH 1-6, PHP 1-4, COL 1-4, PHM 1', 2, ''), ('1TI 1-6, TIT 1-3, 2TI 1-4, HEB 1-13', 2, ''), ('1PE 1-5, 2PE 1-3, 1JN 1-5, 2JN 1, 3JN 1, JUD 1', 2, '')])
ep(10, 'The Revelation', [('REV 1-22', 5, 'Show what John says he saw, without choosing an interpretive school.')])

def chapters(spans):
    out = []
    for sp in [x.strip() for x in spans.split(',')]:
        m = re.match(r'(\w+) (\d+)(?:-(\d+))?$', sp); b, a, z = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        for c in range(a, z + 1): out.append((b, c, len([k for k in bsb.db()[b][str(c)] if k != 'title'])))
    return out
def split(chs, n):
    total = sum(c[2] for c in chs); groups, cur, acc = [], [], 0
    for i, c in enumerate(chs):
        cur.append(c); acc += c[2]; left = len(chs) - i - 1; need = n - len(groups) - 1
        if need > 0 and (acc >= total * (len(groups) + 1) / n or left == need): groups.append(cur); cur = []
    groups.append(cur); return [g for g in groups if g]
def label(g):
    out = []; 
    for b, c, _ in g:
        if out and out[-1][0] == b and out[-1][2] == c - 1: out[-1][2] = c
        else: out.append([b, c, c])
    return [f'{b} {a}' + (f'-{z}' if z != a else '') for b, a, z in out]
units, ecount = [], {}
for season, title, parts, also in E:
    ecount[season] = ecount.get(season, 0) + 1; k = 0
    seqs = [(label(g), note, sum(c[2] for c in g)) for spans, n, note in parts for g in split(chapters(spans), n)]
    for passages, note, verses in seqs:
        units.append(dict(id=f's{season:02d}e{ecount[season]:02d}{chr(97 + k)}', season=season, season_title=S[season], episode=ecount[season], episode_title=title,
                          part=f'{k + 1}/{len(seqs)}', passages=passages, verses=verses, also=also, notes=note)); k += 1
order = [u for u in units if u['season'] != 8] + [u for u in units if u['season'] == 8]     # Gospels are generated last
json.dump(dict(units=order), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'story-spine.json'), 'w'), indent=1, ensure_ascii=False)
books = {p.split()[0] for u in units for p in u['passages']} | {b for u in units for b in re.findall(r'\b([1-3]?[A-Z]{2,3})\b', u['also'])}
print(len(units), 'sequences,', len({(u['season'], u['episode']) for u in units}), 'episodes | books not covered:', sorted(set(bsb.db()) - books))
