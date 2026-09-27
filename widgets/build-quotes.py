#!/usr/bin/env python3
"""Rebuild quote.html from quotes.txt.

Add new lines to quotes.txt (one per line), run this, commit both files.
Every embedded copy picks the change up on the next page load.

The stride is recomputed each time so it stays coprime with the new count --
that is what guarantees no quote repeats inside a 365-day window.
"""
import json, random, math, re, sys, pathlib

HERE = pathlib.Path(__file__).parent
SEED = 20260927          # keep fixed: the shuffled order stays stable between builds

qs, seen = [], set()
for line in (HERE / 'quotes.txt').read_text(encoding='utf-8').splitlines():
    q = line.strip()
    if q and q not in seen:
        seen.add(q); qs.append(q)
N = len(qs)

if N < 366:
    sys.exit(f'Refusing to build: {N} quotes. Need at least 366 for the no-repeat-in-a-year promise.')

random.Random(SEED).shuffle(qs)
stride = next(s for s in range(N // 3, N) if math.gcd(s, N) == 1)

# verify before writing
for start in range(0, 3000, 11):
    win = [((d * stride) % N) for d in range(start, start + 365)]
    assert len(set(win)) == 365, 'repeat inside a 365-day window'

p = HERE / 'quote.html'
src = p.read_text(encoding='utf-8')
src = re.sub(r'var L=\[.*?\];',
             'var L=' + json.dumps(qs, ensure_ascii=False, indent=0) + ';',
             src, flags=re.S)
src = re.sub(r'\(\(day\*\d+\)%L\.length', f'((day*{stride})%L.length', src)
p.write_text(src, encoding='utf-8')

print(f'{N} quotes, stride {stride}, first repeat after {N} days. quote.html rebuilt.')
