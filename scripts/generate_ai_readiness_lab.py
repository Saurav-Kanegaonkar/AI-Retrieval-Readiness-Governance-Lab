from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "analysis" / "outputs"
IMAGE_DIR = ROOT / "docs" / "images"
AS_OF_DATE = date(2026, 7, 22)
RNG = np.random.default_rng(42)


def choice(values, size=None, p=None):
    return RNG.choice(values, size=size, p=p)


def bounded_int(mean: float, sd: float, low: int, high: int, size: int) -> np.ndarray:
    return np.clip(RNG.normal(mean, sd, size).round().astype(int), low, high)


def save_csv(frame: pd.DataFrame, name: str) -> None:
    frame.to_csv(DATA_DIR / name, index=False)


def build_sources() -> pd.DataFrame:
    domains = [
        "Identity Verification",
        "Fraud Signals",
        "Business Registry",
        "Sanctions Screening",
        "Device Intelligence",
        "Case Operations",
        "Compliance Policy",
        "Customer Risk Notes",
    ]
    systems = ["source_api", "document_repository", "warehouse_table", "curated_knowledge_base", "case_management_export"]
    owners = [
        "Risk Data Stewardship",
        "Identity Products",
        "Fraud Analytics",
        "Compliance Operations",
        "Platform Governance",
        "Customer Operations",
    ]
    rows = []
    for idx in range(96):
        domain = choice(domains)
        source_type = choice(systems, p=[0.21, 0.18, 0.28, 0.21, 0.12])
        approved = choice([True, False], p=[0.84, 0.16])
        criticality = choice(["high", "medium", "low"], p=[0.42, 0.43, 0.15])
        expected_refresh = int(choice([1, 3, 7, 14, 30], p=[0.2, 0.24, 0.3, 0.16, 0.1]))
        max_access = choice(["public_internal", "confidential", "restricted", "regulated_sensitive"], p=[0.18, 0.38, 0.29, 0.15])
        rows.append(
            {
                "source_id": f"SRC-{idx + 1:03d}",
                "source_name": f"{domain} {source_type.replace('_', ' ').title()} {idx + 1:02d}",
                "domain": domain,
                "source_type": source_type,
                "approved_for_ai": approved,
                "criticality": criticality,
                "business_owner": choice(owners),
                "technical_owner": choice(["Data Platform", "Search Platform", "Risk ETL", "Knowledge Systems"]),
                "expected_refresh_days": expected_refresh,
                "max_allowed_classification": max_access,
                "retention_policy_days": int(choice([365, 730, 1095, 1825, 2555], p=[0.18, 0.3, 0.24, 0.18, 0.1])),
                "source_contract_status": choice(["active", "pending_review", "deprecated"], p=[0.81, 0.14, 0.05]),
                "ai_use_case": choice(
                    [
                        "risk_assessment_retrieval",
                        "identity_resolution_support",
                        "fraud_triage_copilot",
                        "compliance_research_assistant",
                        "customer_risk_context",
                    ]
                ),
            }
        )
    return pd.DataFrame(rows)


