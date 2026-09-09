# Read-Only Task Extract — پلن ورک‌فلو طراحی داخلی AI

Status: INFERRED / PROPOSED — not an approved product specification  
Source task: `پلن ورک‌فلو طراحی داخلی AI`  
ChatGPT task id: `6a986ec1-0478-83ed-9290-8eebff83dae4`  
Extraction date: 2026-09-09  
Authority: read-only task observation; no mutation of the source task

## ۱. هدف محصول استخراج‌شده

یک سیستم حرفه‌ای برای طراحی و اجرای دکوراسیون داخلی، با تمرکز بر پروژه‌های مشتری، آشپزخانه و کابینت، که از ورودی‌های عکس/پلان/اندازه/متریال به خروجی قابل‌ساخت برسد؛ نه صرفاً تولید تصویر زیبا.

خروجی مورد انتظار:

`Design Intent + Geometry + Dimensions + Materials + Objects + BOM/Cut List + Revision/Approval`

## ۲. نیازمندی‌های دامنه

- پروندهٔ Customer/Project/Site/Room و چند فضای مستقل
- Survey شامل عکس، Scan، Measurement و Existing Geometry
- Inspiration Board و Design Constraint Board با وضعیت‌های `Locked / Preferred / Flexible / Excluded`
- Material/Product Library
- Design Variants و Selected Design
- BIM/Geometry، BOM و Production
- حفظ عناصر ثابت و تفکیک عناصر قابل‌تغییر
- خروجی مقیاس‌دار و پارامتریک برای ساخت، نه فقط Render

## ۳. تصمیم معماری استخراج‌شده

مدل مرکزی باید CDM (Canonical Domain Model) باشد و هیچ موتور سه‌بعدی Source of Truth نباشد:

```text
CAD/BIM + AI Core + 3D Runtime
            ↓
           CDM
            ↓
  Geometry / BIM / Render / Production adapters
```

نقش پیشنهادی لایه‌ها:

- OCCT/FreeCAD: Geometry/CAD core candidate
- IfcOpenShell/Bonsai: IFC/BIM candidate
- Blender: Render/procedural worker candidate
- Godot/O3DE/Unreal/Unity: 3D Runtime/interactive visualization adapters
- ChatGPT/Claude/Codex: Design Director/Orchestrator، نه CAD source of truth

## ۴. تصمیم‌های مثبت و محدودیت‌ها

- 3D Engine نباید هستهٔ مهندسی باشد؛ فقط Runtime/Visualization adapter است.
- LikeC4/Structurizr و SAGE Architecture Model باید منبع مدل معماری باشند؛ تصویر خروجی منبع حقیقت نیست.
- انتخاب قطعی Kernel، Runtime و Provider به Code Audit اجرایی، License Review و Vertical Slice وابسته است.
- استفاده از پروژه‌های Open Source باید با حکم `REUSE / FORK / EMBED / REFERENCE_ONLY` و بررسی License انجام شود.
- اتصال API/MCP، تغییر هندسه، تولید BOM و Render باید Gate و Evidence مستقل داشته باشد.

## ۵. Vertical Slice پیشنهادی برای اعتبارسنجی

```text
New Project
→ Room 4×3
→ Wall/Door/Window
→ Add Base Cabinet
→ Change Dimensions
→ Apply MDF Material
→ Generate BOM/Cut List
→ Render
```

## ۶. نگاشت به SAGE

| نیاز Task | قرارداد SAGE |
|---|---|
| Customer/Project/Room | Domain Model + Scope |
| Locked/Preferred/Flexible/Excluded | Constraint Contract |
| CDM و Adapterها | Architecture Model + Provider Adapter |
| تغییر پارامتریک | Architecture Delta + Mutation Boundary |
| BOM/Cut List | Acceptance + Evidence |
| انتخاب موتور/سورس | Decision Record + License Gate |
| پلان تا Runtime | Workflow Package + Convergence |

## ۷. مواردی که هنوز Approved نیستند

- انتخاب نهایی CAD Kernel و 3D Runtime
- اتصال زنده به Revit/Planner/Blender یا MCP خارجی
- License clearance برای هر dependency
- Benchmark واقعی روی Windows
- قرارداد کامل CDM و schema دامنهٔ داخلی
- Vertical Slice اجرایی با geometry واقعی

این فایل فقط استخراج Read-Only است. هیچ نتیجهٔ آن بدون Review و Approval به مدل Approved تبدیل نمی‌شود.
