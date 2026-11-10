const api = window.API_BASE_URL.replace(/\/$/, '');
const status = document.getElementById('status');
const form = document.getElementById('form');
const submit = form.querySelector('button');
async function request(path, options = {}) {
  const response = await fetch(`${api}${path}`, {...options, signal: AbortSignal.timeout(10000)});
  if (!response.ok) throw new Error(`La API respondió ${response.status}.`);
  return response.json();
}
function text(tag, value, className) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}
async function cargarCategorias() {
  const cats = await request('/categorias');
  document.getElementById('categoria').replaceChildren(...cats.map(c => {
    const option = text('option', c); option.value = c; return option;
  }));
}
async function cargarGastos() {
  const gastos = await request('/gastos');
  document.getElementById('tbody').replaceChildren(...gastos.map(g => {
    const row = document.createElement('tr');
    const category = document.createElement('td');
    category.appendChild(text('span', g.categoria, 'tag'));
    row.append(text('td', g.descripcion), category, text('td', `$${g.monto.toFixed(2)}`));
    return row;
  }));
  document.getElementById('empty').style.display = gastos.length ? 'none' : 'block';
  document.getElementById('total').textContent = gastos.reduce((a, g) => a + g.monto, 0).toFixed(2);
  renderChart(gastos);
}
function renderChart(gastos) {
  const chart = document.getElementById('chart');
  if (!chart) return;
  chart.replaceChildren();
  const totales = new Map();
  gastos.forEach(g => totales.set(g.categoria, (totales.get(g.categoria) || 0) + g.monto));
  const entradas = [...totales].sort((a,b) => b[1] - a[1]);
  if (!entradas.length) { chart.appendChild(text('div', 'Sin datos para graficar todavía.', 'empty')); return; }
  const max = Math.max(...entradas.map(([,v]) => v));
  entradas.forEach(([cat, val]) => {
    const row = text('div', '', 'bar-row');
    const label = text('div', '', 'bar-label');
    label.append(text('span', cat), text('span', `$${val.toFixed(2)}`));
    const track = text('div', '', 'bar-track');
    const fill = text('div', '', 'bar-fill');
    fill.style.width = `${max > 0 ? Math.max(0, val / max * 100) : 0}%`;
    track.appendChild(fill); row.append(label, track); chart.appendChild(row);
  });
}
form.addEventListener('submit', async e => {
  e.preventDefault(); submit.disabled = true;
  const body = {
    descripcion: document.getElementById('descripcion').value,
    monto: parseFloat(document.getElementById('monto').value),
    categoria: document.getElementById('categoria').value,
  };
  try {
    await request('/gastos', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    form.reset(); status.textContent = 'Gasto guardado.';
    try { await cargarGastos(); }
    catch(error) { status.textContent = `El gasto se guardó, pero no se pudo actualizar la lista. ${error.message}`; }
  } catch(error) { status.textContent = `No se pudo guardar el gasto. ${error.message}`; }
  finally { submit.disabled = false; }
});
submit.disabled = true;
Promise.all([cargarCategorias(), cargarGastos()])
  .then(() => { submit.disabled = false; })
  .catch(error => { status.textContent = `No se pudo conectar con el backend. ${error.message} Recargá la página para reintentar.`; });
