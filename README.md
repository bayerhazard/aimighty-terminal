# AIM Terminal

Open Terminal 0.12.3 for Olares, packaged as an AIM app so **Open WebUI gets a real
shell and filesystem** instead of text extraction — the path for large spreadsheets
(100 MB and beyond), Parquet/SQL work, documents and generated charts.

## Why

Open WebUI's legacy interpreters are `pyodide` (browser, memory-bound) and `jupyter`
(no file browser, per-message kernel). Upstream recommends **Open Terminal** instead:
an isolated container that exposes `run_command`, `read_file`, `write_file`,
`grep_search`, `glob_search` and process control as tools. Combined with Open WebUI's
*Chat Uploads → Filesystem* setting, an attached workbook lands **in the terminal**,
with no text extraction, no RAG chunking and no copy in the Open WebUI database.

## Contents

```
OlaresManifest.yaml            root manifest (identical values to the chart)
aimterminal/
  Chart.yaml
  OlaresManifest.yaml          metadata + entrances + envs + spec
  values.yaml
  templates/deployment.yaml    ConfigMap + Deployment
  templates/secret.yaml        API key Secret (helm.sh/resource-policy: keep)
  templates/service.yaml       ClusterIP :8000
```

## Layout on Olares

| Item | Value |
|---|---|
| App name / namespace | `aimterminal` / `aimterminal-aimighty` |
| Image | `ghcr.io/open-webui/open-terminal:0.12.3` (pinned) |
| Entrance | `aimterminal`, port 8000, `authLevel: internal`, `invisible: true` |
| Home volume | userspace PVC, `/olares/rootfs/userspace/pvc-userspace-aimighty-<hash>/Data/aimterminal/home` |
| Resources | 500m–8 CPU, 1–12 GiB RAM, no GPU |

The API key is **not** in this repo: it is declared in `OlaresManifest.yaml` under
`envs:` (`required`, `type: password`), supplied at install time and rendered into the
`aimterminal-secret` Secret.

## Install

```bash
olares-cli chart package aimterminal
olares-cli market upload aimterminal-26.9.1.tgz
olares-cli market install aimterminal -s upload \
  --env OPEN_TERMINAL_API_KEY="$(python3 -c 'import secrets;print("ot-"+secrets.token_hex(24))')" --watch
```

The key must match `^.{16,}$` and stays valid across upgrades (`editable: false`).
Keep it: Open WebUI needs it for the connection.

## Connect Open WebUI

1. `Admin → Integrations → Open Terminal → Add`
2. URL `https://<appid>.aimighty.olares.de`, auth **Bearer**, key = `OPEN_TERMINAL_API_KEY`
3. **Chat Uploads: Filesystem** (attachments go to the terminal, not into retrieval)
4. Access grant for all users; save.
5. Per model: enable **Builtin Tools**, native function calling.

Check the connection from inside the cluster:

```bash
curl -s https://<appid>.aimighty.olares.de/health
curl -s -H "Authorization: Bearer $OPEN_TERMINAL_API_KEY" https://<appid>.aimighty.olares.de/api/config
```

## Large workbooks

Preinstalled: pandas, numpy, scipy, scikit-learn, matplotlib, seaborn, plotly,
openpyxl, csvkit, plus duckdb, pyarrow, python-calamine, polars, xlsx2csv, tabulate.

Measured on a 104 MB / 1,000,000-row x 18-column workbook (see `xlsxbench.py`):

| Path | Result |
|---|---|
| `duckdb read_xlsx` + `GROUP BY` | seconds, aggregates only |
| `duckdb xlsx → parquet` then SQL | one conversion, then fast repeat queries |
| `python-calamine` full read | fastest whole-file read, lowest memory |
| `pandas` + `openpyxl` | works, but the slowest and hungriest route |

Guideline for the model's system prompt: aggregate (SQL/Parquet), never print raw
rows, write charts as PNG.

## Prompting note

Files attached with *Filesystem* mode are visible to the model as a path plus the
terminal tools. Ask for aggregates, not for the file's contents.
