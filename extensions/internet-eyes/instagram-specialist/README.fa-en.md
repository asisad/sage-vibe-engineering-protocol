# SAGE Ω — Instagram specialist for Internet Eyes

**Status: SOURCE_ONLY / review candidate. No host install, Router binding, Instagram login, or content publication is implied by this commit.**

## Purpose / هدف

Two complementary components, not alternatives:

- **Agent Reach Instagram** (Internet Eyes): experimental read-only `search` (USERS ONLY), `profile` and `posts` (recent descriptions) through OpenCLI. No complete Reels analytics, unified comment retrieval, publishing or DM support.
- **Jakeschincariol/instagram-agent-skill** (Content / Report): 13 Claude/Codex-consumable content strategy and drafting skills and 6 local Python text/analytics scripts. No Instagram account connection, automatic publishing or messaging.
- **SAGE Evidence Engine / Report Writer**: sources, confidence, data provenance and optional authorized Obsidian delivery remain owned by SAGE, not third-party Skill instructions.

## Pinned upstream

Repository: https://github.com/Jakeschincariol/instagram-agent-skill

Commit: `d03c56bb598be770c60b201f94237e5d1a4268a6` (September 13, 2026). Upstream plugin `1.0.0`, license MIT. Source files are NOT vendored in this SAGE integration.

## Skill roles

| User task | Skill |
|---|---|
| Reel script / hook / timing | `ig-reel` |
| Competitive research with sourced sample | `ig-viral` |
| Captions | `ig-caption` |
| Carousels | `ig-carousel` |
| Stories | `ig-story` |
| Profile audit | `ig-profile` |
| Weekly calendar | `ig-plan` |
| English-first stylistic cleanup | `ig-human` |
| Draft comment or reply | `ig-comment`, `ig-reply` |
| Draft warm DM (do not send) | `ig-dm` |
| Repurpose source material | `ig-repurpose` |
| Own-post performance audit using actual insights | `ig-audit` |

## Safe standalone installation on Windows

The standalone installation script supplied in the deployment package downloads this exact Git commit to a versioned independent folder under `%LOCALAPPDATA%\InternetEyes\InstagramAgentSkill`, checks expected Git object hashes, asks Microsoft Defender to scan, then copies all 13 `ig-*` skill folders to `%USERPROFILE%\.agents\skills` and `%USERPROFILE%\.claude\skills`. It refuses to overwrite unrelated skills, does not log in or publish, and writes a local receipt.

Optional `agent-reach add instagram` is the *existing* Agent Reach channel setup, not a dependency of the content skills, and it must not log in automatically. Confirm installed/version/doctor on the actual Windows machine before claiming deployment.

## SAGE discovery contract

Run from repo root:

    python extensions/internet-eyes/instagram-specialist/router.py status
    python extensions/internet-eyes/instagram-specialist/router.py list
    python extensions/internet-eyes/instagram-specialist/router.py route --intent reel --language fa
    python extensions/internet-eyes/instagram-specialist/router.py route --intent viral-research --language en
    python -m unittest discover -s tools -p test_sage_instagram_skill.py -v

`router.py` is an offline advisory catalog. It never executes upstream scripts, browses Instagram, grants authority, configures Agent Reach or sends content. A future approved SAGE Tool Router binding must retain existing task IDs, authority, scope, and evidence controls.

Workflow: `SAGE Ω → Internet Eyes (optional Agent Reach evidence) → Content/Report specialist (IG skills) → Evidence Engine → Report Writer → existing approved Obsidian gateway`.

## Security and accuracy limits

- No unattended scraping, no password/cookie/key extraction, no automated posting, comments, likes, follows or DMs.
- Upstream `ig-human/humanize.py` removes format characters including U+200C (essential Persian half-space). **Do not auto-run it on Persian.** Localize, preserve orthography and verify with Persian-language tests before enabling.
- The linter, scoring rules, and voice template are mainly English-oriented. Customize per brand and validate contemporary Instagram constraints.
- Upstream reports hook-score AUC about 0.56 for distinguishing actual hits from misses. Treat it as a weak-hook filter, not a virality forecast.
- `ig-viral` requires credible views and per-account median samples; Agent Reach's Instagram read channel alone cannot supply those metrics.
- Committing these source-only files is not proof that the independent skill or Agent Reach channel is installed or works on the user's Windows host.

## Acceptance before activation

Confirm 13 independent skills in Claude/Codex, a clean installation receipt from Windows, Python local smoke tests, a permitted real Instagram read if applicable, no Persian half-space regression, and SAGE Evidence Engine / Obsidian handoff with actual receipts. Keep mainline, Agent Reach source and existing Instagram sessions unchanged until then.
