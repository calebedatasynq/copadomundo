// ── Constantes ──────────────────────────────────────
const MAX_TIME = 11;

const POS_ABBR = {
    Atacante: 'ATK', Goleiro: 'GOL', Zagueiro: 'ZAG',
    Lateral: 'LAT', Meiocampo: 'MEI'
};

const STAT_LABEL = {
    velocidade:'VEL', chute:'CHU', passe:'PAS', drible:'DRI',
    defesa:'DEF', fisico:'FIS', elasticidade:'ELA', manejo:'MAN',
    reflexo:'REF', posicionamento:'POS', marcacao:'MAR', forca:'FOR',
    cabeceio:'CAB', cruzamento:'CRU', visao:'VIS', resistencia:'RES'
};

const CARD_STATS = {
    Atacante:  ['velocidade','chute','drible'],
    Goleiro:   ['reflexo','posicionamento','elasticidade'],
    Zagueiro:  ['marcacao','forca','cabeceio'],
    Lateral:   ['velocidade','cruzamento','marcacao'],
    Meiocampo: ['passe','visao','resistencia']
};

const POS_STATS_ALL = {
    Atacante:  ['velocidade','chute','passe','drible','defesa','fisico'],
    Goleiro:   ['elasticidade','manejo','chute','reflexo','posicionamento','velocidade'],
    Zagueiro:  ['marcacao','forca','cabeceio','velocidade','passe'],
    Lateral:   ['velocidade','cruzamento','marcacao'],
    Meiocampo: ['passe','visao','resistencia']
};

// Converte código ISO2 em emoji de bandeira
function flagEmoji(iso2) {
    if (!iso2) return '🏳️';
    return [...iso2.toUpperCase()].map(c =>
        String.fromCodePoint(0x1F1E6 + c.charCodeAt(0) - 65)
    ).join('');
}

// Mapa nome_en → iso2 (dos 48 times da Copa 2026)
const ISO2 = {
    'Algeria':'DZ','Argentina':'AR','Australia':'AU','Austria':'AT',
    'Belgium':'BE','Bosnia and Herzegovina':'BA','Brazil':'BR',
    'Canada':'CA','Cape Verde':'CV','Colombia':'CO','Croatia':'HR',
    'Czech Republic':'CZ','Democratic Republic of the Congo':'CD',
    'Ecuador':'EC','Egypt':'EG','England':'ENG','France':'FR',
    'Germany':'DE','Ghana':'GH','Haiti':'HT','Iran':'IR','Iraq':'IQ',
    'Ivory Coast':'CI','Japan':'JP','Jordan':'JO','Mexico':'MX',
    'Morocco':'MA','Netherlands':'NL','New Zealand':'NZ','Norway':'NO',
    'Panama':'PA','Paraguay':'PY','Portugal':'PT','Qatar':'QA',
    'Saudi Arabia':'SA','Scotland':'SCO','Senegal':'SN',
    'South Africa':'ZA','South Korea':'KR','Spain':'ES','Sweden':'SE',
    'Switzerland':'CH','Tunisia':'TN','Turkey':'TR','United States':'US',
    'Uruguay':'UY','Uzbekistan':'UZ','Curaçao':'CW',
};

// ── Estado global ────────────────────────────────────
let allPlayers   = [];
let teamPlayers  = [];
let currentFilter = 'all';
let currentSelecao = '';
let selecoes = [];
let compareSelected = [];   // seleções marcadas para comparar
let playerA = null, playerB = null;

// ══════════════════════════════════════════════════════
// TABS
// ══════════════════════════════════════════════════════
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
    });
});

document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.sub-tab').forEach(t => { t.style.display = 'none'; });
        btn.classList.add('active');
        document.getElementById(`sub-${btn.dataset.sub}`).style.display = 'block';
    });
});

