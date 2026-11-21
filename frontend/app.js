const els = {
  banner: document.getElementById('banner'),
  statusPill: document.getElementById('status-pill'),
  countdown: document.getElementById('countdown'),
  totalRuns: document.getElementById('total-runs'),
  modelChip: document.getElementById('model-chip'),
  sourceChip: document.getElementById('source-chip'),
  intervalChip: document.getElementById('interval-chip'),
  syncTime: document.getElementById('sync-time'),
  runNow: document.getElementById('run-now'),
  refreshSelect: document.getElementById('refresh-interval'),
  fixtures: document.getElementById('fixtures'),
  runs: document.getElementById('runs'),
  logPath: document.getElementById('log-path'),
  mFixtures: document.getElementById('m-fixtures'),
  mPositive: document.getElementById('m-positive'),
  mBest: document.getElementById('m-best'),
  mDuration: document.getElementById('m-duration'),
};

const pct = value => `${(value * 100).toFixed(1)}%`;
const signedPct = value => `${value >= 0 ? '+' : ''}${(value * 100).toFixed(1)}%`;
const ms = value => `${Number(value).toFixed(2)} ms`;
const timeFmt = new Intl.DateTimeFormat('es-EC', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
const state = { fixtures: [], predictions: {}, timer: null, openRun: null };

function banner(message, kind) {
  els.banner.hidden = !message;
  els.banner.textContent = message || '';
  els.banner.className = `banner ${kind === 'error' ? 'banner-error' : 'banner-ok'}`;
}

async function getJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail || `Error ${response.status}`);
  }
  return response.json();
}

async function loadStatus() {
  const status = await getJSON('/api/v1/agent/status');
  const running = status.enabled && status.running;
  els.statusPill.textContent = !status.enabled ? 'AGENTE DESACTIVADO' : running ? 'AGENTE ACTIVO' : 'AGENTE EN PAUSA';
  els.statusPill.className = `pill ${!status.enabled ? 'pill-off' : running ? 'pill-live' : 'pill-paused'}`;
  els.totalRuns.textContent = status.total_runs ?? 0;
  els.intervalChip.textContent = `intervalo ${status.interval_seconds}s`;
  els.modelChip.textContent = `modelo ${status.model_version}`;
  els.logPath.textContent = status.runs_repository.split(/[\\/]/).slice(-2).join('/');
  els.nextRunAt = status.next_run_at ? new Date(status.next_run_at) : null;
  return status;
}

async function loadRuns() {
  const data = await getJSON('/api/v1/agent/runs?limit=12');
  renderRuns(data.runs);
  return data.runs;
}

async function loadFixtures() {
  const data = await getJSON('/api/v1/fixtures');
  els.sourceChip.textContent = `fuente ${data.source}`;
  state.fixtures = data.fixtures;
  for (const fixture of data.fixtures) {
    state.predictions[fixture.id] = await getJSON(`/api/v1/predictions/${fixture.id}`);
  }
  renderCards();
}

