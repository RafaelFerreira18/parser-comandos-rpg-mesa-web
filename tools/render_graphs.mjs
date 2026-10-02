// Renderizador opcional: npm install --no-save @viz-js/viz
// Ou defina RPG_VIZ_MODULE com o caminho absoluto do módulo viz.js.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
const moduleName = process.env.RPG_VIZ_MODULE ? pathToFileURL(process.env.RPG_VIZ_MODULE).href : '@viz-js/viz';
const {instance} = await import(moduleName);
const viz = await instance();
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const rules = JSON.parse(await fs.readFile(path.join(root, 'docs/manifest.json'), 'utf8'));
await fs.mkdir(path.join(root, 'tmp/graphs'), {recursive:true});
for (const rule of rules) {
  const source = await fs.readFile(path.join(root, 'automata', rule.acao + '.dot'), 'utf8');
  const svg = viz.renderString(source, {format:'svg', engine:'dot'});
  await fs.writeFile(path.join(root, 'automata', rule.acao + '.svg'), svg);
  await fs.writeFile(path.join(root, 'tmp/graphs', rule.acao + '.json'), JSON.stringify(viz.renderJSON(source)));
}
const links = rules.map(r => `<li><a href="${r.acao}.svg">${r.id}: ${r.nome}</a> · <a href="${r.acao}.jff">JFLAP</a> · <a href="${r.acao}.dot">Graphviz DOT</a></li>`).join('');
await fs.writeFile(path.join(root, 'automata/index.html'), `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>AFNε do projeto</title><style>body{max-width:900px;margin:50px auto;font:18px/1.8 system-ui;padding:20px}a{color:#3150a0}</style><h1>Autômatos dos comandos</h1><p>Diagramas vetoriais gerados pelo Graphviz ${viz.graphvizVersion}. Abra o SVG e amplie para ler cada estado. As classes entre colchetes representam transições paralelas de um símbolo. ␠ é espaço U+0020 e ε é movimento vazio.</p><ul>${links}</ul><p>Todos começam em q0 e terminam em q1. Os arquivos JFLAP expandem as classes em transições individuais. Tabelas completas em ../docs/expressoes-regulares.md.</p></html>`);
console.log(`Cinco diagramas SVG gerados pelo Graphviz ${viz.graphvizVersion}.`);
