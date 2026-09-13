#!/usr/bin/env python3
"""urdf_lint.py: catch the URDF problems that make Isaac Lab explode, before you load it.

Checks (no ROS, no Isaac, stdlib only):
  E1 multiple root links / disconnected kinematic tree (parses as XML, crashes in PhysX)
  E2 link with zero/negative mass or missing <inertial> (robot flies on frame 1, reward NaN)
  E3 inertia tensor not symmetric positive-definite / violates triangle inequality
  E4 inertia wildly inconsistent with mass (typical unit error: mm vs m, g vs kg)
  W1 collision uses the same high-poly mesh as visual (1024 envs -> OOM)
  W2 joint missing <limit effort/velocity> (actuator config silently wrong)
  W3 joint with zero-range limits / lower > upper
  W4 mesh paths that do not exist relative to the URDF
Usage: python3 urdf_lint.py robot.urdf [--strict]   exit 1 on any E*, and on W* with --strict
"""
import sys, os, math, xml.etree.ElementTree as ET

def fnum(s, d=0.0):
    try: return float(s)
    except Exception: return d

def main(path, strict=False):
    errs, warns = [], []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"E0 XML parse error: {e}"); return 1
    base = os.path.dirname(os.path.abspath(path))
    links = {l.get('name'): l for l in root.findall('link')}
    joints = root.findall('joint')
    children = set(); parents = {}
    for j in joints:
        p = j.find('parent'); c = j.find('child')
        if p is None or c is None: errs.append(f"E1 joint '{j.get('name')}' missing parent/child"); continue
        pn, cn = p.get('link'), c.get('link')
        for n in (pn, cn):
            if n not in links: errs.append(f"E1 joint '{j.get('name')}' references unknown link '{n}'")
        if cn in parents: errs.append(f"E1 link '{cn}' has two parents ('{parents[cn]}' and '{pn}')")
        parents[cn] = pn; children.add(cn)
    roots = [n for n in links if n not in children]
    if len(roots) == 0 and links: errs.append("E1 no root link: kinematic loop")
    if len(roots) > 1: errs.append(f"E1 multiple root links (disconnected tree): {roots}. Isaac/Gazebo will float or crash.")
    # reachability from first root
    if roots:
        seen = {roots[0]}; stack = [roots[0]]
        kids = {}
        for c, p in parents.items(): kids.setdefault(p, []).append(c)
        while stack:
            n = stack.pop()
            for k in kids.get(n, []):
                if k not in seen: seen.add(k); stack.append(k)
        orphan = set(links) - seen
        if orphan and len(roots) == 1: errs.append(f"E1 links unreachable from root: {sorted(orphan)}")

    for name, l in links.items():
        inertial = l.find('inertial')
        has_geom = l.find('visual') is not None or l.find('collision') is not None
        if inertial is None:
            if has_geom and name != (roots[0] if roots else None):
                errs.append(f"E2 link '{name}' has geometry but no <inertial>; PhysX assigns default mass -> wrong dynamics")
            continue
        m = fnum(inertial.findtext('mass/[@value]') or (inertial.find('mass').get('value') if inertial.find('mass') is not None else '0'))
        if m <= 0: errs.append(f"E2 link '{name}' mass={m} (<=0). Robot will launch on frame 1 / NaN reward."); continue
        I = inertial.find('inertia')
        if I is None: errs.append(f"E2 link '{name}' has mass but no <inertia>"); continue
        ixx, iyy, izz = (fnum(I.get(k)) for k in ('ixx', 'iyy', 'izz'))
        ixy, ixz, iyz = (fnum(I.get(k)) for k in ('ixy', 'ixz', 'iyz'))
        if min(ixx, iyy, izz) <= 0: errs.append(f"E3 link '{name}' non-positive diagonal inertia ({ixx:.3g},{iyy:.3g},{izz:.3g})")
        else:
            # principal-axis triangle inequality (approx using diagonals; tightened by off-diagonals)
            if ixx + iyy < izz * 0.999 or ixx + izz < iyy * 0.999 or iyy + izz < ixx * 0.999:
                errs.append(f"E3 link '{name}' inertia violates triangle inequality; not a physical body")
            # PD check via determinant of 3x3
            det = ixx*(iyy*izz - iyz*iyz) - ixy*(ixy*izz - iyz*ixz) + ixz*(ixy*iyz - iyy*ixz)
            if det <= 0: errs.append(f"E3 link '{name}' inertia tensor not positive-definite (det={det:.3g})")
            # plausibility: for a body of mass m and characteristic size r, I ~ m r^2. Flag if I/m implies r < 1 mm or r > 10 m
            r = math.sqrt(max(ixx, iyy, izz) / m)
            if r < 1e-3: warns.append(f"E4 link '{name}': inertia/mass implies size {r*1000:.2f} mm; likely mm^2 or g units. Isaac will be jittery/unstable")
            if r > 10: errs.append(f"E4 link '{name}': inertia/mass implies size {r:.1f} m; unit error (mm vs m?)")
        # W1 collision == visual mesh
        vis = [g.get('filename') for g in l.findall('visual/geometry/mesh')]
        col = [g.get('filename') for g in l.findall('collision/geometry/mesh')]
        for f in col:
            if f in vis: warns.append(f"W1 link '{name}' uses visual mesh as collision ({os.path.basename(f)}). Replace with primitives or convex decomposition; N envs x high-poly = OOM")
        for f in dict.fromkeys(vis + col):
            if f and f.startswith('package://'): continue
            if f and not os.path.exists(os.path.join(base, f)) and not os.path.exists(f):
                warns.append(f"W4 link '{name}' mesh not found: {f}")

    for j in joints:
        jt = j.get('type'); n = j.get('name')
        if jt in ('revolute', 'prismatic', 'continuous'):
            lim = j.find('limit')
            if lim is None or lim.get('effort') is None or lim.get('velocity') is None:
                warns.append(f"W2 joint '{n}' ({jt}) missing <limit effort= velocity=>; actuator cfg in Isaac Lab will be wrong")
            elif jt != 'continuous':
                lo, hi = fnum(lim.get('lower')), fnum(lim.get('upper'))
                if hi <= lo: warns.append(f"W3 joint '{n}' limits lower={lo} upper={hi}")

    for e in errs: print(e)
    for w in warns: print(w)
    print(f"\n{len(links)} links, {len(joints)} joints, root={roots}, {len(errs)} errors, {len(warns)} warnings")
    return 1 if errs or (strict and warns) else 0

if __name__ == '__main__':
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1], '--strict' in sys.argv))