// ══════════════════════════════════════════════════════
// ABA: MONTAR TIME
// ══════════════════════════════════════════════════════
function createCard(player) {
    const stats = CARD_STATS[player.posicao] || [];
    const card = document.createElement('div');
    card.className = `player-card card-${player.posicao}`;
    card.dataset.nome = player.nome;

    const statsHtml = stats.map(s => `
        <div class="stat">
            <span class="stat-label">${STAT_LABEL[s]}</span>
            <span class="stat-value">${player[s] ?? '-'}</span>
        </div>`).join('');

    const iso2 = ISO2[player.nacionalidade] || '';
    const flag = iso2 ? flagEmoji(iso2) : '🏳️';

    card.innerHTML = `
        <div class="card-top">
            <div>
                <div class="card-overall">${player.overall}</div>
                <div class="card-pos">${POS_ABBR[player.posicao] || player.posicao}</div>
            </div>
            <div class="card-nationality">${flag}<br><span>${player.nacionalidade}</span></div>
        </div>
        <div class="card-divider"></div>
        <div class="card-name">${player.nome}</div>
        <div class="card-stats">${statsHtml}</div>
    `;
    card.addEventListener('click', () => addToTeam(player));
    return card;
}

function renderCards(players) {
    const grid = document.getElementById('cards-grid');
    grid.innerHTML = '';
    if (!players.length) {
        grid.innerHTML = '<p class="loading">Nenhum jogador encontrado.</p>';
        return;
    }
    const frag = document.createDocumentFragment();
    players.forEach(p => {
        const card = createCard(p);
        if (teamPlayers.some(t => t.nome === p.nome)) card.classList.add('in-team');
        frag.appendChild(card);
    });
    grid.appendChild(frag);
}

function filteredPlayers() {
    let list = allPlayers;
    if (currentFilter !== 'all') list = list.filter(p => p.posicao === currentFilter);
    return list;
}

async function carregarJogadores() {
    const grid = document.getElementById('cards-grid');
    grid.innerHTML = '<div class="loading">Carregando...</div>';
    const params = new URLSearchParams();
    if (currentFilter !== 'all')  params.set('posicao', currentFilter);
    if (currentSelecao)           params.set('selecao', currentSelecao);
    const res = await fetch(`/api/jogadores?${params}`);
    allPlayers = await res.json();
    renderCards(filteredPlayers());
}

// Filtros de posição
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.pos;
        carregarJogadores();
    });
});

// ── Filtro por país (autocomplete) ──
const countryInput  = document.getElementById('country-search');
const countryDrop   = document.getElementById('country-dropdown');
const countryClear  = document.getElementById('country-clear');

function renderCountryDrop(lista) {
    countryDrop.innerHTML = lista.map(nome => {
        const iso2 = ISO2[nome] || '';
        const flag = iso2 ? flagEmoji(iso2) : '🏳️';
        return `<div class="country-opt" data-nome="${nome}">${flag} ${nome}</div>`;
    }).join('');
    countryDrop.style.display = lista.length ? 'block' : 'none';
    countryDrop.querySelectorAll('.country-opt').forEach(el => {
        el.addEventListener('click', () => {
            currentSelecao = el.dataset.nome;
            countryInput.value = el.textContent.trim();
            countryDrop.style.display = 'none';
            countryClear.style.display = 'inline-flex';
            carregarJogadores();
        });
    });
}

countryInput.addEventListener('input', () => {
    const q = countryInput.value.trim().toLowerCase();
    if (!q) {
        countryDrop.style.display = 'none';
        return;
    }
    const matches = selecoes.filter(s => s.toLowerCase().includes(q));
    renderCountryDrop(matches);
});

countryInput.addEventListener('focus', () => {
    if (countryInput.value.trim()) return;
    renderCountryDrop(selecoes);
});

document.addEventListener('click', e => {
    if (!countryInput.contains(e.target) && !countryDrop.contains(e.target))
        countryDrop.style.display = 'none';
});

countryClear.addEventListener('click', () => {
    currentSelecao = '';
    countryInput.value = '';
    countryClear.style.display = 'none';
    countryDrop.style.display = 'none';
    carregarJogadores();
});

// Adicionar ao time
function addToTeam(player) {
    if (teamPlayers.length >= MAX_TIME) { alert('Time completo!'); return; }
    if (teamPlayers.some(p => p.nome === player.nome)) return;
    teamPlayers.push(player);
    updateTeamUI();
    renderCards(filteredPlayers());
    hideOverall();
}

