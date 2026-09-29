"""Offline, fail-closed checks for a source-use permission registry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

PURPOSES = ("metadata", "fulltext", "summary", "public")
ENVIRONMENTS = ("internal", "public")
REVIEW_STATUSES = ("pending", "approved_internal", "approved_public", "rejected")
RIGHTS_FIELDS = (
    "fetch_metadata", "fetch_fulltext", "store_fulltext", "summarize",
    "public_title_link", "public_summary",
)


def _object(value: object, allowed: set[str], where: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{where} must be an object")
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"{where} has unknown fields: {', '.join(sorted(unknown))}")
    return value


def validate_registry(payload: object) -> list[dict]:
    root = _object(payload, {"sources"}, "registry")
    if not isinstance(root.get("sources"), list):
        raise ValueError("registry.sources must be a list")
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for index, raw in enumerate(root["sources"], 1):
        where = f"sources[{index}]"
        source = _object(raw, {"id", "name", "feed_url", "selection", "rights", "operations"}, where)
        for key in ("id", "name", "feed_url"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                raise ValueError(f"{where}.{key} must be a non-empty string")
        url = urlsplit(source["feed_url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError(f"{where}.feed_url must be a plain HTTPS URL")
        if source["id"] in seen_ids:
            raise ValueError(f"duplicate source id: {source['id']}")
        if source["feed_url"] in seen_urls:
            raise ValueError(f"duplicate feed URL: {source['feed_url']}")
        seen_ids.add(source["id"])
        seen_urls.add(source["feed_url"])
        if source.get("selection") not in {"accepted", "pending", "rejected"}:
            raise ValueError(f"{where}.selection is invalid")
        rights = _object(source.get("rights"), set(RIGHTS_FIELDS) | {"review_status"}, f"{where}.rights")
        if rights.get("review_status") not in REVIEW_STATUSES:
            raise ValueError(f"{where}.rights.review_status is invalid")
        for key in RIGHTS_FIELDS:
            if type(rights.get(key)) is not bool:
                raise ValueError(f"{where}.rights.{key} must be a boolean")
        operations = _object(source.get("operations"), {"enabled", "environments"}, f"{where}.operations")
        if type(operations.get("enabled")) is not bool:
            raise ValueError(f"{where}.operations.enabled must be a boolean")
        envs = operations.get("environments")
        if not isinstance(envs, list) or len(envs) != len(set(map(str, envs))) or any(env not in ENVIRONMENTS for env in envs):
            raise ValueError(f"{where}.operations.environments must be a unique list of internal/public")
        if operations["enabled"] and source["selection"] != "accepted":
            raise ValueError(f"{where}: only accepted sources may be enabled")
        if operations["enabled"] and rights["review_status"] not in {"approved_internal", "approved_public"}:
            raise ValueError(f"{where}: enabled sources need an approved rights review")
        if "public" in envs and rights["review_status"] != "approved_public":
            raise ValueError(f"{where}: public environment needs approved_public review")
        if rights["store_fulltext"] and not rights["fetch_fulltext"]:
            raise ValueError(f"{where}: storing fulltext requires fetch_fulltext")
        if rights["public_summary"] and not rights["summarize"]:
            raise ValueError(f"{where}: public_summary requires summarize")
    return root["sources"]


def evaluate(source: dict, environment: str, purpose: str) -> dict:
    if environment not in ENVIRONMENTS or purpose not in PURPOSES:
        raise ValueError("unknown environment or purpose")
    reasons = []
    rights, operations = source["rights"], source["operations"]
    if source["selection"] != "accepted":
        reasons.append("source_not_accepted")
    if not operations["enabled"]:
        reasons.append("source_disabled")
    if environment not in operations["environments"]:
        reasons.append("environment_not_enabled")
    if rights["review_status"] not in {"approved_internal", "approved_public"}:
        reasons.append("rights_not_approved")
    if environment == "public" and rights["review_status"] != "approved_public":
        reasons.append("public_review_required")
    required = {
        "metadata": ("fetch_metadata",),
        "fulltext": ("fetch_fulltext", "store_fulltext"),
        "summary": ("summarize",),
        "public": ("fetch_metadata", "summarize", "public_title_link", "public_summary"),
    }[purpose]
    for field in required:
        if not rights[field]:
            reasons.append(f"permission_missing:{field}")
    if purpose == "public" and (environment != "public" or rights["review_status"] != "approved_public"):
        reasons.append("public_purpose_requires_public_review_and_environment")
    return {"source_id": source["id"], "environment": environment, "purpose": purpose, "allowed": not reasons, "reasons": reasons}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and query an offline source-rights registry")
    parser.add_argument("registry", type=Path, help="JSON registry path")
    parser.add_argument("--source", help="source id to evaluate (otherwise validate all)")
    parser.add_argument("--environment", choices=ENVIRONMENTS, default="internal")
    parser.add_argument("--purpose", choices=PURPOSES, default="metadata")
    args = parser.parse_args(argv)
    try:
        sources = validate_registry(json.loads(args.registry.read_text(encoding="utf-8")))
        if args.source:
            source = next((item for item in sources if item["id"] == args.source), None)
            if source is None:
                raise ValueError(f"unknown source id: {args.source}")
            result = evaluate(source, args.environment, args.purpose)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["allowed"] else 1
        print(f"Valid registry: {len(sources)} sources")
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
