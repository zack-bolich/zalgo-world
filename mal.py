import sys
from collections import deque

XLAT1 = '+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA"lI.v%{gJh4G\\-=O@5`_3i<?Z\';FNQuY]szf$!BS/|t:Pn6^Ha'
XLAT2 = '5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK\'X~xDl}REokN:#?G"i@'
assert len(XLAT1) == 94 and len(XLAT2) == 94
T = [[1, 0, 0], [1, 0, 2], [2, 2, 1]]  # T[d][a]
P3 = [3 ** i for i in range(10)]

def crz(a, d):
    r = 0
    for i in range(10):
        r += T[(d // P3[i]) % 3][(a // P3[i]) % 3] * P3[i]
    return r

def rot(x):
    return x // 3 + (x % 3) * 19683

def run(src, max_steps=10_000_000):
    src = ''.join(ch for ch in src if not ch.isspace())
    mem = [0] * 59049
    for i, ch in enumerate(src):
        x = ord(ch)
        if XLAT1[(x - 33 + i) % 94] not in 'ji*p</vo':
            raise ValueError(f'invalid char at {i}')
        mem[i] = x
    for i in range(len(src), 59049):
        mem[i] = crz(mem[i - 1], mem[i - 2])
    a = c = d = 0
    out = bytearray()
    for _ in range(max_steps):
        if not 33 <= mem[c] <= 126:
            raise RuntimeError('mem[c] out of range')
        op = XLAT1[(mem[c] - 33 + c) % 94]
        if op == 'j': d = mem[d]
        elif op == 'i': c = mem[c]
        elif op == '*': a = mem[d] = rot(mem[d])
        elif op == 'p': a = mem[d] = crz(a, mem[d])
        elif op == '<': out.append(a % 256)
        elif op == 'v': return bytes(out)
        elif op == '/': raise RuntimeError('input not supported')
        if not 33 <= mem[c] <= 126:
            raise RuntimeError('mem[c] out of range before encrypt')
        mem[c] = ord(XLAT2[mem[c] - 33])
        c = (c + 1) % 59049
        d = (d + 1) % 59049
    raise RuntimeError('too many steps')

def char_for(op, pos):
    for x in range(33, 127):
        if XLAT1[(x - 33 + pos) % 94] == op:
            return chr(x)
    raise ValueError

def generate(data):
    prog = []
    a = 0
    for target in data:
        pos = len(prog)
        # BFS over (a) with sequences of nop/opr/rot; c == d, operand is the cell's own value
        start = (a, ())
        seen = {a}
        q = deque([start])
        found = None
        while q:
            cur, seq = q.popleft()
            if cur % 256 == target:
                found = (cur, seq)
                break
            if len(seq) > 12:
                continue
            p = pos + len(seq)
            for op in 'p*o':
                ch = char_for(op, p)
                v = ord(ch)
                if op == 'p': na = crz(cur, v); nv = na
                elif op == '*': na = rot(v); nv = na
                else: na = cur; nv = v
                if not 33 <= nv <= 126:
                    continue  # keep memory printable so every interpreter agrees
                if op == 'o':
                    continue  # nop never changes a; skip as a search move
                if na in seen:
                    continue
                seen.add(na)
                q.append((na, seq + (ch,)))
        if found is None:
            raise RuntimeError(f'no path for byte {target}')
        a, seq = found
        prog.extend(seq)
        prog.append(char_for('<', len(prog)))
    prog.append(char_for('v', len(prog)))
    return ''.join(prog)

if __name__ == '__main__':
    hw = "(=<`#9]~6ZY32Vx/4Rs+0No-&Jk)\"Fh}|Bcy?`=*z]Kw%oG4UUS0/@-ejc(:'8dc"
    print('classic test:', run(hw))
