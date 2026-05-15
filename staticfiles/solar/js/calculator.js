/* ═══════════════════════════════════════════════
   calculator.js — Lógica da calculadora solar
   PI Energia Solar
   ═══════════════════════════════════════════════ */

/**
 * Formata um número para moeda brasileira.
 * @param {number} valor
 * @param {string} prefixo
 * @returns {string}
 */
function formatarMoeda(valor, prefixo = 'R$ ') {
  return prefixo + valor.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/**
 * Lê o cookie CSRF do Django (necessário para POST).
 * @param {string} nome
 * @returns {string}
 */
function getCookie(nome) {
  const match = document.cookie.match('(^|;) ?' + nome + '=([^;]*)(;|$)');
  return match ? match[2] : '';
}

/**
 * Atualiza o label do range em tempo real.
 * Chamada pelo atributo oninput no HTML.
 * @param {HTMLInputElement} input
 * @param {string} labelId
 * @param {string} sufixo
 */
function atualizarLabel(input, labelId, sufixo = '%') {
  document.getElementById(labelId).textContent = input.value + sufixo;
}

/**
 * Exibe a seção de resultado com animação.
 */
function exibirResultado() {
  const div = document.getElementById('resultado');
  div.style.display = 'block';
  div.classList.add('show');
  div.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Preenche os cards de resultado com os dados da API.
 * @param {Object} data - Resposta JSON do backend
 */
function preencherResultado(data) {
  document.getElementById('r-potencia').textContent = data.potencia + ' kWp';
  document.getElementById('r-custo').textContent    = formatarMoeda(data.custo);
  document.getElementById('r-economia').textContent = formatarMoeda(data.economia_mensal);
  document.getElementById('r-payback').textContent  = data.payback + ' anos';

  const badge = document.getElementById('viab-badge');
if (data.classificacao === 'otimo') {
    badge.textContent = '✅ Ótimo investimento!';
    badge.className   = 'viab-badge viab-sim';
} else if (data.classificacao === 'razoavel') {
    badge.textContent = '⚠️ Viável, mas payback alto';
    badge.className   = 'viab-badge viab-nao';
} else {
    badge.textContent = '❌ Não compensa';
    badge.className   = 'viab-badge viab-nao';
}

  // Ativa o step 2 no indicador de progresso
  document.getElementById('step2').classList.add('active');
}

/**
 * Coleta os valores do formulário.
 * @returns {Object}
 */
function coletarDados() {
  return {
    consumo:    parseFloat(document.getElementById('consumo').value)    || 0,
    conta:      parseFloat(document.getElementById('conta').value)      || 0,
    tarifa:     parseFloat(document.getElementById('tarifa').value)     || 0.85,
    irradiacao: parseFloat(document.getElementById('irradiacao').value) || 5.0,
    geracao:    parseFloat(document.getElementById('geracao').value)    || 100,
    reajuste:   parseFloat(document.getElementById('reajuste').value)   || 8,
  };
}

/**
 * Função principal — envia o cálculo ao backend e exibe o resultado.
 */
async function calcular() {

  const btn = document.getElementById('btn-calcular');

  btn.classList.add('loading');

  try {

    const resposta = await fetch('/calcular/', {

      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },

      body: JSON.stringify(coletarDados()),

    });

    // tenta converter resposta em JSON
    let data;

    try {

      data = await resposta.json();

    } catch {

      throw new Error('Resposta inválida do servidor.');

    }

    // erro vindo do Django
    if (!resposta.ok) {

      alert(data.erro || 'Erro ao calcular.');

      return;
    }

    // preenche resultado
    preencherResultado(data);

    // mostra seção de resultado
    exibirResultado();

    console.log('Cálculo realizado com sucesso:', data);

  } catch (e) {

    console.error('ERRO COMPLETO:', e);

    alert(
      'Erro no sistema.\n\n' +
      'Abra o console (F12) para ver detalhes.'
    );

  } finally {

    btn.classList.remove('loading');

  }
}


