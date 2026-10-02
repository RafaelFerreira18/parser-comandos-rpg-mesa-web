const input = document.querySelector('#command');
const validation = document.querySelector('#validation');
const history = document.querySelector('#history');
const executeButton = document.querySelector('#execute');
let timer, revision = 0;
async function request(path, comando) {
  const response = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({comando})});
  return response.json();
}
function validate() {
  clearTimeout(timer);
  const current = ++revision;
  validation.className = '';
  validation.textContent = input.value ? 'Conferindo sintaxe…' : 'Digite um comando ou escolha um exemplo abaixo.';
  if (!input.value) return;
  const command = input.value;
  timer = setTimeout(async () => {
    try {
      const result = await request('/api/validar', command);
      if (current !== revision) return;
      validation.className = result.ok ? 'valid' : 'invalid';
      validation.textContent = result.ok ? `Sintaxe válida · ação: ${result.acao}` : result.erro;
    } catch {
      if (current === revision) validation.textContent = 'Não foi possível conectar ao servidor.';
    }
  }, 300);
}
input.addEventListener('input', validate);
function addResult(command, result) {
  history.querySelector('.empty')?.remove();
  const article = document.createElement('article');
  article.className = result.ok ? 'result' : 'result error';
  const code = document.createElement('code'); code.textContent = command;
  const message = document.createElement('p'); message.textContent = result.mensagem || result.erro;
  article.append(code, message);
  for (const roll of result.rolagens || []) {
    const row = document.createElement('div');
    for (const value of roll.valores) {
      const die = document.createElement('span'); die.className = 'dice'; die.textContent = value; row.append(die);
    }
    const detail = document.createElement('p'); detail.className = 'detail';
    detail.textContent = `d${roll.faces} · modificador ${roll.modificador} · total ${roll.total}`;
    row.append(detail); article.append(row);
  }
  if (result.parametros) {
    const details = document.createElement('details');
    const summary = document.createElement('summary'); summary.textContent = 'Parâmetros reconhecidos';
    const pre = document.createElement('pre'); pre.className = 'detail'; pre.textContent = JSON.stringify(result.parametros, null, 2);
    details.append(summary, pre); article.append(details);
  }
  history.prepend(article);
  while (history.children.length > 30) history.lastElementChild.remove();
}
document.querySelector('#command-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (executeButton.disabled) return;
  const command = input.value;
  executeButton.disabled = true;
  try { addResult(command, await request('/api/executar', command)); }
  catch { addResult(command, {ok:false, erro:'Servidor indisponível. Confira se a aplicação está em execução.'}); }
  finally { executeButton.disabled = false; input.focus(); }
});
document.querySelector('#clear').addEventListener('click', () => {
  history.replaceChildren();
  const empty = document.createElement('p'); empty.className = 'empty'; empty.textContent = 'Registro limpo. Pronto para a próxima ação.'; history.append(empty);
});
fetch('/api/regras').then(response => response.json()).then(data => {
  for (const rule of data.regras) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = rule.nome; button.title = rule.exemplo;
    button.addEventListener('click', () => { input.value = rule.exemplo; input.focus(); validate(); });
    document.querySelector('#examples').append(button);
  }
}).catch(() => { document.querySelector('#connection').textContent = 'Servidor indisponível'; });