function removeFromTeam(nome) {
    teamPlayers = teamPlayers.filter(p => p.nome !== nome);
    updateTeamUI();
    renderCards(filteredPlayers());
    hideOverall();
}

function updateTeamUI() {
    document.getElementById('player-count').textContent = `${teamPlayers.length} / ${MAX_TIME}`;
    const list = document.getElementById('team-list');
    if (!teamPlayers.length) {
        list.innerHTML = '<p class="empty-team">Clique em um card para adicionar</p>';
        return;
    }
    list.innerHTML = teamPlayers.map(p => {
        const iso2 = ISO2[p.nacionalidade] || '';
        const flag = iso2 ? flagEmoji(iso2) : '';
        const safe = p.nome.replace(/'/g, "\\'");
        return `
        <div class="team-player">
            <span class="team-player-badge badge-${p.posicao}">${POS_ABBR[p.posicao]}</span>
            <div class="team-player-info">
                <div class="team-player-name">${p.nome}</div>
                <div class="team-player-meta">${flag} ${p.nacionalidade}</div>
            </div>
            <span class="team-player-overall">${p.overall}</span>
            <button class="remove-btn" onclick="removeFromTeam('${safe}')">×</button>
        </div>`;
    }).join('');
}

// Overall
async function calcularTime() {
    if (!teamPlayers.length) { alert('Adicione jogadores!'); return; }
    const res = await fetch('/api/time/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jogadores: teamPlayers.map(p => p.nome) })
    });
    const data = await res.json();
    showOverall(data.overall);
}

function showOverall(value) {
    const display = document.getElementById('overall-display');
    const numberEl = document.getElementById('overall-number');
    const ring = document.getElementById('ring-fill');
    const desc = document.getElementById('overall-desc');
    display.style.display = 'block';
    display.style.animation = 'none'; display.offsetHeight; display.style.animation = '';
    const offset = 264 - (264 * value / 100);
    setTimeout(() => {
        numberEl.textContent = value;
        ring.style.strokeDashoffset = offset;
        if (value >= 90) { ring.style.stroke = '#ffd700'; desc.textContent = '🌟 Time de nível mundial!'; }
        else if (value >= 85) { ring.style.stroke = '#66bb6a'; desc.textContent = '🔥 Time de elite!'; }
        else if (value >= 80) { ring.style.stroke = '#42a5f5'; desc.textContent = '💪 Time muito forte!'; }
        else { ring.style.stroke = '#9e9e9e'; desc.textContent = '⚽ Ainda há espaço para melhorar'; }
    }, 50);
}

function hideOverall() { document.getElementById('overall-display').style.display = 'none'; }

document.getElementById('calc-btn').addEventListener('click', calcularTime);

document.getElementById('auto-btn').addEventListener('click', async () => {
    const params = currentSelecao ? `?selecao=${encodeURIComponent(currentSelecao)}` : '';
    const res = await fetch(`/api/time/automatico${params}`);
    const data = await res.json();
    teamPlayers = data.jogadores;
    updateTeamUI();
    renderCards(filteredPlayers());
    showOverall(data.overall);
});

// ══════════════════════════════════════════════════════
// ABA: SELEÇÕES
// ══════════════════════════════════════════════════════
function renderSelecoes(ranking) {
    const grid = document.getElementById('selecoes-grid');
    grid.innerHTML = '';
    ranking.forEach((s, i) => {
        const iso2 = ISO2[s.selecao] || '';
        const flag = iso2 ? flagEmoji(iso2) : '🏳️';
        const bar = Math.round((s.overall_medio / 100) * 100);
        const div = document.createElement('div');
        div.className = 'selecao-card';
        div.dataset.nome = s.selecao;
        div.innerHTML = `
            <div class="sel-rank">#${i + 1}</div>
            <div class="sel-flag">${flag}</div>
            <div class="sel-name">${s.selecao}</div>
            <div class="sel-overall">${s.overall_medio}</div>
            <div class="sel-bar-wrap"><div class="sel-bar" style="width:${bar}%"></div></div>
            <div class="sel-meta">${s.jogadores} jogadores · top ${s.melhor_overall}</div>
        `;
        div.addEventListener('click', () => toggleCompareSelect(s.selecao, div));
        grid.appendChild(div);
    });
}

