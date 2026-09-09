# SAGE Infographic Handoff — فارسی / English

این بریف برای تحویل مستقیم به طراح اینفوگرافی آماده شده است. هدف، توضیح **روش و معماری SAGE** است؛ نه تبلیغ یک اپلیکیشن یا نمایش نتیجهٔ Scan امنیتی.

## فارسی — بریف طراحی

### پیام اصلی

**SAGE: تبدیل Vibe Coding به Vibe Engineering قابل‌ردیابی**

زیرعنوان: «از ایدهٔ خام تا طرح، اجرا و راستی‌آزمایی؛ با Scope، Gate، Skill، Tool و Evidence.»

### دیاگرام اصلی پیشنهادی

یک جریان افقی یا دایره‌ای با هفت ایستگاه بسازید:

```text
درخواست / Intent
  ↓
Intake: فهم هدف و ریسک
  ↓
Discover: پیدا کردن Skill و Tool
  ↓
Plan: معماری، Scope و Approval
  ↓
Implement: اجرای کنترل‌شده
  ↓
Verify: تست و شواهد
  ↓
DONE | BLOCKED | ESCALATED
```

### هستهٔ مرکزی

در مرکز یا پشت جریان، سه لایه نمایش داده شود:

۱) **Workflow State Machine** — ترتیب مرحله‌ها و انتقال مجاز را کنترل می‌کند.

۲) **Authority & Scope Gates** — توانایی با مجوز یکی نیست؛ هیچ Tool یا Provider بدون Scope و Approval اجرا نمی‌شود.

۳) **Evidence Ledger** — تصمیم‌ها، ورودی‌ها، خروجی‌ها، تست‌ها و provenance را ثبت و قابل‌ردیابی می‌کند.

### لایهٔ اتصال‌ها

در کنار هسته، یک مرز جدا با برچسب `External Adapters — Opt-in` قرار دهید:

- `Providers`
- `Tools`
- `Agent / Skill Registry`
- `Strix Security Adapter`

با یک خط‌چین نشان دهید که این‌ها «قابل اتصال» هستند، اما بخشی از Authority هسته نیستند. Strix فقط Adapter امنیتی اختیاری است و اجرای Live آن Target، Scope، Approval، Review و شواهد مستقل می‌خواهد.

### وضعیت‌ها و رنگ‌ها

- آبی: هسته و Workflow
- زرد: Gate، Scope و Approval
- سبز: Evidence و Verify
- بنفش: Adapterهای بیرونی
- قرمز فقط برای `BLOCKED` و هشدار؛ نه برای تزئین

### متن‌های کوتاه قابل استفاده

- «Discover پیشنهاد می‌دهد؛ مجوز نمی‌دهد.»
- «Implement فقط پس از Plan تأییدشده.»
- «هر نتیجه باید Evidence داشته باشد.»
- «Live execution پیش‌فرض خاموش است.»
- «DONE یعنی شواهد کافی؛ نه صرفاً تولید کد.»

### منابعی که طراح باید ببیند

- `README.md` برای معرفی عمومی
- `SAGE_v0.8_EXECUTION_PROTOCOL_AND_SKILL_CONTRACT.md` برای قرارداد معماری
- `docs/diagrams/sage-architecture.mmd` به‌عنوان منبع دیاگرام قابل‌ویرایش
- `skills/registry.json` برای ترتیب Skillها
- `docs/QUICKSTART.fa-en.md` برای متن راه‌اندازی دو‌زبانه

خروجی پیشنهادی: یک پوستر افقی 16:9، نسخهٔ عمودی 9:16 و فایل ویرایش‌پذیر SVG/Figma. متن فارسی و انگلیسی را در دو بلوک هم‌تراز نگه دارید و از اضافه‌کردن ادعای «امنیت تضمین‌شده» خودداری کنید.

## English — design brief

### Main message

**SAGE: turning vibe coding into traceable vibe engineering**

Subtitle: “From intent to plan, implementation and verification—with scope, gates, skills, tools and evidence.”

### Primary visual

Show this controlled flow as the main horizontal or circular path:

```text
Intent → Intake → Discover → Plan → Implement → Verify → DONE / BLOCKED / ESCALATED
```

Place the Workflow State Machine, Authority & Scope Gates, and Evidence Ledger as the control layer behind the flow. Add an `External Adapters — Opt-in` boundary containing Providers, Tools, Agent/Skill Registry and the optional Strix Security Adapter.

Make the following distinctions visually explicit:

- capability discovery does not grant authority;
- implementation requires an approved plan;
- verification is evidence-based;
- live execution is off by default;
- Strix is an optional security adapter, not a core dependency.

Use blue for core runtime, yellow for gates, green for evidence, purple for external adapters, and red only for blocked or warning states. Deliver editable source plus 16:9, 9:16 and SVG/Figma exports. Do not add claims that SAGE or a partial security scan guarantees safety.

