// plots.js
// Requires global Plotly (loaded in index.html)

export function initPlots(data) {
  const F = data.positions?.length || 0;
  const x = Array.from({length: F}, (_, i) => i);

  // pull series if they exist; otherwise make empty arrays of length F
  const polar   = Array.isArray(data.polar)   && data.polar.length === F   ? data.polar   : new Array(F).fill(null);
  const azimuth = Array.isArray(data.azimuth) && data.azimuth.length === F ? data.azimuth : new Array(F).fill(null);

  const line = (y) => [{ x, y, mode: 'lines', line: { simplify: false } }];

  const layoutBase = (title, ytitle) => ({
    margin: { l: 50, r: 10, t: 30, b: 40 },
    title,
    xaxis: { title: 'Frame', rangemode: 'normal', fixedrange: false },
    yaxis: { title: ytitle, automargin: true },
    shapes: [
      // vertical cursor line (x set later)
      { type: 'line', x0: 0, x1: 0, y0: 0, y1: 1, xref: 'x', yref: 'paper' }
    ]
  });

  Plotly.newPlot('inclination', line(polar),   layoutBase('Trunk Inclination', 'deg'), {responsive: true});
  Plotly.newPlot('rotation',    line(azimuth), layoutBase('Trunk Rotation',    'deg'), {responsive: true});

  // Expose a simple cursor updater the viewer can call on each frame change
  window.updatePlotCursors = function(k) {
    Plotly.relayout('inclination', { 'shapes[0].x0': k, 'shapes[0].x1': k });
    Plotly.relayout('rotation',    { 'shapes[0].x0': k, 'shapes[0].x1': k });
  };

  // Initialize cursors at 0
  window.updatePlotCursors(0);
}