function toggleCompareSelect(nome, el) {
    const idx = compareSelected.indexOf(nome);
    if (idx >= 0) {
        compareSelected.splice(idx, 1);
        el.classList.remove('selected');
    } else {
        if (compareSelected.length >= 2) return;
        compareSelected.push(nome);
        el.classList.add('selected');
    }
    const bar = document.getElementById('compare-bar');
    const labels = document.getElementById('compare-sel-labels');
    if (compareSelected.length > 0) {
        bar.style.display = 'flex';
        labels.textContent = compareSelected.join(' vs ');
    } else {
        bar.style.display = 'none';
    }
}

document.getElementById('compare-clear-btn').addEventListener('click', () => {
    compareSelected = [];
    document.querySelectorAll('.selecao-card.selected').forEach(el => el.classList.remove('selected'));
    document.getElementById('compare-bar').style.display = 'none';
});

document.getElementById('compare-go-btn').addEventListener('click', () => {
    if (compareSelected.length < 2) { alert('Selecione 2 seleções!'); return; }
    // Muda para aba comparar → sub-aba seleções e preenche os selects
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-tab="comparar"]').classList.add('active');
    document.getElementById('tab-comparar').classList.add('active');

    document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.sub-tab').forEach(t => { t.style.display = 'none'; });
    document.querySelector('[data-sub="selecoes"]').classList.add('active');
    document.getElementById('sub-selecoes').style.display = 'block';

    document.getElementById('sel-a').value = compareSelected[0];
    document.getElementById('sel-b').value = compareSelected[1];
    compararSelecoes();
});

// ══════════════════════════════════════════════════════
// ABA: COMPARAR — SELEÇÕES
// ══════════════════════════════════════════════════════
async function compararSelecoes() {
    const a = document.getElementById('sel-a').value;
    const b = document.getElementById('sel-b').value;
    if (!a || !b || a === b) return;

    const res = await fetch(`/api/selecoes/comparar?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}`);
    const data = await res.json();

    const el = document.getElementById('compare-sel-result');
    el.style.display = 'grid';

    const posicoes = ['Atacante', 'Meiocampo', 'Lateral', 'Zagueiro', 'Goleiro'];
    const isoA = ISO2[a] || ''; const isoB = ISO2[b] || '';

    function buildCol(sel, isoCode) {
        const d = data[sel] || {};
        const geral = d['_geral'] || 0;
        const rows = posicoes.map(pos => {
            const p = d[pos] || {};
            return `<tr>
                <td>${pos}</td>
                <td>${p.total || 0} jog.</td>
                <td class="avg-cell">${p.avg || '-'}</td>
                <td>${p.melhor || '-'}</td>
            </tr>`;
        }).join('');
        return `
            <div class="sel-col">
                <div class="sel-col-header">
                    <span class="big-flag">${flagEmoji(isoCode)}</span>
                    <div>
                        <div class="sel-col-name">${sel}</div>
                        <div class="sel-col-overall">Overall médio: <strong>${geral}</strong></div>
                    </div>
                </div>
                <table class="sel-table">
                    <thead><tr><th>Posição</th><th>Total</th><th>Média</th><th>Top</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>`;
    }

    el.innerHTML = buildCol(a, isoA) + `<div class="vs-divider">VS</div>` + buildCol(b, isoB);
}

document.getElementById('btn-comparar-sel').addEventListener('click', compararSelecoes);

