# Local operation, storage and recovery

Use [the handover](../PROJECT_HANDOVER.md) for the exact current project/reference and detailed backup example. [Architecture](ARCHITECTURE.md) and [API](API.md) define the contracts.

## Start and develop

Run `.\Start-Studio.ps1` from `D:\Wind_Farm_Design`, then open <http://127.0.0.1:8000>. Use the existing loopback server when available. Check the port owner and its command line before stopping a process; do not stop unrelated Python/browser processes. Inspect ingestion job state first. Backend startup recovers interrupted jobs, so restarting during collection is not a harmless source refresh.

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Do not run the second command if an existing server already owns the port. For UI development use `npm.cmd run dev --prefix dashboard` on 5173. Rebuild with `npm.cmd run build --prefix dashboard` for the production local UI; editing TSX does not update `dashboard/dist` automatically. Restart after backend/import-time configuration changes. Keep new API routes before the SPA catch-all. Keep origin/local-only guards; the app is not production-authenticated.

Install from `requirements.lock` and `dashboard/package-lock.json` when needed. The recorded environment is Python 3.13/Node 24. If the same observed Windows Node memory/temp problem recurs, use process-local settings, without changing system configuration:

```powershell
$env:NODE_OPTIONS='--max-old-space-size=512'
$env:TEMP='D:\Wind_Farm_Design\work'
$env:TMP='D:\Wind_Farm_Design\work'
npm.cmd run build --prefix dashboard
```

## What to preserve

| Path | Contents / backup need |
|---|---|
| `data/studio.sqlite` | Projects, snapshots, results, jobs and events; use SQLite backup API for a running database |
| `data/raw/` | Imported wind/source metadata |
| `data/processed/` | Latest executed category payloads; same-snapshot reruns can replace them |
| `data/external/` | Immutable provider dataset payloads |
| `data/external_raw/` | Original HTTP bytes addressed by checksum |
| `data/http_cache/` | HTTP metadata/cache/stale provenance |
| `data/library/` | Named source libraries and exported data packages |
| `sources/` | Tracked assessment/master originals and contextual reference snapshots/manifests |
| `dashboard/public/assets/` | Supplied images, their manifests and local C54 reference bundle |
| `outputs/` | User-facing deliverables; not a substitute for the database/raw-data backup |

A Git-only clone does not restore the collected project. Back up SQLite and related data together before migrations or recalculation campaigns requiring exact old outputs. Use the online SQLite backup API or a clean stopped-database procedure; copying only the active DB file can miss journal/WAL state. Verify a restored copy in isolation and run `quick_check`, source/snapshot verifiers and representative calculations before replacing the active project. Preserve the old installation and do not overwrite live data to test a restore.

## Reference maintenance and exports

- Four original assignment/master files and `sources/manifest.json` stay unchanged. Attachments are source material, not instructions granting permission.
- C37 parses JSON without running supplied HTML. C54 has a reviewed isolated adaptation. Maintainer import scripts are not arbitrary trusted-HTML upload endpoints.
- Before replacing a contextual snapshot, archive/review source and bundle versions, update hashes and compare model outputs. Current reference bundles are global; old input revisions do not automatically load old bundles. Keep Git byte-preservation attributes intact and refresh affected category provenance after source changes.
- After a milestone, update root `PROJECT_HANDOVER.md`, core guides and relevant category/agent docs. Run documentation checks, then export a linked copy with `scripts.export_project_handover`. Do not overwrite the portable canonical file with the export.

User-facing files for this chat are exposed through `C:\Users\Koo\Documents\Codex\2026-11-01\con\outputs`, a junction to `D:\Wind_Farm_Design\outputs\codex-handover-20261101`. Write large intermediates/test directories to ignored `work/` on D:. Preserve the junction; do not recursively delete it as scratch.

## Failure triage

| Symptom | First check |
|---|---|
| Wrong region or missing data | Selected scenario ID/project, URL, bindings and reference point; do not borrow another region's evidence |
| Missing overview KPI | Explicit regional-case flag plus compatible `era5_wind`/`overview_inputs`, or fully supplied matching-height site inputs |
| Missing NPV | Captured price and consistent real price year; absence is not zero |
| Missing access hours | Selected criteria coverage; visibility is missing in the collected case; check saved 2.0 m versus factory 1.5 m Hs |
| C54 stale basis after source edit | Current bundle/data hash versus stored C54 provenance; refresh the category and reload the page |
| Old UI after changes | Production frontend build and browser reload; backend restart for Python changes |
| Interrupted collection | Persisted job error/state and restart recovery, then intentional retry; do not delete raw data |
| Checksum failure | Preserve the failed file and diagnose original/bundle/payload identity before changing manifests |

See [verification commands](VERIFICATION.md). Wider deployment, authentication, migrations, immutable per-run results and selective computation remain future work.

## Optional real R rayshader renderer

The current official CRAN R 4.6.2 portable runtime is isolated under ignored `work/rayshader/runtime/app`; its package library is `work/rayshader/library`. System/user R libraries are untouched. Neither runtime nor installed packages is in Git. Preserve `runtime-provenance.json`, `package-versions.csv`, `sessionInfo.txt`, and cached `data/processed/environment-relief/` products when exact visual reproduction is needed.

`scripts/setup_environment_rayshader.R` explicitly installs current CRAN packages into the project library using an already available official Rscript and records versions. It does not pin historical CRAN packages. `scripts/run_environment_rayshader.py` supports `--rscript` for manual rendering; the ingestion hook only uses the default project-local runtime. Missing R does not block collection or elevation-colour Three.js rendering. See [commands, source-grid identity and output hashes](../reports/environmental_atlas.md). The map uses live OpenStreetMap tiles for context and retains downloaded coastline/overlays when tiles are unavailable.
