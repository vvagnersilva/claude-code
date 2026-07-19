# Cloudflare dashboard — navigation reference

Used by `browser-cloudflare-pages`. Navigation only — never record env-var
values here.

## URLs

- Dashboard root: `https://dash.cloudflare.com/`
- Workers & Pages: `https://dash.cloudflare.com/?to=/:account/workers-and-pages`

## Login / hand-off

Login wall → hand control to the recipient; resume after they confirm.
The **GitHub App authorization** step is also a hand-off: Cloudflare opens a
GitHub OAuth screen the recipient must approve (for the target repo or all
repos). Never type their GitHub or Cloudflare password.

## Path: create the Pages project

**Workers & Pages → Create → Pages → Connect to Git**. Then:
- Pick the repo (matches the GitHub URL from deploy-stack Step 7).
- Project name: `PROJECT_NAME` (sets the `.pages.dev` subdomain).
- Production branch: `main`.
- Framework preset: **None**.
- Build command: **empty**.
- Build output directory: **`/`** (a single forward slash — this one trips
  people; wrong value = blank/404 pages).
- **Confirm with the recipient before "Save and Deploy."** First deploy may
  fail/blank — expected until D1 + env vars are set.

## Path: bind the D1 database

Project → **Settings → Bindings → Add → D1 database**.
- Variable name: **`DB`** (exactly — code reads `env.DB`).
- Database: `${PROJECT_NAME}-db`.
- Apply to: Production (and Preview if used).

## Path: environment variables

Project → **Settings → Environment variables → Add variable** → Production.
Toggle **Encrypt** on every secret row before saving. See deploy-stack Step
10 for the full table of which vars and which to encrypt. Encrypted values
show masked afterward — that's correct, not a failure.

## Path: trigger a redeploy

Project → **Deployments** tab → latest deployment → **Retry deployment**.
(Or push any commit to `main`.) Wait for green (~1-2 min).

## Known drift points

- The Pages creation flow has been relocated under "Workers & Pages → Create"
  and previously under a standalone "Pages" tab; check both.
- "Bindings" has at times lived under "Functions" rather than "Settings".
- Build configuration ("Build output directory") is under **Settings →
  Builds → Configure production deployments** after initial creation.
