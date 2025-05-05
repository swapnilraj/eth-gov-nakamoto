#!/usr/bin/env python3
"""
Parse Core Dev Meeting Attendance - Extract participant information from Ethereum Core Dev meetings
"""

import os
import re
import csv
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass
from bs4 import BeautifulSoup
from tqdm import tqdm


@dataclass
class MeetingData:
    """Data model for core dev meeting information."""
    meeting_number: int
    attendees: List[str]
    file_path: str

def load_organization_mapping(mapping_file: str) -> Dict:
    """Load organization mapping from JSON file."""
    try:
        with open(mapping_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading organization mapping: {e}")
        return {}

def extract_meeting_attendees(file_path: Path) -> MeetingData:
    """
    Extract attendance information from a core dev meeting notes file.
    
    Args:
        file_path: Path to the meeting notes markdown file
        
    Returns:
        MeetingData object with extracted information
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract meeting number from filename or content
        meeting_num_match = re.search(r'(?:meeting|call).*?(\d+)', str(file_path), re.IGNORECASE)
        if meeting_num_match:
            meeting_number = int(meeting_num_match.group(1))
        else:
            meeting_number = 0
            
        # Extract date from content
        date_match = re.search(r'Date: (\d{4}-\d{2}-\d{2})', content)
        if date_match:
            date = date_match.group(1)
        else:
            # Try alternative date formats
            alt_date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)? \w+ \d{4})', content)
            if alt_date_match:
                date = alt_date_match.group(1)
            else:
                date = "Unknown"
        
        # Extract attendees - look for common patterns in meeting notes
        attendees: Set[str] = set()
        
        # Pattern 1: Find attendee sections with a heading (# Attendees, ## Attendees, ### Attendees)
        # Improved pattern with more flexible section termination
        attendee_sections = re.finditer(
            r'(?:^|\n)#{1,3}\s+Attendees\s*\n+?(.*?)(?=\n#{1,3}|\n----|\n\n\n|\Z)', 
            content, 
            re.DOTALL
        )
        
        for section in attendee_sections:
            section_text = section.group(1).strip()
            
            # Handle bullet point lists (- or *) with optional diamond symbol
            # Updated pattern to handle GitHub-linked names with handle in URL
            bullet_items = re.finditer(
                r'[-*]\s+(?:♦\s+)?(?:\[([^\]]+?)(?:\s+)?\(([^)]+)\)?\]\([^)]+\)|\[([^\]]+)\]\([^)]+\)|([^\n]+))', 
                section_text
            )
            for item in bullet_items:
                # Check if it's a GitHub-linked name with org (group 1), 
                # GitHub-linked name without org (group 3), or regular name (group 4)
                name = item.group(1) or item.group(3) or item.group(4)
                if name and name.lower() not in ['agenda', 'summary', 'actions', 'notes']:
                    # Strip trailing commas and asterisks from names
                    name = name.strip().rstrip(',*')
                    attendees.add(name)
            
            # If no bullet points, check for comma-separated list
            if not re.search(r'[-*]', section_text):
                # First check if it's just a list of names on separate lines (no commas)
                lines = [line.strip() for line in section_text.split('\n') if line.strip()]
                if lines:
                    # If there are commas in any line, treat as comma-separated
                    if any(',' in line for line in lines):
                        for line in lines:
                            for name in line.split(','):
                                name = name.strip().rstrip(',*')
                                if name and len(name) > 1:
                                    attendees.add(name)
                    # Otherwise treat each line as a separate name
                    else:
                        for name in lines:
                            name = name.strip().rstrip(',*')
                            if name and len(name) > 1:
                                attendees.add(name)
        
        # Pattern 2: "Attendees: person1, person2, ..." format
        attendees_match = re.search(r'(?:^|\n)(?:Attendees|Participants):\s*(.*?)(?:\n\n|\n#{1,3}|\Z)', content, re.DOTALL)
        if attendees_match:
            attendee_text = attendees_match.group(1).strip()
            # Split by newlines and commas
            for line in attendee_text.split('\n'):
                for name in line.split(','):
                    name = name.strip().rstrip(',*')
                    if name and not name.startswith('-') and len(name) > 1:
                        attendees.add(name)
        
        # Fallback pattern: Handle simple # Attendees followed by bullet lists
        # that might not be caught by the main pattern
        fallback_match = re.search(r'(?:^|\n)#{1,3}\s+Attendees\s*\n+?((?:[-*]\s+[^\n]+\n?)+)', content)
        if fallback_match:
            bullet_text = fallback_match.group(1).strip()
            # Updated pattern to handle GitHub-linked names with handle in URL
            bullet_items = re.finditer(
                r'[-*]\s+(?:♦\s+)?(?:\[([^\]]+?)(?:\s+)?\(([^)]+)\)?\]\([^)]+\)|\[([^\]]+)\]\([^)]+\)|([^\n]+))', 
                bullet_text
            )
            for item in bullet_items:
                # Check if it's a GitHub-linked name with org (group 1), 
                # GitHub-linked name without org (group 3), or regular name (group 4)
                name = item.group(1) or item.group(3) or item.group(4)
                if name and name.lower() not in ['agenda', 'summary', 'actions', 'notes']:
                    # Strip trailing commas and asterisks from names
                    name = name.strip().rstrip(',*')
                    attendees.add(name)
        
        # Return the extracted data
        return MeetingData(
            meeting_number=meeting_number,
            attendees=list(attendees),
            file_path=str(file_path)
        )
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return MeetingData(meeting_number=0, attendees=[], file_path=str(file_path))


def map_attendee_to_organizations(attendee: str, org_mapping: Dict) -> List[str]:
    """
    Map attendee to their organizations using the organization mapping.
    
    Args:
        attendee: Attendee name, possibly with organization
        
    Returns:
        List of organization names
    """
    # First check if organization is in parentheses (with or without space)
    org_match = re.search(r'(.+?)(?:\s+)?\(([^)]+)\)', attendee)
    if org_match:
        return [org_match.group(2).strip()]
    
    # Clean the attendee name - remove org, trailing commas, and asterisks
    clean_name = re.sub(r'(?:\s+)?\([^)]+\)', '', attendee).strip().rstrip(',*')
    
    # Try to find organizations by name (case-insensitive)
    orgs = set()
    # Create a case-insensitive mapping
    case_insensitive_mapping = {k.lower(): v for k, v in org_mapping.items()}
    
    if clean_name.lower() in case_insensitive_mapping:
        orgs.update(case_insensitive_mapping[clean_name.lower()])
    
    # Try to find organizations by GitHub handle if present (case-insensitive)
    github_match = re.search(r'@([\w-]+)', clean_name)
    if github_match:
        github_handle = github_match.group(1).lower()
        if github_handle in case_insensitive_mapping:
            orgs.update(case_insensitive_mapping[github_handle])
    
    return list(orgs)


def process_core_dev_meetings(repo_path: str, output_path: str, org_mapping_file: str) -> None:
    """
    Process all core dev meeting notes and generate attendance CSV.
    
    Args:
        repo_path: Path to the Ethereum PM repository
        output_path: Path to save the output CSV file
        org_mapping_file: Path to the organization mapping JSON file
    """
    # Load organization mapping
    org_mapping = load_organization_mapping(org_mapping_file)
    
    repo_path = Path(repo_path)
    
    # Define common patterns for AllCoreDevs files
    patterns = [
        "AllCoreDevs*/**/*Call*",
        "AllCoreDevs*/**/*call*", 
        "AllCoreDevs*/**/*Meeting*",
        "AllCoreDevs*/**/*meeting*",
    ]
    # Find all meeting notes
    meeting_files = []
    for pattern in patterns:
        meeting_files.extend(list(repo_path.glob(f"**/{pattern}.md")))
    
    # Process each file
    meeting_data_list = []
    for file_path in tqdm(meeting_files, desc="Processing meeting notes"):
        meeting_data = extract_meeting_attendees(file_path)
        if meeting_data.meeting_number > 0:
            meeting_data_list.append(meeting_data)
    
    print(f"Successfully processed {len(meeting_data_list)} core dev meetings")
    
    # Prepare output directory
    output_dir = Path(output_path).parent
    os.makedirs(output_dir, exist_ok=True)
    
    # Write meeting attendance to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Meeting Number', 'Attendee', 'Organizations', 'Filename'])
        
        for meeting in meeting_data_list:
            for attendee in meeting.attendees:
                organizations = map_attendee_to_organizations(attendee, org_mapping)
                # Remove organization from attendee name if it's in the name
                clean_attendee = re.sub(r'(?:\s+)?\([^)]+\)', '', attendee).strip().rstrip(',')
                
                writer.writerow([
                    meeting.meeting_number,
                    clean_attendee,
                    '; '.join(organizations) if organizations else '',
                    meeting.file_path
                ])
    
    print(f"Core dev meeting attendance data written to {output_path}")


def main() -> None:
    """Main entry point for the core dev meeting parser."""
    parser = argparse.ArgumentParser(description='Parse core dev meeting notes and extract attendance')
    parser.add_argument('--source', required=True, help='Path to the Ethereum PM repository')
    parser.add_argument('--output', default='output/core_dev_attendance.csv', help='Output CSV file path')
    parser.add_argument('--org-mapping', default='data/organization_mapping.json', help='Path to organization mapping JSON file')
    args = parser.parse_args()
    
    process_core_dev_meetings(args.source, args.output, args.org_mapping)


if __name__ == '__main__':
    main() 