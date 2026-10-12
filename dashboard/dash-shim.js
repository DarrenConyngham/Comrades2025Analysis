// Minimal stand-in for the hosted dashboard's `dash` API, so the page runs
// from this folder. Loads the files in data/, runs the page's calculations and
// redraws on data arrival and resize.
(() => {
  const sources = {
    runners: 'data/runners.csv',
    leaders: 'data/leaders.csv',
    route: 'data/route.json',
    coast: 'data/coast.json',
    places: 'data/places.json',
  };
  const results = {};
  const calcs = {};
  const listeners = [];
  const state = (id) => results[id] || { status: 'loading', data: [], columns: [] };

  const runCalcs = () => {
    Object.entries(calcs).forEach(([id, c]) => {
      if (results[id] && results[id].status === 'ok') return;
      const inputs = c.inputs.map(state);
      if (inputs.some((d) => d.status === 'error')) results[id] = { status: 'error', data: [], columns: [] };
      else if (inputs.every((d) => d.status === 'ok')) {
        const data = c.fn(...inputs.map((d) => d.data));
        results[id] = { status: 'ok', data, columns: data.length ? Object.keys(data[0]) : [] };
      }
    });
  };
  const notify = () => { runCalcs(); listeners.forEach((fn) => fn()); };

  window.dash = {
    colors: ['#4e86e4', '#e0663a', '#2fa37a', '#b05cc6', '#d6a21e', '#3fb3c4', '#d14d7b', '#7c8a99'],
    data: state,
    onData(fn) { listeners.push(fn); fn(); },
    calc(id, c) { calcs[id] = c; runCalcs(); },
    params: () => ({}),
    setParams() {},
    resetParams() {},
    setLink() {},
    refresh() {},
  };

  Object.entries(sources).forEach(([id, url]) => {
    fetch(url)
      .then((r) => { if (!r.ok) throw new Error(`${url}: ${r.status}`); return r.text(); })
      .then((text) => {
        const data = url.endsWith('.csv') ? d3.csvParse(text) : JSON.parse(text);
        results[id] = { status: 'ok', data, columns: data.columns || Object.keys(data[0] || {}) };
      })
      .catch((e) => { console.error(e); results[id] = { status: 'error', data: [], columns: [], message: String(e) }; })
      .then(notify);
  });

  let w = 0;
  new ResizeObserver(() => {
    const nw = document.getElementById('dash-root').clientWidth;
    if (nw !== w) { w = nw; listeners.forEach((fn) => fn()); }
  }).observe(document.getElementById('dash-root'));
})();
