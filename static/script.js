const MAX_TIME = 11;

const POS_ABBR = {
    Atacante: 'ATK', Goleiro: 'GOL', Zagueiro: 'ZAG',
    Lateral: 'LAT', Meiocampo: 'MEI'
};

const STAT_LABEL = {
    velocidade: 'VEL', chute: 'CHU', passe: 'PAS', drible: 'DRI',
    defesa: 'DEF', fisico: 'FIS', elasticidade: 'ELA', manejo: 'MAN',
    reflexo: 'REF', posicionamento: 'POS', marcacao: 'MAR', forca: 'FOR',
    cabeceio: 'CAB', cruzamento: 'CRU', visao: 'VIS', resistencia: 'RES'
};

// atributos exibidos no card por posição
const CARD_STATS = {
    Atacante:  ['velocidade', 'chute', 'drible'],
    Goleiro:   ['reflexo', 'posicionamento', 'elasticidade'],
    Zagueiro:  ['marcacao', 'forca', 'cabeceio'],
    Lateral:   ['velocidade', 'cruzamento', 'marcacao'],
    Meiocampo: ['passe', 'visao', 'resistencia']
};

const FLAGS = {
    'Brasil': '🇧🇷', 'França': '🇫🇷', 'Espanha': '🇪🇸', 'Noruega': '🇳🇴',
    'Bélgica': '🇧🇪', 'Holanda': '🇳🇱', 'Alemanha': '🇩🇪',
    'Inglaterra': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Croácia': '🇭🇷', 'Portugal': '🇵🇹',
    'Egito': '🇪🇬', 'Polônia': '🇵🇱', 'Nigéria': '🇳🇬',
    'Eslovênia': '🇸🇮', 'Canadá': '🇨🇦'
};

let allPlayers = [];
let teamPlayers = [];
let currentFilter = 'all';

// ── Criar card HTML ──
function createCard(player) {
    const stats = CARD_STATS[player.posicao] || [];
    const card = document.createElement('div');
    card.className = `player-card card-${player.posicao}`;
    card.dataset.nome = player.nome;

    const statsHtml = stats.map(s => `
        <div class="stat">
            <span class="stat-label">${STAT_LABEL[s] || s.slice(0,3).toUpperCase()}</span>
            <span class="stat-value">${player[s] ?? '-'}</span>
        </div>`
    ).join('');

    const flag = FLAGS[player.nacionalidade] || '';

    card.innerHTML = `
        <div class="card-top">
            <div>
                <div class="card-overall">${player.overall}</div>
                <div class="card-pos">${POS_ABBR[player.posicao] || player.posicao}</div>
            </div>
            <div class="card-nationality">${flag}<br>${player.nacionalidade}</div>
        </div>
        <div class="card-divider"></div>
        <div class="card-name">${player.nome}</div>
        <div class="card-stats">${statsHtml}</div>
        <div class="card-age">${player.idade} anos</div>
    `;

    card.addEventListener('click', () => addToTeam(player));
    return card;
}

// ── Renderizar grid de cards ──
function renderCards(players) {
    const grid = document.getElementById('cards-grid');
    grid.innerHTML = '';

    if (!players.length) {
        grid.innerHTML = '<p class="loading">Nenhum jogador nessa posição.</p>';
        return;
    }

    players.forEach(p => {
        const card = createCard(p);
        if (teamPlayers.some(t => t.nome === p.nome)) {
            card.classList.add('in-team');
        }
        grid.appendChild(card);
    });
}

// ── Adicionar ao time ──
function addToTeam(player) {
    if (teamPlayers.length >= MAX_TIME) {
        alert('O time já está completo (11 jogadores)!');
        return;
    }
    if (teamPlayers.some(p => p.nome === player.nome)) return;

    teamPlayers.push(player);
    updateTeamUI();
    renderCards(filteredPlayers());
    hideOverall();
}

// ── Remover do time ──
function removeFromTeam(nome) {
    teamPlayers = teamPlayers.filter(p => p.nome !== nome);
    updateTeamUI();
    renderCards(filteredPlayers());
    hideOverall();
}

// ── Atualizar painel do time ──
function updateTeamUI() {
    document.getElementById('player-count').textContent = `${teamPlayers.length} / ${MAX_TIME}`;

    const list = document.getElementById('team-list');
    if (!teamPlayers.length) {
        list.innerHTML = '<p class="empty-team">Clique em um card para adicionar ao time</p>';
        return;
    }

    list.innerHTML = teamPlayers.map(p => {
        const safeName = p.nome.replace(/'/g, "\\'");
        return `
        <div class="team-player">
            <span class="team-player-badge badge-${p.posicao}">${POS_ABBR[p.posicao]}</span>
            <div class="team-player-info">
                <div class="team-player-name">${p.nome}</div>
                <div class="team-player-meta">${FLAGS[p.nacionalidade] || ''} ${p.nacionalidade} · ${p.idade} anos</div>
            </div>
            <span class="team-player-overall">${p.overall}</span>
            <button class="remove-btn" onclick="removeFromTeam('${safeName}')">×</button>
        </div>`;
    }).join('');
}

// ── Calcular overall via API ──
async function calcularTime() {
    if (!teamPlayers.length) {
        alert('Adicione pelo menos um jogador ao time!');
        return;
    }

    const res = await fetch('/api/time/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jogadores: teamPlayers.map(p => p.nome) })
    });

    const data = await res.json();
    showOverall(data.overall);
}

// ── Mostrar overall com animação ──
function showOverall(value) {
    const display = document.getElementById('overall-display');
    const numberEl = document.getElementById('overall-number');
    const ring = document.getElementById('ring-fill');
    const desc = document.getElementById('overall-desc');

    display.style.display = 'block';

    // re-trigger animation
    display.style.animation = 'none';
    display.offsetHeight;
    display.style.animation = '';

    const circumference = 264;
    const offset = circumference - (circumference * value / 100);

    setTimeout(() => {
        numberEl.textContent = value;
        ring.style.strokeDashoffset = offset;

        if (value >= 90) {
            ring.style.stroke = '#ffd700';
            desc.textContent = '🌟 Time de nível mundial!';
        } else if (value >= 85) {
            ring.style.stroke = '#66bb6a';
            desc.textContent = '🔥 Time de elite!';
        } else if (value >= 80) {
            ring.style.stroke = '#42a5f5';
            desc.textContent = '💪 Time muito forte!';
        } else {
            ring.style.stroke = '#9e9e9e';
            desc.textContent = '⚽ Ainda há espaço para melhorar';
        }
    }, 50);
}

function hideOverall() {
    document.getElementById('overall-display').style.display = 'none';
}

function filteredPlayers() {
    if (currentFilter === 'all') return allPlayers;
    return allPlayers.filter(p => p.posicao === currentFilter);
}

// ── Filtros de posição ──
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.pos;
        renderCards(filteredPlayers());
    });
});

// ── Botão calcular ──
document.getElementById('calc-btn').addEventListener('click', calcularTime);

// ── Botão auto-montar ──
document.getElementById('auto-btn').addEventListener('click', async () => {
    const res = await fetch('/api/time/automatico');
    const data = await res.json();

    teamPlayers = data.jogadores;
    updateTeamUI();
    renderCards(filteredPlayers());
    showOverall(data.overall);
});

// ── Carregar jogadores da API ──
fetch('/api/jogadores')
    .then(r => r.json())
    .then(data => {
        allPlayers = data;
        renderCards(allPlayers);
    })
    .catch(() => {
        document.getElementById('cards-grid').innerHTML =
            '<p class="loading">Erro ao carregar jogadores.</p>';
    });
