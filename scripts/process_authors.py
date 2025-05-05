import pandas as pd
import json
from collections import defaultdict
from typing import Dict, List, Set
import re

def extract_organization_from_email(email: str) -> str:
    """Extract organization name from email domain."""
    if not email or '@' not in email:
        return ""
    
    domain = email.split('@')[1].lower()
    # Remove common TLDs and subdomains
    domain = re.sub(r'\.(com|org|io|net|edu|gov)$', '', domain)
    domain = re.sub(r'^www\.', '', domain)
    
    # Convert domain to readable organization name
    org_name = domain.replace('.', ' ').title()
    return org_name

def process_authors_data(csv_path: str) -> Dict:
    """Process authors data and create organization mappings."""
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Initialize a dictionary to store author information
    authors_data = defaultdict(lambda: {
        'emails': set(),
        'github_handles': set(),
        'organizations': set(),
        'inferred_organizations': set()
    })
    
    # Process each row
    for _, row in df.iterrows():
        author_name = row['Author Name']
        if pd.isna(author_name):
            continue
            
        # Add non-empty values to respective sets
        if not pd.isna(row['Author Email']):
            email = row['Author Email'].strip()
            authors_data[author_name]['emails'].add(email)
            # Infer organization from email
            inferred_org = extract_organization_from_email(email)
            if inferred_org:
                authors_data[author_name]['inferred_organizations'].add(inferred_org)
                
        if not pd.isna(row['Author GitHub']):
            authors_data[author_name]['github_handles'].add(row['Author GitHub'].strip())
            
        if not pd.isna(row['Organization']):
            authors_data[author_name]['organizations'].add(row['Organization'].strip())
    
    # Convert sets to lists for JSON serialization
    result = {}
    for author, data in authors_data.items():
        result[author] = {
            'emails': list(data['emails']),
            'github_handles': list(data['github_handles']),
            'organizations': list(data['organizations']),
            'inferred_organizations': list(data['inferred_organizations'])
        }
    
    return result

def main():
    # Process the authors data
    authors_mapping = process_authors_data('output/authors.csv')
    
    # Save the results to a JSON file
    with open('output/authors_organizations.json', 'w') as f:
        json.dump(authors_mapping, f, indent=2)
    
    print(f"Processed {len(authors_mapping)} authors")
    print("Results saved to output/authors_organizations.json")

if __name__ == "__main__":
    main() 