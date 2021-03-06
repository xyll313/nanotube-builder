#!/usr/bin/env python3
"""Nanotube generator.

For details and notation, see

http://www.photon.t.u-tokyo.ac.jp/~maruyama/kataura/chirality.html

Usage:
    ./nanotuby.py N M LENGTH [-a DIST] [--species SP] [--centered]

Options:
    -a DIST                    Atom-atom distance [default: 1.421].
    --species SP               Comma-separated pair of species to use [default: C,C].
    --centered                 Center nanotube in unit cell.
"""
import numpy as np
from numpy.linalg import norm
from fractions import gcd
from itertools import product
from geomlib import Atom, Molecule, Crystal

thre = 1e-10
vacuum = 4


def nanotube(n, m, N=1, length=None, a=1.421, species=('C', 'C'), centered=False):
    d = gcd(n, m)
    dR = 3*d if (n-m) % (3*d) == 0 else d
    t1 = (2*m+n)//dR
    t2 = -(2*n+m)//dR
    a1 = np.array((np.sqrt(3)*a, 0))
    a2 = np.array((np.sqrt(3)/2*a, -3*a/2))
    Ch = n*a1+m*a2
    T = t1*a1+t2*a2
    if length:
        N = int(np.ceil(length/norm(T)))
    Ch_proj, T_proj = [v/norm(v)**2 for v in [Ch, T]]
    basis = [np.array((0, 0)), (a1+a2)/3]
    pts = []
    for i1, i2 in product(range(0, n+t1+1), range(t2, m+1)):
        shift = i1*a1+i2*a2
        for sp, b in zip(species, basis):
            pt = b+shift
            if all(-thre < pt.dot(v) < 1-thre for v in [Ch_proj, T_proj]):
                for k in range(N):
                    pts.append((sp, pt+k*T))
    diameter = norm(Ch)/np.pi

    def gr2tube(v):
        phi = 2*np.pi*v.dot(Ch_proj)
        return np.array((diameter/2*np.cos(phi),
                         diameter/2*np.sin(phi),
                         v.dot(T_proj)*norm(T)))
    xyz = [gr2tube(v) for _, v in pts]
    m = Molecule([Atom(sp, r) for (sp, _), r in zip(pts, xyz)])
    if centered:
        m = m.shifted(np.array((1, 1, 0))*diameter*(vacuum+1)/2)
    return Crystal([((vacuum+1)*diameter, 0, 0),
                    (0, (vacuum+1)*diameter, 0),
                    (0, 0, N*norm(T))],
                   m.atoms)


if __name__ == '__main__':
    import sys
    from docopt import docopt
    args = docopt(__doc__)
    n = int(args['N'])
    m = int(args['M'])
    length = float(args['LENGTH'])
    a = float(args['-a'])
    species = args['--species'].split(',')
    nanotube(n, m, length=length, a=a, species=species, centered=args['--centered']) \
        .dump(sys.stdout, 'aims')
