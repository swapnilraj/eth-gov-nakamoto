#!/usr/bin/env python3
"""
EIP Parser - Extract author information from Ethereum Improvement Proposals
"""

import os
import re
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import yaml
from bs4 import BeautifulSoup
from tqdm import tqdm


@dataclass
class EipAuthor:
    """Represents an author of an Ethereum Improvement Proposal."""
    name: str
    email: Optional[str] = None
    github: Optional[str] = None
    organization: Optional[str] = None


class EipMetadata:
    """Metadata for an Ethereum Improvement Proposal."""
    def __init__(self, eip_number: int, title: str, authors: List[EipAuthor], 
                 status: str, type_: str, category: Optional[str], 
                 created: str):
        self.eip_number = eip_number
        self.title = title
        self.authors = authors
        self.status = status
        self.type = type_
        self.category = category
        self.created = created


def parse_eip_file(file_path: Path) -> Optional[EipMetadata]:
    """
    Parse an EIP markdown file and extract its metadata.
    
    Args:
        file_path: Path to the EIP markdown file
        
    Returns:
        EipMetadata object or None if parsing failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract YAML frontmatter
        yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            return None
            
        frontmatter = yaml.safe_load(yaml_match.group(1))
        
        # Extract EIP number from filename
        eip_number_match = re.search(r'eip-(\d+)', file_path.name)
        if eip_number_match:
            eip_number = int(eip_number_match.group(1))
        else:
            return None
            
        # Extract authors
        authors_raw = frontmatter.get('author', '')
        authors = []
        
        # Split authors by comma if it's a string
        if isinstance(authors_raw, str):
            author_entries = [a.strip() for a in authors_raw.split(',')]
        elif isinstance(authors_raw, list):
            author_entries = authors_raw
        else:
            author_entries = []
            
        for author_entry in author_entries:
            # Try to parse name, email, github handle, and organization
            name = author_entry
            email = None
            github = None
            organization = None
            
            # Extract email if present
            email_match = re.search(r'<([^>]+)>', author_entry)
            if email_match:
                email = email_match.group(1)
                name = name.replace(email_match.group(0), '').strip()
                
            # Extract GitHub handle if present
            github_match = re.search(r'@(\w+)', author_entry)
            if github_match:
                github = github_match.group(1)
                name = name.replace(github_match.group(0), '').strip()
                
            # Extract organization if in parentheses
            org_match = re.search(r'\(([^)]+)\)', author_entry)
            if org_match:
                organization = org_match.group(1)
                name = name.replace(org_match.group(0), '').strip()
                
            authors.append(EipAuthor(name=name, email=email, github=github, organization=organization))
            
        return EipMetadata(
            eip_number=eip_number,
            title=frontmatter.get('title', ''),
            authors=authors,
            status=frontmatter.get('status', ''),
            type_=frontmatter.get('type', ''),
            category=frontmatter.get('category', None),
            created=frontmatter.get('created', '')
        )
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def map_github_to_organization(github_handles: List[str]) -> Dict[str, str]:
    """
    Map GitHub handles to organizations.
    In a real implementation, this could use GitHub API or a prepared mapping.
    
    Args:
        github_handles: List of GitHub handles to map
        
    Returns:
        Dictionary mapping GitHub handles to organization names
    """
    # This is a placeholder - in a real implementation you would:
    # 1. Use GitHub API to fetch organization info
    # 2. Use a prepared CSV mapping
    # 3. Use a combination of sources
    # For now, we'll return an empty mapping
    return {}


def process_eips_repository(repo_path: str, output_path: str) -> None:
    """
    Process all EIPs in the repository and generate an authors CSV file.
    
    Args:
        repo_path: Path to the EIPs repository
        output_path: Path to save the output CSV file
    """
    eips_path = Path(repo_path)
    
    # Find all EIP markdown files
    eip_files = list(eips_path.glob('EIPS/eip-*.md'))
    print(f"Found {len(eip_files)} EIP files")
    
    eip_metadata_list = []
    for file_path in tqdm(eip_files, desc="Parsing EIPs"):
        metadata = parse_eip_file(file_path)
        if metadata:
            eip_metadata_list.append(metadata)
    
    print(f"Successfully parsed {len(eip_metadata_list)} EIPs")
    
    # Collect all GitHub handles
    github_handles = []
    for metadata in eip_metadata_list:
        for author in metadata.authors:
            if author.github:
                github_handles.append(author.github)
    
    # Map GitHub handles to organizations
    github_to_org = map_github_to_organization(github_handles)
    
    # Prepare output directory
    output_dir = Path(output_path).parent
    os.makedirs(output_dir, exist_ok=True)
    
    # Write results to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['EIP', 'Title', 'Type', 'Category', 'Status', 'Created', 
                         'Author Name', 'Author Email', 'Author GitHub', 'Organization'])
        
        for metadata in eip_metadata_list:
            for author in metadata.authors:
                # If organization not specified in EIP, try to get it from GitHub mapping
                organization = author.organization
                if not organization and author.github and author.github in github_to_org:
                    organization = github_to_org[author.github]
                    
                writer.writerow([
                    metadata.eip_number,
                    metadata.title,
                    metadata.type,
                    metadata.category or '',
                    metadata.status,
                    metadata.created,
                    author.name,
                    author.email or '',
                    author.github or '',
                    organization or ''
                ])
    
    print(f"EIP author data written to {output_path}")


def main() -> None:
    """Main entry point for the EIP parser."""
    parser = argparse.ArgumentParser(description='Parse EIPs and extract author information')
    parser.add_argument('--source', required=True, help='Path to the EIPs repository')
    parser.add_argument('--output', default='output/authors.csv', help='Output CSV file path')
    args = parser.parse_args()
    
    process_eips_repository(args.source, args.output)


if __name__ == '__main__':
    main() 