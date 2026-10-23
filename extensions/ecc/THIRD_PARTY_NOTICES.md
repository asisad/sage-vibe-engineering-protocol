# Third-party source notices

This extension includes unmodified source material from **Affaan Mustafa and
ECC contributors**, repository `https://github.com/affaan-m/ECC`, commit
`90606c8315ee09cafc303515c5f33024db6b9882` (version 2.2.3).

The source tree under `sources/upstream/ecc/` is attributed upstream material,
not original SAGE skill content. SAGE adds catalog metadata, mappings, policy
envelopes, an offline loader and tests. No affiliation or endorsement is implied.

## Scope-specific licenses

- The upstream root license is MIT; its complete text and copyright notice are
  retained at `sources/upstream/ecc/LICENSE`.
- Eight skills declare **Apache-2.0** in their original frontmatter:
  `carrier-relationship-management`, `customs-trade-compliance`,
  `energy-procurement`, `inventory-demand-planning`,
  `logistics-exception-management`, `production-scheduling`,
  `quality-nonconformance`, and `returns-reverse-logistics`.
  A copy of the standard license is provided in `licenses/Apache-2.0.txt`.
- `osint-investigation` explicitly declares **CC-BY-SA-4.0**. Its original
  attribution section and complete `LICENSE.txt` remain inside that skill's
  source directory. It is **not relabeled MIT**.
- `taste-application` contains its own `SOURCE.md` and
  `scripts/LICENSE`; both are retained with the resources they describe.

`catalog.json` records each ECC entry's declared license, falling back to the
upstream root MIT only where the entry has no local declaration. This is a
source attribution record, not a certification of every external dependency.
External tools, models, paid services and separately installed packages keep
their own licenses, terms and access requirements.

Preserve these notices, skill-local attribution and complete license texts
when redistributing source packets. The inventory lock records source hashes
so changes and updates can be reviewed separately from upstream originals.
