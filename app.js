async function carregarPlanilhas() {
    const galeria = document.getElementById('galeria');
    const infoDatas = document.getElementById('info-datas');

    try {
        const res = await fetch('dados.json?v=' + new Date().getTime());
        if (!res.ok) throw new Error('Falha ao carregar dados');
        const dados = await res.json();

        if (!dados.dias || dados.dias.length === 0) {
            galeria.innerHTML = '<p class="loading">Nenhuma planilha postada ainda.</p>';
            infoDatas.innerHTML = '<span class="linha-destaque">Aguardando primeira postagem</span>';
            return;
        }

        const maisRecente = dados.dias[0].data;
        const [a, m, d] = maisRecente.split('-');
        infoDatas.innerHTML = `
            <span class="linha-destaque">📅 Postagem: ${d}/${m}/${a}</span>
            <span class="linha-postado">🕒 Atualizado às 22h</span>
        `;

        galeria.innerHTML = '';
        const hojeStr = new Date().toISOString().split('T')[0];

        dados.dias.forEach(dia => {
            const ehHoje = dia.data === hojeStr;
            const card = document.createElement('div');
            card.className = 'dia-card';

            let html = `
                <div class="dia-header">
                    <span class="badge">${ehHoje ? 'ATUALIZADO HOJE' : 'POSTAGEM ANTERIOR'}</span>
                    <span class="data-texto">📅 ${dia.data.split('-').reverse().join('/')}</span>
                </div>
            `;

            const loterias = [
                { id: 'lf', nome: '🟣 Lotofácil', cor: 'var(--lf)', imgs: dia.lotofacil || [] },
                { id: 'lm', nome: '🔵 Lotomania', cor: 'var(--lm)', imgs: dia.lotomania || [] },
                { id: 'ms', nome: '🟢 Mega Sena', cor: 'var(--ms)', imgs: dia.megasena || [] }
            ];

            loterias.forEach(lot => {
                let grid = `<div class="img-grid">`;
                for (let i = 0; i < 6; i++) {
                    const imgPath = lot.imgs[i];
                    const numSlot = i + 1;

                    if (imgPath) {
                        grid += `
                            <div class="slot">
                                <img src="${imgPath}" loading="lazy" decoding="async" alt="${lot.nome} - Imagem ${numSlot}" 
                                     onload="this.style.opacity=1">
                            </div>`;
                    } else {
                        grid += `<div class="slot vazio">Espaço ${numSlot}</div>`;
                    }
                }
                grid += `</div>`;

                html += `
                    <div class="loteria-secao">
                        <span class="loteria-label" style="color:${lot.cor}">${lot.nome}</span>
                        ${grid}
                    </div>
                `;
            });

            card.innerHTML = html;
            galeria.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        galeria.innerHTML = '<p class="loading">⚠️ Erro ao carregar. Atualize a página ou verifique sua conexão.</p>';
    }
}

document.addEventListener('DOMContentLoaded', carregarPlanilhas);