// ══════════════════════════════════════════════════════
// ABA: COMPARAR — JOGADORES
// ══════════════════════════════════════════════════════
function setupSearch(inputId, resultsId, onSelect) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);
    let timeout;

    input.addEventListener('input', () => {
        clearTimeout(timeout);
        const q = input.value.trim();
        if (q.length < 2) { results.innerHTML = ''; results.style.display = 'none'; return; }
        timeout = setTimeout(async () => {
            const res = await fetch(`/api/jogadores/buscar?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            results.innerHTML = data.map(p => `
                <div class="search-result-item" data-id="${p.id}">
                    <span class="result-name">${p.nome}</span>
                    <span class="result-meta">${p.posicao} · ${p.selecao} · ${p.overall}</span>
                </div>`).join('') || '<div class="result-empty">Nenhum resultado</div>';
            results.style.display = 'block';
            results.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    onSelect(item.dataset.id);
                    results.style.display = 'none';
                    input.value = item.querySelector('.result-name').textContent;
                });
            });
        }, 300);
    });

    document.addEventListener('click', e => {
        if (!input.contains(e.target) && !results.contains(e.target))
            results.style.display = 'none';
    });
}

async function carregarComparacao() {
    if (!playerA || !playerB) return;
    const res = await fetch(`/api/comparar/jogadores?a=${playerA}&b=${playerB}`);
    const { a, b } = await res.json();

    const slotA = document.getElementById('card-a');
    const slotB = document.getElementById('card-b');
    slotA.innerHTML = buildMiniCard(a);
    slotB.innerHTML = buildMiniCard(b);

    const statsA = POS_STATS_ALL[a.posicao] || [];
    const statsB = POS_STATS_ALL[b.posicao] || [];
    const allStats = [...new Set([...statsA, ...statsB])];

    const rows = allStats.map(stat => {
        const va = a[stat] || 0;
        const vb = b[stat] || 0;
        const max = Math.max(va, vb, 1);
        const winA = va > vb ? 'stat-win' : va < vb ? 'stat-lose' : '';
        const winB = vb > va ? 'stat-win' : vb < va ? 'stat-lose' : '';
        return `
        <div class="stat-row">
            <span class="stat-val-a ${winA}">${va || '-'}</span>
            <div class="stat-bars">
                <div class="bar-a" style="width:${(va/max)*45}%"></div>
                <span class="stat-name">${STAT_LABEL[stat] || stat}</span>
                <div class="bar-b" style="width:${(vb/max)*45}%"></div>
            </div>
            <span class="stat-val-b ${winB}">${vb || '-'}</span>
        </div>`;
    }).join('');

    const stats = document.getElementById('compare-stats');
    stats.style.display = 'block';
    stats.innerHTML = `<div class="stat-rows">${rows}</div>`;
}

function buildMiniCard(p) {
    const iso2 = ISO2[p.nacionalidade] || '';
    return `
        <div class="mini-card card-${p.posicao}">
            <div class="mini-top">
                <div>
                    <div class="mini-overall">${p.overall}</div>
                    <div class="mini-pos">${POS_ABBR[p.posicao]}</div>
                </div>
                <div class="mini-flag">${iso2 ? flagEmoji(iso2) : '🏳️'}</div>
            </div>
            <div class="mini-name">${p.nome}</div>
            <div class="mini-meta">${p.nacionalidade}</div>
        </div>`;
}

setupSearch('search-a', 'results-a', id => { playerA = id; carregarComparacao(); });
setupSearch('search-b', 'results-b', id => { playerB = id; carregarComparacao(); });

// ══════════════════════════════════════════════════════
// INICIALIZAÇÃO
// ══════════════════════════════════════════════════════
async function init() {
    // Carregar seleções para os selects
    const res = await fetch('/api/selecoes');
    selecoes = await res.json();

    const selA = document.getElementById('sel-a');
    const selB = document.getElementById('sel-b');
    selecoes.forEach(nome => {
        const iso2 = ISO2[nome] || '';
        const flag = iso2 ? flagEmoji(iso2) : '';
        const opt = `<option value="${nome}">${flag} ${nome}</option>`;
        selA.insertAdjacentHTML('beforeend', opt);
        selB.insertAdjacentHTML('beforeend', opt);
    });

    // Carregar ranking de seleções
    const rankRes = await fetch('/api/selecoes/ranking');
    const ranking = await rankRes.json();
    renderSelecoes(ranking);

    // Carregar jogadores iniciais
    carregarJogadores();
}

init();
