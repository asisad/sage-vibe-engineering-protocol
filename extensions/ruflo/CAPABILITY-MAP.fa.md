# Ruflo × SAGE/ECC — ماتریس همپوشانی و تصمیم فنی

مبنای بررسی: SAGE master 21b5ad7، ECC 90606c8، Ruflo tag v3.61.1 e6c3743 (2026-10-24). این ماتریس طبقه‌بندی حوزه‌هاست نه تأیید خط‌به‌خط همه فایل‌های upstream؛ تصمیم قطعی هر tool پس از discovery و آزمون نسخه‌دار گرفته می‌شود.

| حوزه Ruflo | همپوشانی با SAGE/ECC | تصمیم | مقصد و شرط فعال‌سازی |
|---|---|---|---|
| Swarm coordination | قرارداد orchestration و Agent | ENHANCE | Ruflo MCP adapter؛ آزمون چند اجرای واقعی |
| Agent role inventory | 88 پروفایل/نقش کاتالوگ SAGE+ECC | ENHANCE | صرفاً نقشه نقش‌ها، نه شمار Agent فعال |
| Agent execution | SAGE production عمدتاً DRY_RUN | ADD | guarded tools/call و شاهد تغییر فایل |
| Task workflow | SAGE lifecycle و gates | ENHANCE | SAGE مالک state و approval می‌ماند |
| Memory search/store | ECC source و SAGE ledger | ADD | persistence مستقل، backend حقیقی، عدم mock |
| Vector RAG / RuVector | ECC و SAGE context policy | ADD | آزمون کیفیت retrieval و provenance |
| Learning/hook routing | SAGE decision/context و SENS | REFERENCE_ONLY | hooks global و self-edit خاموش |
| Federation / network | SAGE interface + trust policy | REFERENCE_ONLY | identity/auth/secure transport |
| CLI MCP server | استاندارد MCP و schema | ADD | handshake + discovery + receipt |
| Claude Code plugin console | بومی میزبان و نه core SAGE | REFERENCE_ONLY | فقط setup مستقل با بازبینی permissions |
| Codex MCP | SAGE Agent-Native | ENHANCE | بدون فرض برابری تمام hooks |
| Security scanning | SAGE policy و Strix pending | ENHANCE | نتیجه Ruflo معادل اسکن مستقل نیست |
| Browser automation | Tool access contract | ADD_CONDITIONAL | fixture-only؛ production بسته |
| Code review / tests | ECC roles+skills و SAGE Verify | ENHANCE | test receipt مستقل |
| Docs / research agents | ECC Skills و optional technology | ENHANCE | on-demand source packet |
| Benchmarks | SAGE evidence gates | REFERENCE_ONLY | هر benchmark مصنوعی مردود |
| Costs / metrics | SENS integration seam | ADD_CONDITIONAL | sampling، out-of-band |
| Schema/policy models | SAGE core | KEEP_SAGE | ownership SAGE |
| Local workspace mutation | SAGE dry-run پیش‌فرض | ADD_CONDITIONAL | SAGE run contract + OS sandbox |
| GitHub automation | ECC و tool capabilities | ADD_CONDITIONAL | narrower permissions و token |
| AgentDB persistence | حافظه اختصاصی SAGE منتشر نشده | ADD_CONDITIONAL | persist/restart/recovery |
| Background workers | SAGE ندارد | REFERENCE_ONLY | قابلیت توقف، rollback، cost |

**مرز عددی:** Ruflo را مجموعه‌ای از ایجنت‌های مستقلِ تأییدشده فرض نکن؛ فهرست ابزارهای واقعی با tools/list از نسخه نصب‌شده به دست می‌آید. هر نقش ECC مشابه، پیوند enhancement می‌گیرد؛ تعریف تکراری قابلیت جدید نیست.

**ریسک نسخه:** پس از انتشار v3.61.1 اصلاح نمایش synthetic برای ۱۲ worker و لغو worker در main ثبت شده است؛ تا انتشار نسخه جدید نباید آن را به npm v3.61.1 نسبت داد. پاسخ کارگر بدون شواهد مستقل PASS نیست.

منابع:
- https://github.com/ruvnet/ruflo
- https://github.com/ruvnet/ruflo/releases/tag/v3.61.1
- https://github.com/asisad/sage-vibe-engineering-protocol/pull/1
- https://github.com/asisad/sage-vibe-engineering-protocol/blob/master/docs/architecture/mcp-standard.md
