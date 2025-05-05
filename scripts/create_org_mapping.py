import json
from typing import Dict, List, Set
from collections import defaultdict

def create_org_mapping(authors_file: str) -> Dict:
    """Create a mapping of names and GitHub handles to organizations."""
    # Read the existing authors data
    with open(authors_file, 'r') as f:
        authors_data = json.load(f)
    
    # Initialize mappings
    name_to_orgs = defaultdict(set)
    github_to_orgs = defaultdict(set)
    
    # Process each author
    for author_name, data in authors_data.items():
        # Get all organizations
        all_orgs = set(data['organizations'])
        
        # Add to name mapping
        name_to_orgs[author_name].update(all_orgs)
        
        # Add to GitHub handle mapping
        for github_handle in data['github_handles']:
            github_to_orgs[github_handle].update(all_orgs)
    
    # Convert sets to sorted lists for JSON serialization
    result = {
        **{
            name: sorted(list(orgs)) 
            for name, orgs in name_to_orgs.items()
        },
        **{
            handle: sorted(list(orgs))
            for handle, orgs in github_to_orgs.items()
        }
    }
    
    return result

def main():
    # Create the organization mappings
    org_mapping = create_org_mapping('output/authors_organizations.json')
    
    # Save the results to a JSON file
    with open('output/organization_mapping.json', 'w') as f:
        json.dump(org_mapping, f, indent=2)
    
    print(f"Created mappings for:")
    print(f"- {len(org_mapping['name_to_organizations'])} names")
    print(f"- {len(org_mapping['github_to_organizations'])} GitHub handles")
    print("Results saved to output/organization_mapping.json")

if __name__ == "__main__":
    main() 