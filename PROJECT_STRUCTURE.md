# Ethereum Governance Analysis - Project Structure

This document explains the structure of the project to help new contributors get oriented.

## Overview

The Ethereum Governance Analysis project analyzes the decentralization of Ethereum governance by processing data from various sources and computing the Nakamoto coefficient - a measure of decentralization that counts the minimum number of entities needed to control more than 50% of a system.

## Key Modules

### 1. EIP Parser (`src/parse_eips.py`)

This module extracts author information from Ethereum Improvement Proposals (EIPs) by parsing the markdown files in the EIPs repository.

- `EipAuthor` class: Represents an author with name, email, github handle, and organization.
- `EipMetadata` class: Stores metadata for an EIP including number, title, status, and authors.
- `parse_eip_file()`: Parses a single EIP file to extract metadata.
- `map_github_to_organization()`: Maps GitHub handles to organizations (placeholder).
- `process_eips_repository()`: Processes all EIPs in the repository and outputs a CSV file.

### 2. Core Dev Meeting Parser (`src/parse_core_devs.py`)

This module extracts attendance information from Ethereum Core Dev meeting notes in the PM repository.

- `MeetingData` class: Represents meeting information including number, date, and attendees.
- `extract_meeting_attendees()`: Parses a meeting notes file to extract attendance information.
- `map_attendee_to_organization()`: Maps attendee names to organizations.
- `process_core_dev_meetings()`: Processes all meeting notes and outputs attendance data.

### 3. Nakamoto Coefficient Calculator (`src/compute_nakamoto.py`)

This module computes decentralization metrics based on entity shares.

- `compute_nakamoto_coefficient()`: Calculates the Nakamoto coefficient for any domain.
- `compute_eip_nakamoto()`: Specifically calculates the Nakamoto coefficient for EIP authorship.
- `compute_all_metrics()`: Computes metrics for all available governance domains.
- Functions for loading data from various sources and visualizing results.

## Data Sources

The project uses several data sources:

1. **EIPs Repository** (`data/EIPs`): A Git submodule containing the official Ethereum Improvement Proposals.
2. **PM Repository** (`data/pm`): A Git submodule containing Ethereum core dev meeting notes.
3. **Client Statistics** (`data/client_stats.json`): A JSON file with client implementation shares.
4. **Staking Distribution** (`data/staking_distribution.csv`): A CSV file with staking pool shares.

## Output Files

The analysis produces several output files:

1. **Authors CSV** (`output/authors.csv`): EIP author data with organizational affiliations.
2. **Core Dev Attendance CSV** (`output/core_dev_attendance.csv`): Meeting attendance records.
3. **Nakamoto Coefficients CSV** (`output/nakamoto.csv`): Computed decentralization metrics.
4. **Visualizations** (`output/*.png`): Charts showing entity shares for each governance domain.

## Tests

The project includes unit tests for all key functionality:

- `tests/test_parse_eips.py`: Tests for EIP parsing functionality.
- `tests/test_compute_nakamoto.py`: Tests for Nakamoto coefficient calculations.

## Exploratory Analysis

The `notebooks` directory contains Jupyter notebooks for exploratory data analysis:

- `notebooks/eip_analysis.ipynb`: Analysis of EIP authorship patterns and organizational influence.

## Adding New Data Sources

To add a new governance domain for analysis:

1. Create a parser for the new data source in the `src` directory.
2. Add loading functions to `compute_nakamoto.py`.
3. Update `compute_all_metrics()` to include the new domain.
4. Add appropriate test cases in the `tests` directory.
5. Update `run_analysis.sh` to include the new data source in the analysis pipeline. 