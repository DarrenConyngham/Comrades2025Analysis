"""Resample a Strava GPX of the route every 100 m to JSON rows {km, lat, lon, ele}.

Usage: python prepare_route.py route.gpx route.json  (timestamps and heart rate are dropped)
"""
import sys, math, json, re
src, out = sys.argv[1], sys.argv[2]
txt = open(src, encoding='utf-8').read()
pts = [(float(a), float(b), float(e)) for a, b, e in re.findall(r'<trkpt lat="([-\d.]+)" lon="([-\d.]+)">\s*<ele>([-\d.]+)</ele>', txt)]
def hav(p, q):
    R = 6371.0088
    la1, lo1, la2, lo2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    a = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*R*math.asin(math.sqrt(a))
cum = [0.0]
for i in range(1, len(pts)):
    cum.append(cum[-1] + hav(pts[i-1], pts[i]))
print('points', len(pts), 'total km', round(cum[-1], 2))
print('start', pts[0], 'end', pts[-1])
# resample every 100 m
rows, step, j = [], 0.1, 0
k = 0.0
while k < cum[-1]:
    while cum[j+1] < k: j += 1
    f = (k - cum[j]) / ((cum[j+1] - cum[j]) or 1)
    p, q = pts[j], pts[j+1]
    rows.append({'km': round(k, 2), 'lat': round(p[0]+f*(q[0]-p[0]), 5), 'lon': round(p[1]+f*(q[1]-p[1]), 5), 'ele': round(p[2]+f*(q[2]-p[2]))})
    k += step
rows.append({'km': round(cum[-1], 2), 'lat': pts[-1][0], 'lon': pts[-1][1], 'ele': round(pts[-1][2])})
json.dump(rows, open(out, 'w'), separators=(',', ':'))
print('rows', len(rows), 'max ele', max(r['ele'] for r in rows), 'min', min(r['ele'] for r in rows))
