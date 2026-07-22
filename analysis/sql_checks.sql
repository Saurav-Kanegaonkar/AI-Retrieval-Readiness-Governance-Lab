-- AI Retrieval Readiness Governance Lab
-- SQL checks are written in portable analytical SQL style. Table names assume
-- the CSVs have been loaded as approved_ai_sources, knowledge_assets,
-- metadata_reviews, governance_policy_checks, lineage_edges, and remediation_queue.

-- 1. Source-level freshness SLA compliance.
SELECT
  s.domain,
  COUNT(*) AS asset_count,
  SUM(CASE WHEN a.days_since_refresh <= s.expected_refresh_days THEN 1 ELSE 0 END) AS freshness_pass_count,
  ROUND(1.0 * SUM(CASE WHEN a.days_since_refresh <= s.expected_refresh_days THEN 1 ELSE 0 END) / COUNT(*), 3) AS freshness_sla_compliance
FROM knowledge_assets a
JOIN approved_ai_sources s
  ON a.source_id = s.source_id
GROUP BY s.domain
ORDER BY freshness_sla_compliance ASC;

-- 2. Metadata and business-description completeness.
SELECT
  a.domain,
  COUNT(*) AS asset_count,
  AVG(m.metadata_completeness_score) AS avg_metadata_score,
  SUM(CASE WHEN m.metadata_completeness_score >= 80 THEN 1 ELSE 0 END) AS metadata_pass_count,
  SUM(CASE WHEN a.business_description_present = FALSE THEN 1 ELSE 0 END) AS missing_business_description_count
FROM knowledge_assets a
JOIN metadata_reviews m
  ON a.asset_id = m.asset_id
GROUP BY a.domain
ORDER BY avg_metadata_score ASC;

-- 3. Semantic labeling and categorization coverage.
SELECT
  domain,
  COUNT(*) AS asset_count,
  SUM(CASE WHEN semantic_label IS NOT NULL AND semantic_label <> '' THEN 1 ELSE 0 END) AS labeled_asset_count,
  ROUND(1.0 * SUM(CASE WHEN semantic_label IS NOT NULL AND semantic_label <> '' THEN 1 ELSE 0 END) / COUNT(*), 3) AS semantic_label_coverage
FROM knowledge_assets
GROUP BY domain
ORDER BY semantic_label_coverage ASC;

-- 4. Classification, access-control, and retention compliance.
SELECT
  a.domain,
  COUNT(*) AS asset_count,
  SUM(CASE WHEN p.governance_pass = TRUE THEN 1 ELSE 0 END) AS governance_pass_count,
  SUM(CASE WHEN p.review_required_before_retrieval = TRUE THEN 1 ELSE 0 END) AS review_required_count,
  SUM(CASE WHEN p.access_control_status <> 'aligned' THEN 1 ELSE 0 END) AS access_exception_count,
  SUM(CASE WHEN p.retention_status <> 'aligned' THEN 1 ELSE 0 END) AS retention_exception_count
FROM knowledge_assets a
JOIN governance_policy_checks p
  ON a.asset_id = p.asset_id
GROUP BY a.domain
ORDER BY review_required_count DESC;

-- 5. Ownership and lineage documentation coverage.
SELECT
  a.domain,
  COUNT(*) AS asset_count,
  SUM(CASE WHEN a.metadata_owner_present = TRUE AND a.lineage_documented = TRUE THEN 1 ELSE 0 END) AS owner_lineage_pass_count,
  ROUND(1.0 * SUM(CASE WHEN a.metadata_owner_present = TRUE AND a.lineage_documented = TRUE THEN 1 ELSE 0 END) / COUNT(*), 3) AS owner_lineage_coverage
FROM knowledge_assets a
GROUP BY a.domain
ORDER BY owner_lineage_coverage ASC;

-- 6. Retrieval inclusion/exclusion candidates.
SELECT
  a.domain,
  CASE
    WHEN s.approved_for_ai = TRUE
      AND s.source_contract_status = 'active'
      AND a.included_in_retrieval = TRUE
      AND p.governance_pass = TRUE
      AND m.metadata_completeness_score >= 80
      AND a.days_since_refresh <= s.expected_refresh_days
    THEN 'include'
    WHEN p.review_required_before_retrieval = TRUE
    THEN 'exclude_until_review'
    ELSE 'conditional_include'
  END AS retrieval_decision,
  COUNT(*) AS asset_count
FROM knowledge_assets a
JOIN approved_ai_sources s
  ON a.source_id = s.source_id
JOIN governance_policy_checks p
  ON a.asset_id = p.asset_id
JOIN metadata_reviews m
  ON a.asset_id = m.asset_id
GROUP BY a.domain, retrieval_decision
ORDER BY a.domain, asset_count DESC;

-- 7. Ranked remediation queue for weekly steward review.
SELECT
  issue_type,
  severity,
  target_owner,
  COUNT(*) AS issue_count,
  SUM(estimated_risk_exposure_points) AS exposure_points,
  AVG(cycle_time_target_days) AS avg_cycle_time_target_days
FROM remediation_queue
WHERE status <> 'resolved'
GROUP BY issue_type, severity, target_owner
ORDER BY exposure_points DESC, issue_count DESC;