def build_assets(sources: pd.DataFrame) -> pd.DataFrame:
    asset_types = ["table", "knowledge_article", "policy_document", "runbook", "case_note_template", "faq"]
    classifications = ["public_internal", "confidential", "restricted", "regulated_sensitive"]
    labels = [
        "entity_resolution",
        "identity_verification",
        "fraud_indicator",
        "sanctions_context",
        "device_risk",
        "business_registry",
        "retention_rule",
        "access_policy",
        "case_workflow",
        "risk_decision_signal",
        "",
    ]
    rows = []
    for idx in range(1450):
        src = sources.sample(1, random_state=int(RNG.integers(0, 1_000_000))).iloc[0]
        asset_type = choice(asset_types, p=[0.34, 0.25, 0.12, 0.11, 0.08, 0.10])
        days_since_refresh = int(choice([*range(0, 95)], p=None))
        if src["criticality"] == "high":
            days_since_refresh = int(max(0, RNG.gamma(2.1, 4.3)))
        classification = choice(classifications, p=[0.14, 0.44, 0.29, 0.13])
        include_candidate = choice([True, False], p=[0.74, 0.26])
        has_description = choice([True, False], p=[0.82, 0.18])
        semantic_label = choice(labels, p=[0.11, 0.12, 0.12, 0.08, 0.08, 0.09, 0.08, 0.09, 0.08, 0.10, 0.05])
        rows.append(
            {
                "asset_id": f"AST-{idx + 1:05d}",
                "source_id": src["source_id"],
                "asset_title": f"{src['domain']} {asset_type.replace('_', ' ').title()} {idx + 1:04d}",
                "asset_type": asset_type,
                "domain": src["domain"],
                "ai_retrieval_candidate": include_candidate,
                "included_in_retrieval": include_candidate and bool(src["approved_for_ai"]) and choice([True, False], p=[0.84, 0.16]),
                "business_description_present": has_description,
                "metadata_owner_present": choice([True, False], p=[0.86, 0.14]),
                "lineage_documented": choice([True, False], p=[0.77, 0.23]),
                "last_refreshed_at": (AS_OF_DATE - timedelta(days=days_since_refresh)).isoformat(),
                "classification": classification,
                "access_control_status": choice(["aligned", "overexposed", "missing_review"], p=[0.78, 0.12, 0.10]),
                "retention_status": choice(["aligned", "expired", "missing_policy"], p=[0.82, 0.08, 0.10]),
                "semantic_label": semantic_label,
                "document_structure_score": round(float(np.clip(RNG.normal(0.78, 0.16), 0.25, 1.0)), 3),
                "retrieval_ambiguity_score": round(float(np.clip(RNG.normal(0.28, 0.18), 0.02, 0.92)), 3),
                "risk_decision_signal": choice(["high", "medium", "low", "unclear"], p=[0.22, 0.42, 0.26, 0.10]),
                "consumer_team": choice(["AI Platform", "Fraud Product", "Identity Product", "Compliance Ops", "Customer Ops"]),
            }
        )
    assets = pd.DataFrame(rows)
    assets["days_since_refresh"] = (
        pd.Timestamp(AS_OF_DATE) - pd.to_datetime(assets["last_refreshed_at"])
    ).dt.days
    return assets


