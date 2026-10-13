import random, sys
from collections import deque
from mal import XLAT2, crz, rot, char_for, run

class Sim:
    def __init__(self, size=40000):
        self.mem = [ord(char_for('o', i)) for i in range(size)]  # cells ahead of c are never read
        self.a = self.c = self.d = 0
        self.prog = []
    def step(self, op):
        ch = char_for(op, self.c); self.prog.append(ch)
        m, c, d = self.mem, self.c, self.d
        m[c] = ord(ch)
        assert d < c or (d == c and op in 'oj<v'), 'data pointer must stay behind code'
        if op == 'j': self.d = m[d]
        elif op == '*': self.a = m[d] = rot(m[d])
        elif op == 'p': self.a = m[d] = crz(self.a, m[d])
        assert 33 <= m[c] <= 126
        m[c] = ord(XLAT2[m[c] - 33])
        self.c += 1; self.d += 1

s = Sim()
# put d far behind c
while not (s.c >= 400 and ord(char_for('j', s.c)) < 80): s.step('o')
s.step('j')
# scribble passes: each one reads the values the previous pass wrote
seen = set()
for N in (4000, 3600, 3200, 2800):
    for _ in range(N):
        x = s.mem[s.d]
        opts = [('p', crz(s.a, x)), ('*', rot(x))]
        op = next((o for o, v in opts if v not in seen), 'p')
        s.step(op); seen.add(s.a)
    while s.mem[s.d] >= 200: s.step('o')
    s.step('j')
    print('pass distinct', len(seen), 'bytes', len({v % 256 for v in seen}), 'd', s.d, 'c', s.c, file=sys.stderr)

def emit(target):
    base = s.d
    q = deque([(s.a, ())]); seen2 = {(s.a, 0)}
    while q:
        cur, seq = q.popleft()
        if cur % 256 == target:
            for op in seq: s.step(op)
            s.step('<'); return
        if len(seq) >= 400: continue
        dv = s.mem[base + len(seq)]
        for op, na in (('p', crz(cur, dv)), ('*', rot(dv)), ('o', cur)):
            key = (na, len(seq) + 1)
            if key in seen2: continue
            seen2.add(key); q.append((na, seq + (op,)))
    raise RuntimeError(f'no path for byte {target}')

rng = random.Random(666)
above = list(range(0x0300, 0x0316)) + [0x033D, 0x0346, 0x034A, 0x0350, 0x0351, 0x0357, 0x035B]
below = list(range(0x0316, 0x0334)) + [0x0347, 0x0348, 0x0349, 0x034D, 0x034E, 0x0353, 0x0359]
text = ''
for ch in 'hello world':
    text += ch
    if ch != ' ':
        for _ in range(rng.randint(1, 3)): text += chr(rng.choice(above))
        for _ in range(rng.randint(1, 2)): text += chr(rng.choice(below))
text += '\n'
data = text.encode('utf-8')
for b in data: emit(b)
s.step('v')
prog = ''.join(s.prog)
out = run(prog)
assert out == data
print('verified; output bytes', len(data), 'program chars', len(prog), file=sys.stderr)
sys.stdout.buffer.write(out)
with open('cursed_hello.mb', 'w', encoding='ascii') as source_file:
    source_file.write(prog)
