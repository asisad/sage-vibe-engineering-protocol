# SAGE CLI Standard

An approved CLI MUST provide stable command names, deterministic exit codes,
`--json` output, machine-readable errors, `version`, help metadata, timeout
behavior and request/correlation IDs for remote calls. Risky mutations MUST
support dry-run. The portable shape is:

```text
<tool> <domain> <action> [options]
```

JSON output MUST identify `schema_version`, `request_id`, `status` and either
`result` or a typed `error`. Secrets never appear in output or receipts.
