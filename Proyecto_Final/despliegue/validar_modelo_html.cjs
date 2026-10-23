// Ejecutar el motor algebraico real incluido en HTML contra referencias de scikit-learn.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const engine = html.match(/<script id="model-engine">([\s\S]*?)<\/script>/)[1];
const data = JSON.parse(html.match(/<script id="payload" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'artefactos/casos_paridad.json'), 'utf8'));
const ctx = vm.createContext({});
vm.runInContext(engine, ctx);
let maxError = 0;
for (const c of cases) {
  const p = ctx.predictPortable(c.valores, data.modelo);
  maxError = Math.max(maxError, Math.abs(p-c.probabilidad));
  assert(Math.abs(p-c.probabilidad) < 1e-12);
  assert.strictEqual(p >= data.modelo.umbral, c.probabilidad >= data.modelo.umbral);
}
console.log(JSON.stringify({casos:cases.length, max_error:maxError, clases_identicas:true}));

