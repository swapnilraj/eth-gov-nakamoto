# Ethereum Governance Analysis

This project analyzes the decentralization of Ethereum governance by processing the Ethereum Improvement Proposals (EIPs) repository and related governance data. The objective is to compute metrics (e.g., Nakamoto coefficient) that quantify how many distinct entities control >50% of contributions in different governance domains.

## Features
- Clone and parse the official EIPs repository as a submodule
- Extract author affiliations and count per-organization contributions
- Integrate client share and staking distribution data (via API or data files)
- Compute decentralization metrics across multiple governance domains
- Run automated tests for data extraction and transformation functions

## Submodules
This project uses Git submodules to manage external data sources.

1. **EIPs Repository**
   ```bash
   git submodule add https://github.com/ethereum/EIPs.git data/EIPs
   ```
2. **Consensus Specifications (optional)**
   ```bash
   git submodule add https://github.com/ethereum/consensus-specs.git data/consensus-specs
   ```
3. **Core Dev Meeting Materials (EF PM repo)**
   ```bash
   git submodule add https://github.com/ethereum/pm.git data/pm
   ```

## Setup
1. Clone this repository with submodules:
   ```bash
   git clone --recurse-submodules <your-repo-url>
   ```
2. Create a virtual environment using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
4. Run tests to verify setup:
   ```bash
   python -m pytest tests/
   ```

## Directory Layout
```
project_root/
  ├── data/                # Submodule content and sample data
  │   ├── EIPs/            # EIPs repository submodule
  │   ├── pm/              # Core dev meeting materials submodule
  │   ├── client_stats.json # Sample client distribution data
  │   └── staking_distribution.csv # Sample staking distribution data
  ├── src/                 # Analysis scripts 
  │   ├── parse_eips.py    # Extract EIP author data
  │   ├── parse_core_devs.py # Extract core dev meeting attendance
  │   └── compute_nakamoto.py # Calculate decentralization metrics
  ├── tests/               # Unit tests
  ├── notebooks/           # Exploratory analysis notebooks
  ├── output/              # Generated reports and visualizations
  ├── .cursorrules         # Coding and workflow rules
  ├── requirements.txt     # Python dependencies
  ├── run_analysis.sh      # Script to run the complete analysis
  ├── specs_versions.yml   # Version tracking for reproducibility
  └── README.md            # Project overview and setup
```

## Usage
1. Update submodules:
   ```bash
   git submodule update --remote --recursive
   ```
2. Run the complete analysis:
   ```bash
   ./run_analysis.sh
   ```
3. Run individual analysis steps:
   ```bash
   # Parse EIPs and extract author data
   python src/parse_eips.py --source data/EIPs --output output/authors.csv
   
   # Parse core dev meeting attendance
   python src/parse_core_devs.py --source data/pm --output output/core_dev_attendance.csv
   
   # Compute Nakamoto coefficients
   python src/compute_nakamoto.py --input output/authors.csv \
     --client-data data/client_stats.json \
     --staking-data data/staking_distribution.csv \
     --output output/nakamoto.csv
   ```
4. Explore data in notebooks:
   ```bash
   jupyter notebook notebooks/eip_analysis.ipynb
   ```

## Output Files
The analysis produces several files in the `output` directory:
- `authors.csv`: EIP author data with metadata
- `core_dev_attendance.csv`: Core developer meeting attendance records
- `nakamoto.csv`: Calculated Nakamoto coefficients for each governance domain
- `*_report.txt`: Text-based visualizations of entity shares in each domain

## Analysis Goals (SPECS)
See `SPECS.md` for a detailed list of metrics, definitions, and accepted data sources.

## Troubleshooting

### Matplotlib Font Issues
If you encounter errors related to font rendering in matplotlib:

1. **Use the `--no-plots` option**: 
   ```bash
   ./run_analysis.sh --no-plots
   ```
   This will skip matplotlib visualizations and only generate text reports.

2. **Install required fonts**:
   - On macOS: `brew install freetype fontconfig`
   - On Ubuntu/Debian: `sudo apt-get install fonts-dejavu`
   - On Fedora/RHEL: `sudo dnf install dejavu-sans-fonts`

3. **Configure matplotlib**:
   You can create a custom `~/.matplotlib/matplotlibrc` file with font settings:
   ```
   font.family: sans-serif
   font.sans-serif: Arial, Helvetica, DejaVu Sans, sans-serif
   ```

4. **Check text reports**:
   Even if visualizations fail, text-based reports will be generated in the `output` directory.

### Git Submodule Issues

If you encounter issues with Git submodules:

1. **Manual initialization**:
   ```bash
   git submodule init
   git submodule update
   ```

2. **Clone with submodules**:
   ```bash
   git clone --recurse-submodules <repository-url>
   ```

3. **Fix uninitialized submodules**:
   ```bash
   git submodule update --init --recursive
   ```

## Contributing
- Follow the conventions in `.cursorrules` for code style, testing, and security
- Open a pull request with clear descriptions of changes
- Ensure all tests pass and coverage remains high before merging

## License
This project is released under the MIT License.

