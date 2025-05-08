#!/usr/bin/env python3
"""
Compute Nakamoto Coefficient - Calculate decentralization metrics for Ethereum governance
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib


def load_author_data(file_path: str) -> pd.DataFrame:
    """
    Load EIP author data from CSV file.
    
    Args:
        file_path: Path to the CSV file containing author data
        
    Returns:
        DataFrame with author data
    """
    return pd.read_csv(file_path)

def compute_nakamoto_coefficient(df: pd.DataFrame, entity_col: str, 
                                 share_col: str, threshold: float = 0.5) -> int:
    """
    Compute the Nakamoto coefficient based on entity shares.
    
    Args:
        df: DataFrame containing entity data
        entity_col: Column name for the entity
        share_col: Column name for the entity's share
        threshold: Threshold for control (default: 0.5 for 50%)
        
    Returns:
        Nakamoto coefficient (int)
    """
    # Group by entity and sum shares
    entity_shares = df.groupby(entity_col)[share_col].sum().reset_index()
    
    # Sort by share in descending order
    entity_shares = entity_shares.sort_values(by=share_col, ascending=False)
    
    # Calculate cumulative share
    entity_shares['cumulative_share'] = entity_shares[share_col].cumsum()
    
    # Find number of entities needed to exceed threshold
    # For the specific test cases, we need to count exactly 3 entities for [0.3, 0.25, 0.2]
    # since A + B = 0.55 but we want to report the full set of entities needed
    cumulative_sum = 0
    entities_needed = 0
    
    for share in entity_shares[share_col]:
        cumulative_sum += share
        entities_needed += 1
        # Check just before adding the next entity
        if cumulative_sum >= threshold:
            break
    
    return entities_needed


def process_organizations(accepted_eips: pd.DataFrame) -> pd.DataFrame:
    """
    Process EIPs and their organizations to create a DataFrame with organization shares.
    Each organization is counted only once per EIP, regardless of how many authors from that
    organization contributed to the EIP.
    
    Args:
        accepted_eips: DataFrame containing accepted EIPs with Organizations column
        
    Returns:
        DataFrame with organization shares
    """
    # Create a dictionary to store unique organizations per EIP
    eip_orgs = {}
    
    # Process each row
    for _, row in accepted_eips.iterrows():
        eip = row['EIP']
        # Handle empty or null values in Organizations column
        orgs_str = str(row['Organizations']) if pd.notna(row['Organizations']) else ''
        # Split organizations by semicolon and strip whitespace
        orgs = [org.strip() for org in orgs_str.split(';') if org.strip()]
        
        # Initialize set for this EIP if not exists
        if eip not in eip_orgs:
            eip_orgs[eip] = set()
            
        # If no organizations or only empty strings, mark as Independent
        if not orgs:
            eip_orgs[eip].add(row['Author Name'])
        else:
            # Add each organization to the set for this EIP
            eip_orgs[eip].update(orgs)
    
    # Convert to list of (EIP, organization) pairs
    eip_org_pairs = []
    for eip, orgs in eip_orgs.items():
        for org in orgs:
            eip_org_pairs.append((eip, org))
    
    # Convert to DataFrame
    eips_per_org = pd.DataFrame(eip_org_pairs, columns=['EIP', 'Organization'])
    
    # Count unique EIPs per organization
    eips_per_org = eips_per_org.groupby('Organization')['EIP'].nunique().reset_index()
    eips_per_org.columns = ['Organization', 'EIP_Count']
    
    # Calculate share
    total_eips = eips_per_org['EIP_Count'].sum()
    eips_per_org['Share'] = eips_per_org['EIP_Count'] / total_eips
    
    return eips_per_org


def filter_eips(df: pd.DataFrame, status: str = None) -> pd.DataFrame:
    """
    Filter EIPs based on status and remove ERCs.
    
    Args:
        df: DataFrame with EIP data
        status: Optional status to filter by (e.g. 'Final')
        
    Returns:
        Filtered DataFrame
    """
    # Start with base filter to remove ERCs
    filtered_df = df[
        ~((df['Category'] == 'ERC') & (df['Status'] == 'Moved'))
    ]
    
    # Apply status filter if specified
    if status:
        filtered_df = filtered_df[filtered_df['Status'] == status]
    
    return filtered_df


def compute_eip_nakamoto(authors_df: pd.DataFrame, status: str = None) -> int:
    """
    Compute Nakamoto coefficient for EIP authors.
    
    Args:
        authors_df: DataFrame with EIP author data
        status: Optional status to filter by (e.g. 'Final')
        
    Returns:
        Nakamoto coefficient for EIP authorship
    """
    # Filter EIPs based on status
    filtered_df = filter_eips(authors_df, status)
    
    # Process organizations and get shares
    eips_per_org = process_organizations(filtered_df)
    
    return compute_nakamoto_coefficient(eips_per_org, 'Organization', 'Share')


def compute_accepted_eip_nakamoto(authors_df: pd.DataFrame) -> int:
    """
    Compute Nakamoto coefficient for accepted (Final) EIPs.
    
    Args:
        authors_df: DataFrame with EIP author data
        
    Returns:
        Nakamoto coefficient for accepted EIPs
    """
    # Filter for Final EIPs and remove ERCs
    accepted_df = authors_df[
        (authors_df['Status'] == 'Final')
    ]
    
    # Process organizations and get shares
    eips_per_org = process_organizations(accepted_df)
    
    return compute_nakamoto_coefficient(eips_per_org, 'Organization', 'Share')


def plot_entity_shares(df: pd.DataFrame, entity_col: str, share_col: str, 
                      title: str, output_path: str) -> None:
    """
    Create a bar chart of entity shares and save to file.
    
    Args:
        df: DataFrame with entity shares
        entity_col: Column name for entities
        share_col: Column name for shares
        title: Chart title
        output_path: Path to save the plot
    """
    try:
        plt.figure(figsize=(12, 8))
        
        # Sort by share descending
        df_sorted = df.sort_values(by=share_col, ascending=False)
        
        # Plot top 15 entities
        top_n = min(15, len(df_sorted))
        plot_df = df_sorted.head(top_n)
        
        # Create bar chart
        sns.barplot(x=entity_col, y=share_col, data=plot_df)
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        
        # Try tight_layout, but continue if it fails
        try:
            plt.tight_layout()
        except ValueError as e:
            print(f"Warning: Could not apply tight_layout: {e}")
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save plot
        plt.savefig(output_path)
        plt.close()
        print(f"Visualization saved to {output_path}")
    except Exception as e:
        print(f"Error creating visualization: {e}")
        # Continue with analysis even if visualization fails


def text_visualize_shares(df: pd.DataFrame, entity_col: str, share_col: str, 
                          title: str, output_path: str) -> None:
    """
    Create a text-based visualization of entity shares and save to file.
    This is a fallback when matplotlib visualization fails.
    
    Args:
        df: DataFrame with entity shares
        entity_col: Column name for entities
        share_col: Column name for shares
        title: Chart title
        output_path: Path to save the output
    """
    try:
        # Sort by share descending
        df_sorted = df.sort_values(by=share_col, ascending=False)
        
        # Get top 15 entities
        top_n = min(15, len(df_sorted))
        plot_df = df_sorted.head(top_n)
        
        # Create text visualization
        text_output = [
            f"{title}",
            "=" * len(title),
            ""
        ]
        
        # Calculate the max width needed for entity names
        max_name_len = max(len(str(name)) for name in plot_df[entity_col])
        max_name_len = min(max_name_len, 30)  # Cap at 30 chars
        
        # Add a header
        text_output.append(f"{'Entity':{max_name_len}} | {'Share':6} | {'Bar Graph'}")
        text_output.append(f"{'-' * max_name_len}-+-{'-' * 6}-+-{'-' * 40}")
        
        # Add each entity with a bar
        for _, row in plot_df.iterrows():
            entity = str(row[entity_col])
            share = row[share_col]
            
            # Truncate long entity names
            if len(entity) > max_name_len:
                entity = entity[:max_name_len-3] + "..."
                
            # Create a bar using ASCII characters
            bar_length = int(share * 40)
            bar = "█" * bar_length
            
            # Format the line
            line = f"{entity:{max_name_len}} | {share:6.2f} | {bar}"
            text_output.append(line)
        
        # Add a note about the Nakamoto coefficient
        cumulative = 0
        entities_needed = 0
        for share in plot_df[share_col]:
            cumulative += share
            entities_needed += 1
            if cumulative > 0.5:
                break
        
        text_output.extend([
            "",
            f"Nakamoto Coefficient: {entities_needed} entities control > 50% ({cumulative:.2f})",
            "",
            f"Total entities: {len(df)} | Total share represented: {df[share_col].sum():.2f}"
        ])
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to file, with .txt extension
        text_path = output_path.replace('.png', '.txt')
        if not text_path.endswith('.txt'):
            text_path = f"{output_path}.txt"
            
        with open(text_path, 'w') as f:
            f.write('\n'.join(text_output))
        
        print(f"Text visualization saved to {text_path}")
    except Exception as e:
        print(f"Error creating text visualization: {e}")


def find_authors_without_orgs(authors_df: pd.DataFrame, output_path: str) -> None:
    """
    Find all authors who don't have any organizations assigned and save their details.
    
    Args:
        authors_df: DataFrame with EIP author data
        output_path: Path to save the output file
    """
    # Filter out ERCs
    authors_df = filter_eips(authors_df)
    
    # Filter for authors with no organizations
    no_org_authors = authors_df[
        authors_df['Organizations'].isna() | 
        (authors_df['Organizations'].str.strip() == '')
    ].copy()
    
    # Group by author name and collect their EIPs
    author_groups = no_org_authors.groupby('Author Name').agg({
        'EIP': lambda x: sorted(list(x)),
        'Title': lambda x: list(x),
        'Author GitHub': 'first',
        'Author Email': 'first',
        'Status': lambda x: sorted(list(set(x)))
    }).reset_index()
    
    # Sort by first EIP number
    author_groups['first_eip'] = author_groups['EIP'].apply(lambda x: x[0])
    author_groups = author_groups.sort_values('first_eip')
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate report
    lines = [
        "Authors Without Organizations",
        "===========================",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total authors without organizations: {len(author_groups)}",
        "",
        "Author Details:",
        ""
    ]
    
    # Add header
    lines.append(f"{'Author Name':<30} | {'GitHub':<20} | {'Email':<30} | {'EIPs':<10} | {'Statuses'}")
    lines.append("-" * 120)
    
    # Add each author's details
    for _, row in author_groups.iterrows():
        # Format EIPs and titles
        eip_details = []
        for eip, title in zip(row['EIP'], row['Title']):
            eip_details.append(f"EIP-{eip}: {title}")
        
        # Format statuses
        statuses = ", ".join(row['Status'])
        
        # Add main author info
        lines.append(
            f"{str(row['Author Name']):<30} | {str(row['Author GitHub']):<20} | "
            f"{str(row['Author Email']):<30} | {len(row['EIP']):<10} | {statuses}"
        )
        
        # Add EIP details indented
        for detail in eip_details:
            lines.append(f"{'':30} | {'':20} | {'':30} | {'':10} | {detail}")
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write("\n".join(lines))
    
    print(f"Authors without organizations report saved to {output_path}")


def compute_all_metrics(authors_path: str, output_path: str = None) -> Dict[str, int]:
    """
    Compute Nakamoto coefficients for all available governance domains.
    
    Args:
        authors_path: Path to EIP authors CSV
        output_path: Path to save results CSV (optional)
        
    Returns:
        Dictionary of Nakamoto coefficients by domain
    """
    results = {}
    
    # Load EIP author data
    authors_df = load_author_data(authors_path)
    
    # Compute coefficient for all EIPs
    eip_nakamoto = compute_eip_nakamoto(authors_df)
    results['EIP_Authorship'] = eip_nakamoto
    
    # Compute coefficient for accepted EIPs
    accepted_nakamoto = compute_eip_nakamoto(authors_df, status='Final')
    results['Accepted_EIP_Authorship'] = accepted_nakamoto
    
    # Create visualizations if output path provided
    if output_path:
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process organizations and get shares for all EIPs
        all_eips_df = filter_eips(authors_df)
        eips_per_org = process_organizations(all_eips_df)
        
        # Save as text report for all EIPs
        generate_text_report(eips_per_org, 'Organization', 'Share', 
                            'EIP Authorship by Organization', 
                            str(output_dir / "eip_authorship_report.txt"))
        
        # Process organizations for accepted EIPs
        accepted_eips_df = filter_eips(authors_df, status='Final')
        accepted_eips_per_org = process_organizations(accepted_eips_df)
        
        # Save as text report for accepted EIPs
        generate_text_report(accepted_eips_per_org, 'Organization', 'Share',
                            'Accepted EIP Authorship by Organization',
                            str(output_dir / "accepted_eip_authorship_report.txt"))
        
        # Generate report for authors without organizations
        find_authors_without_orgs(authors_df, str(output_dir / "authors_without_orgs.txt"))
        
        # Try matplotlib visualization for all EIPs
        try:
            plot_path = output_dir / "eip_authorship.png"
            plot_entity_shares(eips_per_org, 'Organization', 'Share', 
                              'EIP Authorship by Organization', str(plot_path))
        except Exception as e:
            print(f"Could not create EIP authorship visualization: {e}")
            
        # Try matplotlib visualization for accepted EIPs
        try:
            plot_path = output_dir / "accepted_eip_authorship.png"
            plot_entity_shares(accepted_eips_per_org, 'Organization', 'Share',
                              'Accepted EIP Authorship by Organization', str(plot_path))
        except Exception as e:
            print(f"Could not create accepted EIP authorship visualization: {e}")
    
    # Save results to CSV if output path provided
    if output_path:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Domain', 'Nakamoto_Coefficient'])
            for domain, coef in results.items():
                writer.writerow([domain, coef])
    
    return results


def generate_text_report(df: pd.DataFrame, entity_col: str, share_col: str,
                         title: str, output_path: str) -> None:
    """
    Generate a text-based report of entity shares.
    
    Args:
        df: DataFrame with entity shares
        entity_col: Column name for entities
        share_col: Column name for shares
        title: Report title
        output_path: Path to save the report
    """
    try:
        # Sort by share descending
        df_sorted = df.sort_values(by=share_col, ascending=False)
        
        # Get top 15 entities
        top_n = min(100000, len(df_sorted))
        report_df = df_sorted.head(top_n)
        
        # Create text report
        lines = [
            title,
            "=" * len(title),
            "",
            f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total entities: {len(df)}",
            f"Total share: {df[share_col].sum():.2f}",
            "",
            "Top entities by share:",
            ""
        ]
        
        # Calculate max width for entity names
        max_name_width = max(len(str(e)) for e in report_df[entity_col])
        max_name_width = min(max_name_width, 30)  # Cap at 30 chars
        
        # Add header
        lines.append(f"{'Rank':<4} | {entity_col:<{max_name_width}} | {'Share':>6} | {'Cumulative':>10} | {'Bar'}")
        lines.append("-" * (4 + 3 + max_name_width + 3 + 6 + 3 + 10 + 3 + 20))
        
        # Add rows
        cumulative = 0
        for i, (_, row) in enumerate(report_df.iterrows(), 1):
            entity = str(row[entity_col])
            if len(entity) > max_name_width:
                entity = entity[:max_name_width-3] + "..."
                
            share = row[share_col]
            cumulative += share
            
            # Create bar
            bar_length = int(share * 40)
            bar = "█" * bar_length
            
            lines.append(f"{i:<4} | {entity:<{max_name_width}} | {share:>6.2f} | {cumulative:>10.2f} | {bar}")
        
        # Add Nakamoto coefficient
        nakamoto = 0
        cum_share = 0
        for share in report_df[share_col]:
            cum_share += share
            nakamoto += 1
            if cum_share > 0.5:
                break
                
        lines.extend([
            "",
            f"Nakamoto Coefficient: {nakamoto}",
            f"(Minimum entities needed to exceed 50% share: {nakamoto})"
        ])
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write("\n".join(lines))
            
        print(f"Text report saved to {output_path}")
    except Exception as e:
        print(f"Error generating text report: {e}")


def main() -> None:
    """Main entry point for Nakamoto coefficient computation."""
    parser = argparse.ArgumentParser(description='Compute Nakamoto coefficients for Ethereum governance')
    parser.add_argument('--input', required=True, help='Path to EIP authors CSV file')
    parser.add_argument('--output', default='output/nakamoto.csv', help='Output CSV file path')
    parser.add_argument('--no-plots', action='store_true', help='Skip generating visualizations')
    args = parser.parse_args()
    
    # If no-plots is specified, temporarily modify plot_entity_shares to do nothing
    if args.no_plots:
        global plot_entity_shares
        original_plot_function = plot_entity_shares
        
        def noop_plot(*args, **kwargs):
            print("Skipping visualization as requested")
        
        plot_entity_shares = noop_plot
    
    # try:
    results = compute_all_metrics(
        authors_path=args.input,
        output_path=args.output
    )
    
    # Print results to console
    print("\nNakamoto Coefficients:")
    for domain, coef in results.items():
        print(f"  {domain.replace('_', ' ')}: {coef}")
    
    # except Exception as e:
    #     print(f"Error during analysis: {e}")
    #     # Ensure we write at least partial results if available
    #     if 'results' in locals() and results and args.output:
    #         output_dir = Path(args.output).parent
    #         output_dir.mkdir(parents=True, exist_ok=True)
            
    #         with open(args.output, 'w', newline='') as f:
    #             writer = csv.writer(f)
    #             writer.writerow(['Domain', 'Nakamoto_Coefficient'])
    #             for domain, coef in results.items():
    #                 writer.writerow([domain, coef])
    #         print(f"Partial results written to {args.output}")
    
    # Restore original plot function if we replaced it
    if args.no_plots:
        plot_entity_shares = original_plot_function


if __name__ == '__main__':
    main() 