def build_metadata_reviews(assets: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, asset in assets.iterrows():
        completeness = 100
        completeness -= 20 if not asset["business_description_present"] else 0
        completeness -= 18 if not asset["metadata_owner_present"] else 0
        completeness -= 18 if not asset["lineage_documented"] else 0
        completeness -= 16 if asset["semantic_label"] == "" else 0
        completeness -= int((1 - asset["document_structure_score"]) * 20)
        completeness = int(np.clip(completeness + RNG.normal(0, 4), 28, 100))
        rows.append(
            {
                "review_id": f"REV-{asset['asset_id'].split('-')[1]}",
                "asset_id": asset["asset_id"],
                "business_description_quality": choice(["clear", "partial", "missing"], p=[0.62, 0.25, 0.13]),
                "field_dictionary_status": choice(["complete", "partial", "missing"], p=[0.55, 0.32, 0.13]),
                "semantic_label_status": "missing" if asset["semantic_label"] == "" else choice(["approved", "needs_review"], p=[0.84, 0.16]),
                "ownership_status": "documented" if asset["metadata_owner_present"] else "missing_owner",
                "lineage_status": "documented" if asset["lineage_documented"] else choice(["partial", "missing"], p=[0.45, 0.55]),
                "metadata_completeness_score": completeness,
                "reviewed_at": (AS_OF_DATE - timedelta(days=int(RNG.integers(0, 45)))).isoformat(),
            }
        )
    return pd.DataFrame(rows)


def build_policy_checks(assets: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
    rank = {
        "public_internal": 1,
        "confidential": 2,
        "restricted": 3,
        "regulated_sensitive": 4,
    }
    source_lookup = sources.set_index("source_id")
    rows = []
    for _, asset in assets.iterrows():
        source = source_lookup.loc[asset["source_id"]]
        exceeds = rank[asset["classification"]] > rank[source["max_allowed_classification"]]
        access_issue = asset["access_control_status"] != "aligned" or exceeds
        rows.append(
            {
                "policy_check_id": f"POL-{asset['asset_id'].split('-')[1]}",
                "asset_id": asset["asset_id"],
                "classification": asset["classification"],
                "source_max_allowed_classification": source["max_allowed_classification"],
                "classification_within_source_policy": not exceeds,
                "access_control_status": asset["access_control_status"],
                "retention_status": asset["retention_status"],
                "retention_policy_days": int(source["retention_policy_days"]),
                "contains_sensitive_tokens": bool(choice([True, False], p=[0.18, 0.82])),
                "governance_pass": not access_issue and asset["retention_status"] == "aligned",
                "review_required_before_retrieval": bool(access_issue or asset["retention_status"] != "aligned"),
            }
        )
    return pd.DataFrame(rows)


def build_lineage_edges(assets: pd.DataFrame) -> pd.DataFrame:
    sample_assets = assets.sample(420, random_state=7)
    rows = []
    for idx, (_, asset) in enumerate(sample_assets.iterrows(), start=1):
        rows.append(
            {
                "lineage_edge_id": f"LIN-{idx:04d}",
                "asset_id": asset["asset_id"],
                "upstream_system": choice(["CRM", "Risk Warehouse", "Document CMS", "Case Management", "External Licensed Feed"]),
                "transformation_owner": choice(["Risk ETL", "Knowledge Systems", "Search Platform", "Data Platform"]),
                "downstream_ai_surface": choice(["risk_copilot", "case_triage_search", "identity_resolution_assistant", "compliance_answering"]),
                "lineage_certified": bool(asset["lineage_documented"] and choice([True, False], p=[0.82, 0.18])),
                "last_lineage_review_at": (AS_OF_DATE - timedelta(days=int(RNG.integers(0, 120)))).isoformat(),
            }
        )
    return pd.DataFrame(rows)


def compute_readiness(
    sources: pd.DataFrame,
    assets: pd.DataFrame,
    reviews: pd.DataFrame,
    policies: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    merged = (
        assets.merge(sources[["source_id", "approved_for_ai", "expected_refresh_days", "source_contract_status", "criticality"]], on="source_id")
        .merge(reviews[["asset_id", "metadata_completeness_score", "semantic_label_status", "ownership_status", "lineage_status"]], on="asset_id")
        .merge(policies[["asset_id", "governance_pass", "review_required_before_retrieval"]], on="asset_id")
    )
    merged["freshness_pass"] = merged["days_since_refresh"] <= merged["expected_refresh_days"]
    merged["metadata_pass"] = merged["metadata_completeness_score"] >= 80
    merged["semantic_label_pass"] = merged["semantic_label"].ne("") & merged["semantic_label_status"].ne("missing")
    merged["lineage_ownership_pass"] = merged["metadata_owner_present"] & merged["lineage_documented"]
    merged["retrieval_quality_pass"] = (
        (merged["document_structure_score"] >= 0.70)
        & (merged["retrieval_ambiguity_score"] <= 0.40)
        & merged["risk_decision_signal"].ne("unclear")
    )
    checks = [
        "freshness_pass",
        "metadata_pass",
        "semantic_label_pass",
        "lineage_ownership_pass",
        "governance_pass",
        "retrieval_quality_pass",
    ]
    merged["readiness_score"] = (merged[checks].mean(axis=1) * 100).round(1)
    merged["ai_ready_pass"] = (
        merged["approved_for_ai"]
        & merged["included_in_retrieval"]
        & (merged["source_contract_status"] == "active")
        & (merged["readiness_score"] >= 83.0)
    )
    source_scores = (
        merged.groupby(["source_id", "domain"], as_index=False)
        .agg(
            assets=("asset_id", "count"),
            included_assets=("included_in_retrieval", "sum"),
            ai_ready_assets=("ai_ready_pass", "sum"),
            avg_readiness_score=("readiness_score", "mean"),
            freshness_sla_compliance=("freshness_pass", "mean"),
            metadata_completeness=("metadata_pass", "mean"),
            semantic_label_coverage=("semantic_label_pass", "mean"),
            lineage_ownership_coverage=("lineage_ownership_pass", "mean"),
            governance_compliance=("governance_pass", "mean"),
            retrieval_quality_pass_rate=("retrieval_quality_pass", "mean"),
        )
        .round(3)
    )
    source_scores["ai_ready_pass_rate"] = (source_scores["ai_ready_assets"] / source_scores["assets"]).round(3)
    source_scores["avg_readiness_score"] = source_scores["avg_readiness_score"].round(1)
    return merged, source_scores


def build_remediation_queue(readiness: pd.DataFrame) -> pd.DataFrame:
    issue_defs = [
        ("freshness_pass", "stale_source", "Refresh or remove stale retrieval source"),
        ("metadata_pass", "metadata_gap", "Complete business description and field dictionary"),
        ("semantic_label_pass", "semantic_label_gap", "Assign approved retrieval category labels"),
        ("lineage_ownership_pass", "lineage_owner_gap", "Document owner and upstream lineage"),
        ("governance_pass", "governance_gap", "Resolve classification, access, or retention exception"),
        ("retrieval_quality_pass", "retrieval_ambiguity", "Rewrite or split asset to reduce ambiguous retrieval context"),
    ]
    priority = {"high": 3, "medium": 2, "low": 1, "unclear": 2}
    rows = []
    for _, asset in readiness.iterrows():
        for check, issue_type, recommendation in issue_defs:
            if bool(asset[check]):
                continue
            severity = "P1" if asset["criticality"] == "high" or issue_type == "governance_gap" else choice(["P2", "P3"], p=[0.68, 0.32])
            exposure = int(
                10
                + (100 - asset["readiness_score"]) * 2.2
                + priority.get(asset["risk_decision_signal"], 1) * 16
                + (18 if asset["included_in_retrieval"] else 0)
                + RNG.normal(0, 8)
            )
            rows.append(
                {
                    "issue_id": f"ISS-{len(rows) + 1:05d}",
                    "asset_id": asset["asset_id"],
                    "source_id": asset["source_id"],
                    "domain": asset["domain"],
                    "issue_type": issue_type,
                    "severity": severity,
                    "included_in_retrieval": bool(asset["included_in_retrieval"]),
                    "estimated_risk_exposure_points": int(np.clip(exposure, 5, 160)),
                    "recommended_action": recommendation,
                    "target_owner": choice(["Data Steward", "Source Owner", "Governance Partner", "Knowledge Manager"]),
                    "cycle_time_target_days": int(choice([5, 10, 15, 20], p=[0.28, 0.42, 0.22, 0.08])),
                    "status": choice(["open", "in_progress", "blocked", "resolved"], p=[0.42, 0.29, 0.14, 0.15]),
                }
            )
    queue = pd.DataFrame(rows)
    queue = queue.sort_values(["severity", "estimated_risk_exposure_points"], ascending=[True, False]).head(900)
    return queue


def write_outputs(
    sources: pd.DataFrame,
    readiness: pd.DataFrame,
    source_scores: pd.DataFrame,
    queue: pd.DataFrame,
) -> dict:
    metric_summary = {
        "as_of_date": AS_OF_DATE.isoformat(),
        "source_count": int(sources.shape[0]),
        "asset_count": int(readiness.shape[0]),
        "retrieval_candidate_assets": int(readiness["ai_retrieval_candidate"].sum()),
        "included_retrieval_assets": int(readiness["included_in_retrieval"].sum()),
        "ai_ready_data_quality_pass_rate": round(float(readiness["ai_ready_pass"].mean()), 3),
        "freshness_sla_compliance": round(float(readiness["freshness_pass"].mean()), 3),
        "metadata_business_description_completeness": round(float(readiness["metadata_pass"].mean()), 3),
        "ownership_lineage_documentation_coverage": round(float(readiness["lineage_ownership_pass"].mean()), 3),
        "governed_access_classification_retention_compliance": round(float(readiness["governance_pass"].mean()), 3),
        "semantic_labeling_categorization_coverage": round(float(readiness["semantic_label_pass"].mean()), 3),
        "risk_decision_signal_actionability": round(float(readiness["risk_decision_signal"].ne("unclear").mean()), 3),
        "open_remediation_issues": int(queue[queue["status"].ne("resolved")].shape[0]),
        "p1_governance_issues": int(queue[(queue["severity"] == "P1") & (queue["issue_type"] == "governance_gap")].shape[0]),
    }
    (OUTPUT_DIR / "readiness_metrics.json").write_text(json.dumps(metric_summary, indent=2) + "\n")

    source_scores.to_csv(OUTPUT_DIR / "source_readiness_scores.csv", index=False)
    queue.to_csv(OUTPUT_DIR / "remediation_queue_ranked.csv", index=False)

    issue_summary = (
        queue.groupby(["issue_type", "severity"], as_index=False)
        .agg(
            issue_count=("issue_id", "count"),
            open_or_blocked=("status", lambda s: int(s.isin(["open", "blocked"]).sum())),
            exposure_points=("estimated_risk_exposure_points", "sum"),
            median_target_cycle_days=("cycle_time_target_days", "median"),
        )
        .sort_values(["exposure_points", "issue_count"], ascending=False)
    )
    issue_summary.to_csv(OUTPUT_DIR / "issue_type_summary.csv", index=False)

    source_priorities = (
        source_scores.assign(
            gap_score=lambda x: (
                (1 - x["freshness_sla_compliance"])
                + (1 - x["metadata_completeness"])
                + (1 - x["semantic_label_coverage"])
                + (1 - x["lineage_ownership_coverage"])
                + (1 - x["governance_compliance"]) * 1.35
            )
        )
        .sort_values("gap_score", ascending=False)
        .head(15)
    )
    source_priorities.to_csv(OUTPUT_DIR / "source_remediation_priorities.csv", index=False)

    findings = [
        "# Executive Findings",
        "",
        f"As of {AS_OF_DATE.isoformat()}, the synthetic lab contains {metric_summary['source_count']} approved-source style records and {metric_summary['asset_count']} AI-consumed knowledge assets.",
        "",
        f"- AI-ready pass rate is {metric_summary['ai_ready_data_quality_pass_rate']:.1%}; the main blockers are freshness, governance, and lineage/ownership documentation.",
        f"- Freshness SLA compliance is {metric_summary['freshness_sla_compliance']:.1%}; stale high-criticality assets should be refreshed or excluded before retrieval use.",
        f"- Governed access/classification/retention compliance is {metric_summary['governed_access_classification_retention_compliance']:.1%}; this is the strongest remediation workstream because it controls whether content is appropriate for AI retrieval.",
        f"- Semantic labeling coverage is {metric_summary['semantic_labeling_categorization_coverage']:.1%}; unlabeled assets create ambiguous retrieval and weaker reasoning context.",
        f"- The ranked queue contains {metric_summary['open_remediation_issues']} non-resolved remediation items, including {metric_summary['p1_governance_issues']} P1 governance gaps.",
        "",
        "Recommended sequence: resolve P1 governance exceptions first, refresh stale high-criticality sources second, then complete metadata, lineage, and semantic labels for assets already included in retrieval.",
        "",
    ]
    (OUTPUT_DIR / "generated_executive_summary.md").write_text("\n".join(findings))
    return metric_summary


def render_images(source_scores: pd.DataFrame, queue: pd.DataFrame, readiness: pd.DataFrame) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")

    metrics = [
        "freshness_sla_compliance",
        "metadata_completeness",
        "semantic_label_coverage",
        "lineage_ownership_coverage",
        "governance_compliance",
        "retrieval_quality_pass_rate",
    ]
    heat = (
        source_scores.groupby("domain")[metrics]
        .mean()
        .sort_values("governance_compliance")
    )
    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.imshow(heat.values, cmap="RdYlGn", vmin=0.45, vmax=1.0)
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(
        [
            "Freshness",
            "Metadata",
            "Semantic labels",
            "Lineage/owner",
            "Governance",
            "Retrieval quality",
        ],
        rotation=35,
        ha="right",
    )
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels(heat.index)
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            ax.text(j, i, f"{heat.values[i, j]:.0%}", ha="center", va="center", fontsize=8)
    ax.set_title("AI Retrieval Readiness Pass Rates by Domain", fontsize=15, weight="bold")
    ax.set_xlabel("Readiness control")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "readiness_control_heatmap.png", dpi=180)
    plt.close(fig)

    top_issues = (
        queue.groupby("issue_type", as_index=False)
        .agg(issue_count=("issue_id", "count"), exposure=("estimated_risk_exposure_points", "sum"))
        .sort_values("exposure", ascending=True)
    )
    fig, ax = plt.subplots(figsize=(11, 6.5))
    colors = ["#546A7B" if issue != "governance_gap" else "#B23A48" for issue in top_issues["issue_type"]]
    ax.barh(top_issues["issue_type"].str.replace("_", " ").str.title(), top_issues["exposure"], color=colors)
    for _, row in top_issues.iterrows():
        ax.text(row["exposure"] + 80, list(top_issues["issue_type"]).index(row["issue_type"]), f"{int(row['issue_count'])} issues", va="center", fontsize=9)
    ax.set_title("Remediation Queue Exposure by Issue Type", fontsize=15, weight="bold")
    ax.set_xlabel("Synthetic risk exposure points")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "remediation_exposure_by_issue.png", dpi=180)
    plt.close(fig)

    decision = (
        readiness.assign(decision=np.where(readiness["ai_ready_pass"], "include", np.where(readiness["review_required_before_retrieval"], "exclude_until_review", "conditional_include")))
        .groupby(["domain", "decision"], as_index=False)
        .size()
    )
    pivot = decision.pivot(index="domain", columns="decision", values="size").fillna(0)
    for column in ["include", "conditional_include", "exclude_until_review"]:
        if column not in pivot:
            pivot[column] = 0
    pivot = pivot[["include", "conditional_include", "exclude_until_review"]].sort_values("exclude_until_review", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6.5))
    bottom = np.zeros(len(pivot))
    palette = {"include": "#2E7D32", "conditional_include": "#D4A72C", "exclude_until_review": "#B23A48"}
    labels = {"include": "Include", "conditional_include": "Conditional", "exclude_until_review": "Exclude until review"}
    for column in pivot.columns:
        ax.bar(pivot.index, pivot[column], bottom=bottom, label=labels[column], color=palette[column])
        bottom += pivot[column].values
    ax.set_title("Retrieval Inclusion Decisions by Risk Domain", fontsize=15, weight="bold")
    ax.set_ylabel("Knowledge assets")
    ax.tick_params(axis="x", rotation=30)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "retrieval_inclusion_decisions.png", dpi=180)
    plt.close(fig)

    table = (
        source_scores.sort_values(["governance_compliance", "avg_readiness_score"], ascending=[True, True])
        .head(8)[["source_id", "domain", "assets", "avg_readiness_score", "freshness_sla_compliance", "governance_compliance", "ai_ready_pass_rate"]]
        .copy()
    )
    for col in ["freshness_sla_compliance", "governance_compliance", "ai_ready_pass_rate"]:
        table[col] = table[col].map(lambda value: f"{value:.0%}")
    table["avg_readiness_score"] = table["avg_readiness_score"].map(lambda value: f"{value:.1f}")
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.axis("off")
    tbl = ax.table(cellText=table.values, colLabels=table.columns, cellLoc="left", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1, 1.45)
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1F2933")
            cell.set_text_props(color="white", weight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#F4F6F8")
    ax.set_title("Lowest-Readiness Sources for Governance Review", fontsize=15, weight="bold", pad=18)
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "lowest_readiness_sources_table.png", dpi=180)
    plt.close(fig)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    sources = build_sources()
    assets = build_assets(sources)
    reviews = build_metadata_reviews(assets)
    policies = build_policy_checks(assets, sources)
    lineage = build_lineage_edges(assets)
    readiness, source_scores = compute_readiness(sources, assets, reviews, policies)
    queue = build_remediation_queue(readiness)

    save_csv(sources, "approved_ai_sources.csv")
    save_csv(assets, "knowledge_assets.csv")
    save_csv(reviews, "metadata_reviews.csv")
    save_csv(policies, "governance_policy_checks.csv")
    save_csv(lineage, "lineage_edges.csv")
    save_csv(queue, "remediation_queue.csv")

    metrics = write_outputs(sources, readiness, source_scores, queue)
    render_images(source_scores, queue, readiness)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
