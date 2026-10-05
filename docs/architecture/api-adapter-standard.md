# SAGE API and Adapter Standard / استاندارد API و Adapter

Identify the official native capability source and supported API/host versions.
Prefer typed operations; preserve target identity, scope, permission, authority
and evidence during mapping. Serialize only allowlisted fields, redact secrets
and reject unsupported versions instead of silently coercing them.

Adapters MUST document input/output schemas, native-to-portable error mapping,
timeout/cancellation and idempotency behavior. Record unsupported operations
and loss of semantics. Select a thin bridge only where host/thread/transport
constraints require it. A direct API binding is valid.

CI validates schemas, compatibility, failure paths and packaging. Actual
transport and host smoke receipts are required before a live integration can
claim conformance. Registration and descriptor Booleans alone are not proof.

API بومی مسئول قابلیت نرم‌افزار است؛ Adapter نگاشت آن به قرارداد SAGE را
انجام می‌دهد. نسخهٔ پشتیبانی‌نشده، حذف محدودیت و خطای بدون معنی روشن باید
رد یا با محدودیت صریح گزارش شود. شواهد reference جای آزمون اتصال واقعی را نمی‌گیرد.
