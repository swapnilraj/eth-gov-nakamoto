#!/usr/bin/env python3
"""
EIP Parser - Extract author information from Ethereum Improvement Proposals
"""

import os
import re
import csv
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
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
            
            # Extract email if present (must contain a dot to distinguish from GitHub handles)
            email_match = re.search(r'<([^>]*\.[^>]*)>', name)
            if email_match:
                email = email_match.group(1)
                name = name.replace(email_match.group(0), '').strip()
                
            # Extract GitHub handle if present
            github_match = re.search(r'@([\w-]+)', name)
            if github_match:
                github = github_match.group(1)
                name = name.replace(github_match.group(0), '').strip()
                
            # Extract organization if in parentheses
            org_match = re.search(r'\(([^)]*)\)', name)
            if org_match:
                org_content = org_match.group(1)
                # Only set organization if parentheses aren't empty
                if org_content.strip():
                    organization = org_content
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


def load_organization_mapping(mapping_file: str) -> Dict[str, List[str]]:
    """
    Load organization mapping from JSON file and create case-insensitive mapping.
    
    Args:
        mapping_file: Path to the organization mapping JSON file
        
    Returns:
        Dictionary mapping names to list of organizations (case-insensitive keys)
    """
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    # Create case-insensitive mapping
    case_insensitive_mapping = {}
    for key, orgs in mapping.items():
        case_insensitive_mapping[key.lower()] = orgs
    
    return case_insensitive_mapping


def get_organizations(author: EipAuthor, org_mapping: Dict[str, List[str]]) -> Set[str]:
    """
    Get organizations for an author based on name and GitHub handle.
    
    Args:
        author: EipAuthor object
        org_mapping: Organization mapping dictionary (case-insensitive keys)
        
    Returns:
        Set of organizations
    """
    orgs = set()
    
    # Try to find by name (case-insensitive)
    if author.name.lower() in org_mapping:
        orgs.update(org_mapping[author.name.lower()])
    
    # Try to find by GitHub handle (case-insensitive)
    if author.github and author.github.lower() in org_mapping:
        orgs.update(org_mapping[author.github.lower()])
    
    # Add organization from EIP if present
    if author.organization and len(orgs) == 0:
        orgs.add(author.organization)
    
    if author.github and len(orgs) == 0:
        orgs.add(author.github)
        
    return orgs


def process_eips_repository(repo_path: str, output_path: str, org_mapping_file: str) -> None:
    """
    Process all EIPs in the repository and generate an authors CSV file.
    
    Args:
        repo_path: Path to the EIPs repository
        output_path: Path to save the output CSV file
        org_mapping_file: Path to the organization mapping JSON file
    """
    eips_path = Path(repo_path)
    
    # Load organization mapping
    org_mapping = load_organization_mapping(org_mapping_file)
    
    # Find all EIP markdown files
    eip_files = list(eips_path.glob('EIPS/eip-*.md'))
    print(f"Found {len(eip_files)} EIP files")
    
    eip_metadata_list = []
    for file_path in tqdm(eip_files, desc="Parsing EIPs"):
        metadata = parse_eip_file(file_path)
        if metadata:
            eip_metadata_list.append(metadata)
    
    print(f"Successfully parsed {len(eip_metadata_list)} EIPs")
    
    # Prepare output directory
    output_dir = Path(output_path).parent
    os.makedirs(output_dir, exist_ok=True)
    
    # Write results to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['EIP', 'Title', 'Type', 'Category', 'Status', 'Created', 
                         'Author Name', 'Author Email', 'Author GitHub', 'Organizations'])
        
        for metadata in eip_metadata_list:
            for author in metadata.authors:
                # Get organizations from mapping and EIP
                organizations = get_organizations(author, org_mapping)
                
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
                    '; '.join(sorted(organizations)) if organizations else ''
                ])
    
    print(f"EIP author data written to {output_path}")


def main() -> None:
    """Main entry point for the EIP parser."""
    parser = argparse.ArgumentParser(description='Parse EIPs and extract author information')
    parser.add_argument('--source', required=True, help='Path to the EIPs repository')
    parser.add_argument('--output', default='output/authors.csv', help='Output CSV file path')
    parser.add_argument('--org-mapping', required=True, help='Path to organization mapping JSON file')
    args = parser.parse_args()
    
    process_eips_repository(args.source, args.output, args.org_mapping)


if __name__ == '__main__':
    main() 