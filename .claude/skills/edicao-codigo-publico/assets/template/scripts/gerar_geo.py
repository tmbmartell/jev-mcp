"""Converte GeoJSON em caminhos SVG na mesma projeção equiretangular da textura (4096x2048)."""
import json, os, sys
sys.setrecursionlimit(100000)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 4096, 2048
def px(lon, lat): return ((lon + 180) / 360 * W, (90 - lat) / 180 * H)
def rdp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1; L = (dx * dx + dy * dy) ** .5 or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps: return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]
def path(geom, eps=0.15, minlen=4):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        ring = [px(*c[:2]) for c in poly[0]]
        m = len(ring) // 2
        ring = rdp(ring[:m + 1], eps)[:-1] + rdp(ring[m:], eps)
        if len(ring) < minlen: continue
        out.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + "Z")
    return "".join(out)
cs = json.load(open(os.path.join(ROOT, "public/countries.geojson")))
sa = []; brazil = None
for f in cs["features"]:
    p = f["properties"]
    if p["ADMIN"] == "Brazil": brazil = path(f["geometry"], 0.1)
    elif p["CONTINENT"] in ("South America", "North America") or p["ADMIN"] in ("United States of America",):
        sa.append(path(f["geometry"], 0.3))
st = json.load(open(os.path.join(ROOT, "public/br-states.geojson")))
states = []
for f in st["features"]:
    p = f["properties"]
    states.append({"sigla": p.get("sigla"), "nome": p.get("name"), "regiao": p.get("regiao_id"), "d": path(f["geometry"], 0.12, 3)})
json.dump({"W": W, "H": H, "brasil": brazil, "vizinhos": sa, "estados": states,
           "brasilia": px(-47.93, -15.78), "mg": px(-44.0, -18.5)}, open(os.path.join(ROOT, "src/geo.json"), "w"), ensure_ascii=False)
print(len(brazil), len(states), [s["sigla"] for s in states][:30], st["features"][0]["properties"])
