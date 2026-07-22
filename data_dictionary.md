# Data Dictionary

All tables are synthetic and represent realistic AI data-readiness governance patterns for risk, identity, fraud, compliance, and case-support workflows.

## `data/approved_ai_sources.csv`

| Field | Description |
|---|---|
| `source_id` | Unique approved-source style identifier. |
| `source_name` | Human-readable source name. |
| `domain` | Risk workflow domain represented by the source. |
| `source_type` | Source format, such as warehouse table, document repository, API, or curated knowledge base. |
| `approved_for_ai` | Whether the source is approved for AI use scenarios. |
| `criticality` | Business criticality used to prioritize remediation. |
| `business_owner` | Accountable business stewardship group. |
| `technical_owner` | Technical owner or platform team. |
| `expected_refresh_days` | Freshness SLA in days. |
| `max_allowed_classification` | Highest content classification allowed for this source's retrieval use. |
| `retention_policy_days` | Retention expectation used by governance checks. |
| `source_contract_status` | Active, pending review, or deprecated source status. |
| `ai_use_case` | AI retrieval or copilot use case supported by the source. |

## `data/knowledge_assets.csv`

| Field | Description |
|---|---|
| `asset_id` | Unique knowledge-asset identifier. |
| `source_id` | Parent source identifier. |
| `asset_title` | Synthetic title of the dataset, document, article, runbook, or template. |
| `asset_type` | Asset format. |
| `domain` | Risk workflow domain. |
| `ai_retrieval_candidate` | Whether the asset is a candidate for retrieval inclusion. |
| `included_in_retrieval` | Whether the asset is currently included in the retrieval corpus. |
| `business_description_present` | Whether the business description exists. |
| `metadata_owner_present` | Whether a metadata owner is documented. |
| `lineage_documented` | Whether upstream lineage is documented. |
| `last_refreshed_at` | Last refresh date. |
| `classification` | Asset-level classification. |
| `access_control_status` | Access-control alignment status. |
| `retention_status` | Retention alignment status. |
| `semantic_label` | Retrieval category or semantic label. |
| `document_structure_score` | Synthetic content hygiene score from 0 to 1. |
| `retrieval_ambiguity_score` | Synthetic ambiguity score from 0 to 1; lower is better. |
| `risk_decision_signal` | Whether the asset has high, medium, low, or unclear decision signal. |
| `consumer_team` | Downstream team using or evaluating the asset. |
| `days_since_refresh` | Calculated age at the July 22, 2026 snapshot. |

## `data/metadata_reviews.csv`

| Field | Description |
|---|---|
| `review_id` | Unique metadata review identifier. |
| `asset_id` | Reviewed asset. |
| `business_description_quality` | Clear, partial, or missing description status. |
| `field_dictionary_status` | Complete, partial, or missing field dictionary status. |
| `semantic_label_status` | Approved, needs review, or missing semantic label status. |
| `ownership_status` | Documented or missing owner status. |
| `lineage_status` | Documented, partial, or missing lineage status. |
| `metadata_completeness_score` | Composite metadata score from 0 to 100. |
| `reviewed_at` | Review date. |

## `data/governance_policy_checks.csv`

| Field | Description |
|---|---|
| `policy_check_id` | Unique governance policy check identifier. |
| `asset_id` | Checked asset. |
| `classification` | Asset classification. |
| `source_max_allowed_classification` | Maximum allowed classification under the source policy. |
| `classification_within_source_policy` | Whether the asset classification is permitted by source policy. |
| `access_control_status` | Access alignment status. |
| `retention_status` | Retention alignment status. |
| `retention_policy_days` | Source retention requirement. |
| `contains_sensitive_tokens` | Synthetic sensitive-token flag. |
| `governance_pass` | Combined classification, access, and retention pass flag. |
| `review_required_before_retrieval` | Whether retrieval use should wait for governance review. |

## `data/lineage_edges.csv`

| Field | Description |
|---|---|
| `lineage_edge_id` | Unique lineage edge identifier. |
| `asset_id` | Asset with an upstream/downstream relationship. |
| `upstream_system` | Synthetic upstream system. |
| `transformation_owner` | Team owning the transformation. |
| `downstream_ai_surface` | AI surface consuming the asset. |
| `lineage_certified` | Whether lineage is certified. |
| `last_lineage_review_at` | Last lineage review date. |

## `data/remediation_queue.csv`

| Field | Description |
|---|---|
| `issue_id` | Unique remediation issue identifier. |
| `asset_id` | Asset requiring remediation. |
| `source_id` | Parent source. |
| `domain` | Risk workflow domain. |
| `issue_type` | Freshness, metadata, semantic label, lineage/owner, governance, or retrieval ambiguity gap. |
| `severity` | P1, P2, or P3 priority. |
| `included_in_retrieval` | Whether the asset is already included. |
| `estimated_risk_exposure_points` | Synthetic exposure score for prioritization. |
| `recommended_action` | Recommended remediation action. |
| `target_owner` | Suggested owner group. |
| `cycle_time_target_days` | Target remediation cycle time. |
| `status` | Current synthetic issue status. |
