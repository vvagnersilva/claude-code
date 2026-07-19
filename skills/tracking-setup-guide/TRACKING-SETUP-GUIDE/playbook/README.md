# Playbook — browser navigation references

These files hold the **volatile** part of the browser skills: dashboard URLs,
menu paths, and field labels that vendors change every few months. The skills
in `.claude/skills/` reference these so the skill logic stays stable while the
selectors drift here.

When a Playwright run can't find an element a skill expects, the skill falls
back to INSTRUCT mode and notes the drift. Update the matching file here with
what you observed (new menu path, renamed button) so the next run works.

| File | Covers |
|---|---|
| `meta-events-manager.md` | Meta Events Manager — Pixel selection, CAPI token generation, Test Events |
| `cloudflare-dashboard.md` | Cloudflare — Pages project creation, D1 binding, env vars, redeploy |
| `sales-platforms.md` | Eduzz / Hotmart / Kiwify webhook configuration |

**Important:** these files describe *navigation*, never *credentials*. No
tokens, passwords, slugs, or account-specific secrets belong here — those live
only in Cloudflare's encrypted env vars and the recipient's password manager.
