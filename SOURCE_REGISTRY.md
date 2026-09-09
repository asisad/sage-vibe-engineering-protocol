# SAGE v0.8 Source Registry

Status: Active source register for `0.8.0 Formalized Baseline`  
Recorded: 2026-09-06  
Hash algorithm: SHA-256

این Registry منشأ را ثبت می‌کند؛ وجود یک منبع به معنی تبدیل همهٔ محتوای آن به Rule الزامی SAGE نیست. قواعد فقط پس از تحلیل، تعمیم و ثبت disposition وارد معماری می‌شوند.

## ۱. Baselineهای حاکم

| Source | Role | SHA-256 |
|---|---|---|
| `SAGE_v0.7_MASTER_BASELINE.md` | Frozen constitutional baseline | `dc0c6baf80465e1f2cf63a2aca96f3578153a898d55752deb9a936e506fd6c0d` |
| `SAGE_HANDOFF_v0.7_to_v0.8.md` | Approved transition context | `867adab8787b00aa25024dc293c850a5d58e4b1132aa7a2f06762d179679cd5e` |
| `history/SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT_v0.8.0-draft.2.md` | Preserved pre-integration draft | `6cab3bf5006b57a01a2ab41e04e06b01dbdd46d4b1161882a9341fc8594876ac` |

Precedence: v0.7 baseline سپس تصمیم‌های صریح Handoff، سپس v0.8 جاری. هیچ Reference بیرونی حق بازنویسی خام این ترتیب را ندارد.

## ۲. منابع تحویلی اصلی

| Archived source | Classification | SHA-256 |
|---|---|---|
| `sources/supplied-originals/15-Claude-Code-Vibe-Coding-Prompts.pdf` | Original reference; informative | `bfd903ce692662eb2cad491fe42baaef45d48f7fe48fe241728be35f86c0828b` |
| `sources/supplied-originals/learn4.html` | Original reference; informative | `ba42d412f3962aa4c55d08df1aa270801ca1e2ea4be25b1d754d081bae4ba579` |

PDF در ۳۳ صفحه به‌صورت کامل استخراج و بصری بررسی شد. هشدار fallback فونت در Renderer مشاهده شد، اما متن فارسی و انگلیسی، عنوان‌ها، کادرها و شماره صفحات خوانا بودند و نقص محتوایی ناشی از Render دیده نشد.

## ۳. Integration Deltaها

| Archived source | Classification | SHA-256 |
|---|---|---|
| `sources/integration-deltas/SAGE_v0.8_SPEC_KIT_INTEGRATION_DELTA.md` | Proposed interpretation | `53bceb1a59d508cc000583bdec062b136cb83869d0d6bd6027a2b83404fa83ac` |
| `sources/integration-deltas/SAGE_v0.8_CLAUDE_PROMPT_PACK_INTEGRATION_DELTA.md` | Proposed interpretation | `dcb1e468d8067811dcabaa870a66b7e966a641cf10d6bef02aea8f17aea856b5` |
| `sources/integration-deltas/SAGE_v0.8_VIBE_MASTER_PROMPT_INTEGRATION_DELTA.md` | Proposed interpretation | `3f779a7387fb459f1c63caa8ebc924ea5c95c78f1ea18c00e02063c7f083c8e5` |
| `sources/integration-deltas/SAGE_v0.8_STRIX_SECURITY_INTEGRATION_DELTA.md` | Proposed interpretation | `7a048ceb92d35d84b7e16ee4570f0665d3023f5d0eab5b9aee3e07cb258fcf52` |
| `sources/integration-deltas/SAGE_v0.8_ARCHITECTURE_MODELING_DIAGRAM_AS_CODE_FINAL_DELTA.md` | Consolidated architecture/diagram proposal | `b5fb69d1d3edf6a566cbaf6de7ca534cb83adb304f7a9b3797572e1549a247d8` |

Deltaها Authority مستقل نیستند. نتیجهٔ پذیرش، تعدیل یا رد هر پیشنهاد در `reviews/SAGE_v0.8_SOURCE_INTEGRATION_AUDIT.md` ثبت می‌شود.

Formalization در 2026-09-09 با تأیید صریح کاربر ثبت شد؛ Draftهای پیشین در `history/` نگهداری می‌شوند و قابل overwrite نیستند.

## ۴. مشتق تاریخی

| Archived source | Classification | SHA-256 |
|---|---|---|
| `sources/legacy-derived/SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT_v0.8.0-draft.1.md` | Superseded derived draft; non-authoritative | `af3e91a4f1cd8a24afe4ade36c1797e975c3a77228a78f05456e42a782fe7962` |

## ۵. Upstream: GitHub Spec Kit

- Repository: `https://github.com/github/spec-kit`
- Pinned commit: `4a7341a93d944d6efe153b71da4a1adb9c2b578c`
- Snapshot date: 2026-09-06
- License snapshot: `sources/upstream/spec-kit/LICENSE`
- Role: pattern source; never a runtime dependency of SAGE core

Selected snapshots:

- `README.md`
- `workflows/README.md`, `workflows/ARCHITECTURE.md`, `workflows/speckit/workflow.yml`
- `extensions/README.md`, `extensions/EXTENSION-USER-GUIDE.md`
- `extensions/bug/extension.yml`, `extensions/assess/extension.yml`
- `extensions/agent-context/README.md`
- `presets/README.md`, `presets/ARCHITECTURE.md`
- `docs/reference/bundles.md`

Accepted generalized ideas include explicit clarification, cross-artifact analysis, convergence, composable workflow packages, priority resolution, dry-run transparency, pinned sources and ownership-aware removal. Product-specific commands and file layouts remain informative only.

## ۶. Upstream: Strix

- Repository: `https://github.com/usestrix/strix`
- Pinned commit: `ff5c8cc8e46d8e60c2bc2439f7bcb07c05ca3db2`
- Pinned tag at snapshot: `v1.6.2`
- Snapshot date: 2026-09-06
- License snapshot: `sources/upstream/strix/LICENSE`
- Role: optional Authorized Security Validation adapter; not SAGE core

Selected snapshots:

- `README.md`, `AGENTS.md`, `pyproject.toml`, `scripts/install.sh`
- `docs/quickstart.mdx`, `docs/advanced/skills.mdx`
- `docs/integrations/coding-agents.mdx`, `docs/integrations/ci-cd.mdx`

Install state، provider credentials و Docker runtime جزو Authority این Registry نیستند. نصب و اجرای Strix در این Integration انجام نشده و هیچ Target امنیتی اسکن نشده است.

## ۷. Freshness و Update

۱) Snapshot جدید باید Commit/Tag و Hash جدید داشته باشد.  
۲) Update منبع به‌تنهایی Rule فعال را تغییر نمی‌دهد.  
۳) هر تغییر معماری نیازمند Integration Audit تازه و disposition صریح است.  
۴) فایل تاریخی و Hash قدیمی overwrite نمی‌شود.  
۵) Sourceهای دارای License باید همراه License snapshot نگهداری شوند.
