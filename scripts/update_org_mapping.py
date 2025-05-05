import csv
import json
from collections import defaultdict
import re

def load_org_mapping(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_org_mapping(mapping, file_path):
    with open(file_path, 'w') as f:
        json.dump(mapping, f, indent=2)

def process_organization(org):
    orgs = set()
    org = org.strip()
    
    # Handle EF cases - matches "EF/", "EF:", "EF " at the start of the string
    if re.match(r'^EF[/:]|^EF\s', org, re.IGNORECASE):
        orgs.add('Ethereum')
        # Extract team name after EF (removes "EF/", "EF:", or "EF " prefix)
        team = re.sub(r'^EF[/:]\s*|^EF\s+', '', org, flags=re.IGNORECASE)
        if team and team.lower() not in ['research', '']:
            orgs.add(team)
    elif org.lower() == 'ef':
        # If it's just "EF", only add Ethereum
        orgs.add('Ethereum')
    else:
        # Only add original org if it's not an EF case and not just "Research"
        if org and org.lower() != 'research':
            orgs.add(org)
    
    # Handle MetaMask and PegaSys cases
    if re.search(r'metamask|pegasys', org, re.IGNORECASE):
        orgs.add('Consensys')
        # Split PegaSys combinations
        if re.search(r'pegasys', org, re.IGNORECASE):
            orgs.add('PegaSys')
        if re.search(r'pantheon', org, re.IGNORECASE):
            orgs.add('Pantheon')
    
    # Handle Solidity case
    if re.search(r'solidity', org, re.IGNORECASE):
        orgs.add('Ethereum')
        orgs.add('Cantina')
    
    # Handle Geth cases - only add Geth if it's a standalone org or EF team
    if re.search(r'^geth$|^EF[/:]\s*geth|^EF\s+geth', org, re.IGNORECASE):
        orgs.add('Geth')
        orgs.add('Ethereum')
    
    return orgs

def parse_attendance_csv(file_path):
    attendance_mapping = defaultdict(set)
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            attendee = row['Attendee'].strip()
            orgs = row['Organizations'].strip()
            
            if not attendee or not orgs:
                continue
                
            # Split organizations by semicolon and process each
            for org in orgs.split(';'):
                processed_orgs = process_organization(org.strip())
                attendance_mapping[attendee].update(processed_orgs)
    
    return attendance_mapping

def update_org_mapping(existing_mapping, attendance_mapping):
    updated_mapping = existing_mapping.copy()
    
    for attendee, orgs in attendance_mapping.items():
        if attendee in updated_mapping:
            # Update existing entry with new organizations
            updated_mapping[attendee] = list(set(updated_mapping[attendee] + list(orgs)))
        else:
            # Create new entry
            updated_mapping[attendee] = list(orgs)
    
    return updated_mapping

def main():
    # File paths
    attendance_file = 'output/core_dev_attendance.csv'
    org_mapping_file = 'data/organization_mapping.json'
    new_org_mapping_file = 'data/organization_mapping_updated.json'
    
    # Load existing mapping
    existing_mapping = load_org_mapping(org_mapping_file)
    
    # Parse attendance data
    attendance_mapping = parse_attendance_csv(attendance_file)
    
    # Update mapping
    updated_mapping = update_org_mapping(existing_mapping, attendance_mapping)
    
    # Save new mapping
    save_org_mapping(updated_mapping, new_org_mapping_file)
    print(f"Updated organization mapping saved to {new_org_mapping_file}")

if __name__ == "__main__":
    main() 