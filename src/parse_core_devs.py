#!/usr/bin/env python3
"""
Parse Core Dev Meeting Attendance - Extract participant information from Ethereum Core Dev meetings
"""

import os
import re
import csv
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
    date: str
    attendees: List[str]
    filename: str


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
        meeting_num_match = re.search(r'All Core Devs (?:Meeting |Call |)#?(\d+)', content)
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
        
        # Pattern 1: "Attendees: person1, person2, ..."
        attendees_match = re.search(r'(?:Attendees|Participants):\s*(.*?)(?:\n\n|\n#)', content, re.DOTALL)
        if attendees_match:
            attendee_text = attendees_match.group(1).strip()
            # Split by newlines and commas
            for line in attendee_text.split('\n'):
                for name in line.split(','):
                    name = name.strip()
                    if name and not name.startswith('-') and len(name) > 1:
                        attendees.add(name)
        
        # Pattern 2: "- Name (Organization)"
        name_pattern = r'[-*]\s+([^()]+)(?:\s+\(([^)]+)\))?'
        for match in re.finditer(name_pattern, content):
            name = match.group(1).strip()
            if name and name.lower() not in ['agenda', 'summary', 'actions', 'notes']:
                attendees.add(name)
        
        # Return the extracted data
        return MeetingData(
            meeting_number=meeting_number,
            date=date,
            attendees=list(attendees),
            filename=file_path.name
        )
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return MeetingData(meeting_number=0, date="Error", attendees=[], filename=file_path.name)


def map_attendee_to_organization(attendee: str) -> str:
    """
    Try to extract organization from attendee string or use a mapping.
    
    Args:
        attendee: Attendee name, possibly with organization
        
    Returns:
        Organization name if found, empty string otherwise
    """
    # Check if organization is in parentheses
    org_match = re.search(r'(.+)\s+\(([^)]+)\)', attendee)
    if org_match:
        return org_match.group(2).strip()
    
    # In a real implementation, you might have a mapping of people to organizations
    # This is a simplified placeholder
    return ""


def process_core_dev_meetings(repo_path: str, output_path: str) -> None:
    """
    Process all core dev meeting notes and generate attendance CSV.
    
    Args:
        repo_path: Path to the Ethereum PM repository
        output_path: Path to save the output CSV file
    """
    repo_path = Path(repo_path)
    
    # Define common patterns for AllCoreDevs files
    patterns = [
        "All Core Devs Meeting*",
        "All Core Devs Call*",
        "Core Devs Meeting*",
        "AllCoreDevs*"
    ]
    
    # Find all meeting notes
    meeting_files = []
    for pattern in patterns:
        meeting_files.extend(list(repo_path.glob(f"**/{pattern}.md")))
    
    print(f"Found {len(meeting_files)} potential core dev meeting files")
    
    # Process each file
    meeting_data_list = []
    for file_path in tqdm(meeting_files, desc="Processing meeting notes"):
        meeting_data = extract_meeting_attendees(file_path)
        if meeting_data.meeting_number > 0:
            meeting_data_list.append(meeting_data)
    
    # Sort by meeting number
    meeting_data_list.sort(key=lambda x: x.meeting_number)
    
    print(f"Successfully processed {len(meeting_data_list)} core dev meetings")
    
    # Prepare output directory
    output_dir = Path(output_path).parent
    os.makedirs(output_dir, exist_ok=True)
    
    # Write meeting attendance to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Meeting Number', 'Date', 'Attendee', 'Organization', 'Filename'])
        
        for meeting in meeting_data_list:
            for attendee in meeting.attendees:
                organization = map_attendee_to_organization(attendee)
                # Remove organization from attendee name if it's in the name
                clean_attendee = re.sub(r'\s+\([^)]+\)', '', attendee).strip()
                
                writer.writerow([
                    meeting.meeting_number,
                    meeting.date,
                    clean_attendee,
                    organization,
                    meeting.filename
                ])
    
    print(f"Core dev meeting attendance data written to {output_path}")


def main() -> None:
    """Main entry point for the core dev meeting parser."""
    parser = argparse.ArgumentParser(description='Parse core dev meeting notes and extract attendance')
    parser.add_argument('--source', required=True, help='Path to the Ethereum PM repository')
    parser.add_argument('--output', default='output/core_dev_attendance.csv', help='Output CSV file path')
    args = parser.parse_args()
    
    process_core_dev_meetings(args.source, args.output)


if __name__ == '__main__':
    main() 