// Runs the Strike app's Python under Pyodide in Node, on the built site (argv[2]), and prints the same lines as
// strike_cpython.py. Used by .github/workflows/site-check.yml.
import { loadPyodide } from "pyodide";
import { readFileSync } from "node:fs";
const site = process.argv[2];
const py = await loadPyodide();
py.FS.writeFile("/home/pyodide/canonical_reference.py", readFileSync(`${site}/py/canonical_reference.py`, "utf8"));
py.FS.writeFile("/home/pyodide/strike.py", readFileSync(`${site}/py/strike.py`, "utf8"));
py.FS.writeFile("/home/pyodide/adaptor_rules.py", readFileSync(`${site}/py/adaptor_rules.py`, "utf8"));
const domains = JSON.parse(readFileSync(new URL("./domains.json", import.meta.url), "utf8"));
py.runPython("import sys; sys.path.insert(0, '/home/pyodide'); import strike");
for (const d of domains) {
  py.globals.set("d", d);
  console.log(py.runPython("strike.strike(d)"));
}
