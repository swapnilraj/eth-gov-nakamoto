This document defines the goals, metrics, data sources, and methodology for the Ethereum Governance Analysis project.

1. Project Overview

Objective: Quantify decentralisation in Ethereum governance by measuring how many distinct entities control over 50% of decision-making power across multiple governance domains.

Scope: Focus on on-chain and off-chain governance processes including EIP authorship, core-dev participation, client diversity, staking distribution, and community signaling.

2. Governance Domains & Metrics

Domain

Metric

Definition

EIP Authorship

Nakamoto coefficient of EIP authors

Minimum number of organizations whose combined authored EIPs exceed 50% of all accepted EIPs in the selected period.

Core Dev Participation

Nakamoto coefficient of call attendees

Minimum number of organizations that together attend >50% of AllCoreDevs calls over the period.

Client Diversity

Nakamoto coefficient of client share

Minimum number of client implementations managing >50% of active nodes or validators.

Staking Distribution

Nakamoto coefficient of stake pools

Minimum number of staking pools/entities controlling >50% of total ETH staked.

Community Signaling

Participation coefficient

Count of unique participants or entities in on-chain governance votes exceeding 50% of total voting weight.

3. Timeframe & Versions

Analysis Window: Last 24 months of EIP acceptance and governance activity (e.g., Jan 2023 – Dec 2024).

Repository Versions: Use git tag or commit hashes for EIPs submodule and consensus-specs submodule snapshots at analysis start.

4. Data Sources

EIPs Repository: data/EIPs submodule containing eip-1.md through eip-XXXX.md files.

AllCoreDevs Calls: Meeting minutes, attendance logs in data/core-dev-calls (exported CSV).

Client Statistics: Node and validator counts per client from a beacon chain API or export (data/client_stats.json).

Staking Data: Staking pool breakdown from a reliable dashboard or beacon chain API (data/staking_distribution.csv).

On-chain Signals: Snapshot or governance DAO proposals CSV (data/governance_votes.csv).

5. Methodology

5.1 Data Extraction

EIP Parsing: Extract author metadata from each accepted EIP. Map author GitHub handles to organizations.

Core Dev Attendance: Parse call logs to list participants and their affiliations for each meeting.

Client & Stake Data: Fetch or import JSON/CSV files listing client and staking pool shares.

Governance Votes: Export on-chain vote records and aggregate by participant/entity.

5.2 Data Transformation

Normalize organization names (e.g., 'EF', 'Ethereum Foundation', 'ethereumfoundation' → 'Ethereum Foundation').

Aggregate counts and percentages by domain.

5.3 Metric Computation

Nakamoto Coefficient: Sort entities by descending share and count entities until cumulative share >50%.

Participation Coefficient: Count unique voters or signalers whose aggregated vote weight crosses 50% threshold.

5.4 Validation & Testing

Unit tests on parsing functions (e.g., EIP author extraction consistency).

Data quality checks: no missing values in key fields, share sums to 100% per domain.

Cross-validate sample metrics manually for accuracy.

6. Deliverables

authors.csv: Processed EIP author affiliations and counts.

nakamoto_coefficients.csv: Coefficients for each domain.

visualizations: Bar charts and cumulative share plots per domain.

report.md: Narrative interpretation of metrics with implications.

7. Revision & Maintenance

Update SPECS.md for any change in domains, data sources, or analysis windows.

Record submodule commit SHA in specs_versions.yml for reproducibility.