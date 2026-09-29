# Source Rights Gate

Being able to open a webpage does not establish permission to collect its full text, retain it, or publish a summary. This tool keeps source selection, rights review, operational enablement, and intended use separate. Each query returns an explicit allow/deny result with reasons, making it a small **auditable configuration gate** before a collection workflow.

[中文说明](README.zh-CN.md) · [Bilingual home](README.md)

## Problems it addresses

- A single vague `allowed=true` no longer stands for collection, storage, and public display at once.
- Pending, rejected, or disabled sources cannot be used merely because they appear in a registry.
- Internal and public use are evaluated separately; public use needs explicit review and display fields.
- Inconsistent configuration fails early, including duplicate IDs, non-HTTPS URLs, and enabled sources without approved review.

## Start in 30 seconds

Use Python 3.9 or newer; no third-party packages are needed. From this folder:

```bash
# Validate the complete registry
python3 rights_gate.py examples/sources.json

# Ask whether a source may expose title, link, and summary publicly
python3 rights_gate.py examples/sources.json \
  --source fictional-public --environment public --purpose public

# Explain why an internal source is denied for public use
python3 rights_gate.py examples/sources.json \
  --source fictional-internal --environment public --purpose public
```

An example query response:

```json
{
  "source_id": "fictional-internal",
  "environment": "public",
  "purpose": "public",
  "allowed": false,
  "reasons": ["environment_not_enabled", "public_review_required"]
}
```

The real response may contain additional denial reasons. Automation can consume `allowed` and `reasons` directly.

## Registry format and rules

See the [fictional source registry](examples/sources.json). Each source has:

| Field | Purpose |
| --- | --- |
| `id`, `name`, `feed_url` | Identity and HTTPS feed; IDs and URLs must be unique |
| `selection` | `accepted`, `pending`, or `rejected` |
| `rights.review_status` | `pending`, `approved_internal`, `approved_public`, or `rejected` |
| `rights.fetch_metadata` | Permission to fetch metadata |
| `rights.fetch_fulltext`, `rights.store_fulltext` | Separate permissions to fetch and retain full text; both are needed for full-text use |
| `rights.summarize` | Permission to prepare summaries |
| `rights.public_title_link`, `rights.public_summary` | Separate public display permissions |
| `operations.enabled`, `operations.environments` | Operational switch and internal/public scope |

The purposes are `metadata`, `fulltext`, `summary`, and `public`; environments are `internal` and `public`. A use is allowed only if the source is accepted, review is approved, operations are enabled for that environment, and every permission for the purpose is true. The `public` purpose requires permissions for metadata, summarizing, public title and link, and public summary, plus `approved_public` review and the public environment.

`review_status` is **a conclusion entered by your organization**. The program cannot inspect website terms, copyright, or contracts, and it never infers permission from a domain. The `fictional-*` entries are policy fixtures, not real grants of rights.

## Put it in your workflow

1. Copy the JSON example into a local registry and replace it with records that have actually been reviewed.
2. Validate the whole file without `--source`, then query the exact environment and purpose of each planned use.
3. Proceed only when `allowed=true`; send denial reasons to the responsible reviewer.
4. Keep fact checking, sensitivity review, and editorial approval as separate steps for public material.

Exit code `0` means valid/allowed, `1` means an explicit denial, and `2` means an invalid file or registry. These codes can gate CI or a batch job.

## Privacy and release boundary

The program reads local JSON only. It does not crawl sites, send network requests, or log credentials. Public samples use reserved example domains and fictional review states; there are no real source lists, operational records, contracts, internal addresses, or keys. Do not commit actual rights-review evidence to a public repository.

This standalone project has no business repository history. It is released under the [Apache-2.0 license](LICENSE) at [workstonedai-collab/source-rights-gate](https://github.com/workstonedai-collab/source-rights-gate). Your source and rights owners must still approve any real-world policy entries.