function renderCards() {
  els.fixtures.innerHTML = '';
  for (const fixture of state.fixtures) {
    const prediction = state.predictions[fixture.id];
    if (!prediction) continue;
    const rows = [
      [fixture.home.name, 'home'],
      ['Empate', 'draw'],
      [fixture.away.name, 'away'],
    ];
    // El dominio devuelve claves canónicas (home/draw/away); la UI las traduce.
    const verdict = prediction.recommendation.replace(
      /\b(home|draw|away)\b/g,
      key => (key === 'draw' ? 'empate' : key === 'home' ? fixture.home.name : fixture.away.name),
    );
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div class="match-head">
        <div>
          <h3 class="match-teams">${fixture.home.name} vs ${fixture.away.name}</h3>
          <p class="match-meta">${fixture.league} · inicio ${new Date(fixture.starts_at).toLocaleString('es-EC')} · cuotas ${fixture.odds.home}/${fixture.odds.draw}/${fixture.odds.away}</p>
        </div>
        <span class="badge badge-${prediction.confidence === 'media' ? 'media' : 'neutral'}">${prediction.confidence} confianza</span>
      </div>
      <div class="bars">
        ${rows.map(([label, key]) => `
          <div class="bar-row">
            <span class="bar-label" title="${label}">${label}</span>
            <span class="bar-track"><span class="bar-fill" style="width:${prediction.probabilities[key] * 100}%"></span></span>
            <span class="bar-value"><strong>${pct(prediction.probabilities[key])}</strong> · EV ${signedPct(prediction.expected_value[key])}</span>
          </div>`).join('')}
      </div>
      <p class="verdict">${verdict}</p>
      <div class="fair">
        <span>Cuota justa ${['home', 'draw', 'away'].map(key => prediction.fair_odds[key].toFixed(2)).join(' / ')}</span>
        <span>Margen de la casa ${pct(prediction.bookmaker_margin)}</span>
      </div>
      ${prediction.warnings.length ? `<ul class="warns">${prediction.warnings.map(text => `<li>${text}</li>`).join('')}</ul>` : ''}
      <ul class="explain">${prediction.explanation.map(item => `<li>${item}</li>`).join('')}</ul>
      <div class="card-foot">${prediction.responsible_use} · modelo ${prediction.model_version} · ${new Date(prediction.generated_at).toLocaleTimeString('es-EC')}</div>`;
    els.fixtures.appendChild(card);
  }
  renderMetrics();
}

function renderRuns(runs) {
  els.runs.innerHTML = '';
  if (!runs.length) {
    els.runs.innerHTML = '<li class="empty">Sin ejecuciones todavía. Pulsa “Ejecutar análisis ahora”.</li>';
    return;
  }
  for (const run of runs) {
    const item = document.createElement('li');
    const open = state.openRun === run.id;
    item.innerHTML = `
      <div class="run-head">
        <span class="run-time">${timeFmt.format(new Date(run.started_at))}</span>
        <span class="badge badge-${run.status === 'success' ? 'neutral' : 'failed'}">${run.trigger} · ${run.status}</span>
      </div>
      <div class="run-sub">
        <span>${ms(run.duration_ms)}</span><span>${run.fixtures_analyzed} fixtures</span>
        <span>${run.model_version}</span><span>${run.data_source}</span>
      </div>
      ${run.error ? `<p class="run-error">${run.error}</p>` : ''}
      ${run.signals.length ? `<button class="run-toggle" data-id="${run.id}">${open ? 'Ocultar señales' : 'Ver señales'}</button>
        <ul class="run-signals" data-panel="${run.id}" ${open ? '' : 'hidden'}>
          ${run.signals.map(signal => `<li><strong>${signal.home} vs ${signal.away}</strong> · favorito ${signal.likely_outcome} ${pct(signal.likely_probability)} · valor ${signal.best_outcome} ${signedPct(signal.best_expected_value)} · ${signal.confidence}</li>`).join('')}
        </ul>` : ''}`;
    els.runs.appendChild(item);
  }
  els.runs.querySelectorAll('.run-toggle').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.dataset.id;
      state.openRun = state.openRun === id ? null : id;
      renderRuns(cacheRuns);
    });
  });
}

function renderMetrics() {
  els.mFixtures.textContent = state.fixtures.length;
  const all = Object.values(state.predictions).flatMap(prediction => Object.values(prediction.expected_value));
  els.mPositive.textContent = all.filter(value => value > 0).length;
  els.mBest.textContent = all.length ? signedPct(Math.max(...all)) : '—';
}

async function runNow() {
  els.runNow.disabled = true;
  try {
    const run = await getJSON('/api/v1/agent/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trigger: 'manual' }),
    });
    banner(`Ciclo manual #${run.id} completado: ${run.fixtures_analyzed} fixtures en ${run.duration_ms} ms.`, 'ok');
    await refresh();
  } catch (error) {
    banner(`No se pudo ejecutar el ciclo: ${error.message}`, 'error');
  } finally {
    els.runNow.disabled = false;
  }
}

function tickCountdown() {
  if (!els.nextRunAt) { els.countdown.textContent = 'manual'; return; }
  const seconds = Math.max(0, Math.round((els.nextRunAt - Date.now()) / 1000));
  if (seconds <= 0) { els.countdown.textContent = 'ahora'; return; }
  const mm = String(Math.floor(seconds / 60)).padStart(2, '0');
  const ss = String(seconds % 60).padStart(2, '0');
  els.countdown.textContent = `${mm}:${ss}`;
}

let cacheRuns = [];

async function refresh() {
  try {
    const status = await loadStatus();
    cacheRuns = await loadRuns();
    if (!state.fixtures.length) await loadFixtures();
    const runs = cacheRuns.filter(run => run.status === 'success');
    els.mDuration.textContent = runs.length
      ? ms(runs.reduce((sum, run) => sum + run.duration_ms, 0) / runs.length)
      : '—';
    els.syncTime.textContent = `sincronizado ${timeFmt.format(new Date())}`;
    return status;
  } catch (error) {
    banner(`La consola no pudo leer la API: ${error.message}`, 'error');
    return null;
  }
}

function scheduleAutoRefresh() {
  clearInterval(state.timer);
  const delay = Number(els.refreshSelect.value);
  if (delay > 0) state.timer = setInterval(refresh, delay);
}

els.runNow.addEventListener('click', runNow);
els.refreshSelect.addEventListener('change', scheduleAutoRefresh);
setInterval(tickCountdown, 1000);

refresh().then(status => {
  scheduleAutoRefresh();
  if (status && !status.enabled) banner('El ciclo automático está desactivado (AGENT_ENABLED=false). Usa el botón manual.', 'ok');
});
