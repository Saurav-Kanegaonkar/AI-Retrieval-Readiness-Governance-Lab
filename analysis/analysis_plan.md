# Analysis Plan

## Objective

Assess whether AI-consumed datasets, documents, and knowledge assets are fresh, governed, well-described, semantically labeled, and retrieval-ready for risk-assessment workflows.

## Stakeholder Questions

1. Which sources and assets can be included in retrieval scenarios with low readiness risk?
2. Which assets should be excluded or conditionally included until governance, freshness, metadata, or lineage gaps are fixed?
3. Which remediation categories create the highest operational exposure?
4. Which metrics should a data steward, product team, or governance partner monitor weekly?

## Control Framework

The lab uses six readiness controls:

- Freshness SLA compliance: `days_since_refresh <= expected_refresh_days`.
- Metadata completeness: metadata score at or above 80.
- Semantic labeling coverage: approved or reviewable semantic labels.
- Ownership and lineage documentation: owner present and lineage documented.
- Governance compliance: classification within policy, aligned access control, and aligned retention.
- Retrieval quality: structured content, low ambiguity, and clear risk-decision signal.

## EDA Coverage

The script reviews:

- Source and asset distribution by domain and source type.
- Freshness distribution relative to source SLAs.
- Metadata completeness and missing-owner patterns.
- Semantic-label coverage and missing-label exceptions.
- Classification, access-control, and retention failures.
- Lineage documentation coverage.
- Remediation issue mix, severity, exposure points, and target cycle time.

## Outputs

- `analysis/outputs/readiness_metrics.json`
- `analysis/outputs/source_readiness_scores.csv`
- `analysis/outputs/source_remediation_priorities.csv`
- `analysis/outputs/issue_type_summary.csv`
- `analysis/outputs/remediation_queue_ranked.csv`
- `analysis/outputs/generated_executive_summary.md`
- `docs/images/readiness_control_heatmap.png`
- `docs/images/remediation_exposure_by_issue.png`
- `docs/images/retrieval_inclusion_decisions.png`
- `docs/images/lowest_readiness_sources_table.png`

## Decision Rule

Assets pass as AI-ready only when the source is approved and active, the asset is included for retrieval, and the composite readiness score meets the threshold. Assets with governance review requirements should be blocked or conditionally excluded before retrieval use.

## Caveats

This is a synthetic analysis lab. The metrics demonstrate readiness reasoning and repeatable controls, not real RELX or LexisNexis Risk Solutions operational performance.
