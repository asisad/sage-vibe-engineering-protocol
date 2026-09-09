# SAGE Diagram-as-Code

این پوشه مدل سطح‌بالای معماری SAGE را به‌صورت قابل‌نسخه‌بندی نگه می‌دارد.

The canonical diagram is [`sage-architecture.mmd`](sage-architecture.mmd). It describes the public boundary of SAGE, not a particular application project:

`Intent → Context/Memory → Intake → Discover → Plan → Implement → Verify → Outcome`

The diagram makes four architectural rules visible:

1. Discovery is advisory; it cannot authorize execution.
2. Implementation is constrained by scope, authority and an approved plan.
3. Every stage and adapter returns evidence to the append-only Evidence Ledger.
4. Providers, Tools and Strix are optional adapters behind an explicit approval boundary.
5. Context and Memory are scoped and provenance-aware; they are inputs to Intake, not an authority source.

## Rendering

GitHub renders Mermaid blocks natively; the `.mmd` source can also be rendered with Mermaid CLI or Mermaid Live Editor. Keep the source file as the editable artifact and update the test when a required lifecycle stage or boundary is renamed.

## فارسی

این دیاگرام برای توضیح «SAGE چیست و چگونه کار می‌کند» مناسب است: SAGE یک اپلیکیشن دامنه‌ای نیست؛ یک پروتکل و Runtime برای تبدیل درخواست خام به کار مهندسیِ قابل‌بررسی، قابل‌آزمون و دارای شواهد است.
