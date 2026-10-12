// Extract Natural Earth coastline points near Durban from world-atlas land-10m.json.
// Usage: node prepare_coast.js <topojson-client dir> land-10m.json coast.json
const fs = require('fs');
const [, , tcDir, landFile, out] = process.argv;
const topojson = require(tcDir);
const topo = JSON.parse(fs.readFileSync(landFile, 'utf8'));
const land = topojson.feature(topo, topo.objects.land);
const box = { w: 29.9, e: 31.6, s: -30.4, n: -29.0 };
const inBox = ([x, y]) => x >= box.w && x <= box.e && y >= box.s && y <= box.n;
const runs = [];
for (const f of land.features ?? [land]) {
  const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
  for (const poly of polys) for (const ring of poly) {
    let cur = [];
    for (const p of ring) { if (inBox(p)) cur.push(p); else if (cur.length) { runs.push(cur); cur = []; } }
    if (cur.length) runs.push(cur);
  }
}
console.log('runs', runs.map((r) => r.length));
const rows = [];
runs.forEach((r, part) => r.forEach(([lon, lat]) => rows.push({ part, lon: +lon.toFixed(5), lat: +lat.toFixed(5) })));
console.log(rows[0], rows[rows.length - 1]);
fs.writeFileSync(out, JSON.stringify(rows));
