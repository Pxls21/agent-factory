// omni_api.mjs — one management-API call against the OmniRoute running on THIS machine, authenticated the way
// the installed OmniRoute CLI authenticates on loopback: `apiFetch` from the CLI's own bin/cli/api.mjs sends the
// machine-bound x-omniroute-cli-token (an HMAC of the node machine id and the instance salt) — no password, no
// API key, nothing printed. Used by harness-ports/bin/omniroute_local_builder.py as its transport.
//
//   OMNIROUTE_BASE_URL=http://127.0.0.1:20128 node omni_api.mjs GET /api/health
//   node omni_api.mjs POST /api/combos body.json
//
// stdout: the HTTP status on line 1, the response body from line 2. OMNIROUTE_CLI_DIR overrides the install
// directory (default: the owner's migrated npm install). OMNIROUTE_API_KEY must be UNSET in the environment or the
// CLI prefers it over the machine token (an inference key is not a management credential).
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { pathToFileURL } from "node:url";

const cliDir = process.env.OMNIROUTE_CLI_DIR
  || path.join(os.homedir(), ".omniroute-migration-npm", "node_modules", "omniroute");
const apiModule = path.join(cliDir, "bin", "cli", "api.mjs");
if (!fs.existsSync(apiModule)) {
  process.stderr.write(`omni_api: OmniRoute CLI not found at ${apiModule} (set OMNIROUTE_CLI_DIR)\n`);
  process.exit(2);
}
const { apiFetch } = await import(pathToFileURL(apiModule).href);

const [, , method, apiPath, bodyFile] = process.argv;
if (!method || !apiPath) {
  process.stderr.write("usage: omni_api.mjs METHOD /api/path [body.json]\n");
  process.exit(64);
}
const body = bodyFile ? JSON.parse(fs.readFileSync(bodyFile, "utf8")) : undefined;
const res = await apiFetch(apiPath, { method, body, acceptNotOk: true, retry: false, timeout: 60000 });
process.stdout.write(String(res.status) + "\n" + (await res.text()) + "\n");
