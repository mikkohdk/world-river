"""
Manual research utility for discovering news outlets.
Provides templates and import tools for adding outlets to find_sources.py.
"""

import json
import sys
from pathlib import Path


def create_research_template(country_code, country_name):
    """Generate a research template for manual discovery."""

    template = f"""
RESEARCH TEMPLATE FOR {country_name.upper()} ({country_code})
================================================================

Instructions:
1. Search Google: "{country_name} news RSS feed English"
2. Search Google: "{country_name} broadcaster news"
3. Visit major outlet websites and look for /feed/, /rss/, or /feeds/ URLs
4. Fill in the outlets below
5. Run: python discover_sources.py import -c {country_code}

OUTLETS TO RESEARCH:
-------------------

Outlet 1:
  Name: [e.g., APS News]
  Feed URL: [e.g., https://...]
  Type: [broadcast/commercial/wire/nonprofit]
  Notes: [e.g., National news agency]

Outlet 2:
  Name:
  Feed URL:
  Type:
  Notes:

Outlet 3:
  Name:
  Feed URL:
  Type:
  Notes:

-------------------
Once filled, save as: research_{country_code}.txt
Then run: python discover_sources.py import -c {country_code}
"""
    return template


def import_from_file(country_code, filename=None):
    """Import outlets from a research file."""

    if filename is None:
        filename = f"research_{country_code}.txt"

    path = Path(filename)
    if not path.exists():
        print(f"ERROR: {filename} not found")
        return None

    outlets = []
    current_outlet = {}

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('Name:'):
                if current_outlet and 'name' in current_outlet:
                    outlets.append(current_outlet)
                current_outlet = {'name': line.replace('Name:', '').strip()}
            elif line.startswith('Feed URL:'):
                current_outlet['url'] = line.replace('Feed URL:', '').strip()
            elif line.startswith('Type:'):
                current_outlet['type'] = line.replace('Type:', '').strip()
            elif line.startswith('Notes:'):
                current_outlet['notes'] = line.replace('Notes:', '').strip()

    if current_outlet and 'name' in current_outlet:
        outlets.append(current_outlet)

    return outlets


def add_to_find_sources(country_code, outlets):
    """Add outlets to find_sources.py SOURCE_CANDIDATES."""

    find_sources_path = Path('find_sources.py')

    if not find_sources_path.exists():
        print(f"ERROR: find_sources.py not found")
        return False

    with open(find_sources_path, 'r') as f:
        content = f.read()

    # Check if country already exists
    if f'"{country_code}": [' in content:
        print(f"WARNING: {country_code} already exists in SOURCE_CANDIDATES")
        return False

    # Generate Python code
    code_lines = []
    for outlet in outlets:
        code_lines.append(
            f'''        {{
            "name": "{outlet.get('name', 'Unknown')}",
            "url": "{outlet.get('url', '')}",
            "type": "{outlet.get('type', 'unknown')}",
            "notes": "{outlet.get('notes', '')}",
        }},'''
        )

    new_entry = f'''    "{country_code}": [
{chr(10).join(code_lines)}
    ],'''

    # Find insertion point (before final closing brace)
    insert_pos = content.rfind('}')
    if insert_pos == -1:
        print("ERROR: Cannot find closing brace in find_sources.py")
        return False

    new_content = content[:insert_pos] + new_entry + '\n' + content[insert_pos:]

    with open(find_sources_path, 'w') as f:
        f.write(new_content)

    print(f"[S] Added {len(outlets)} sources for {country_code} to find_sources.py")
    return True


def main():
    import argparse
    ap = argparse.ArgumentParser(
        description="Manual research utility for discovering news outlets"
    )

    subparsers = ap.add_subparsers(dest='command')

    # Generate template
    template_parser = subparsers.add_parser(
        'template',
        help='Generate research template for a country'
    )
    template_parser.add_argument('-c', '--country', required=True, help='Country code')
    template_parser.add_argument('-n', '--name', required=True, help='Country name')
    template_parser.add_argument('-o', '--output', help='Output file (default: research_CC.txt)')

    # Import from file
    import_parser = subparsers.add_parser(
        'import',
        help='Import outlets from research file'
    )
    import_parser.add_argument('-c', '--country', required=True, help='Country code')
    import_parser.add_argument('-f', '--file', help='Input file (default: research_CC.txt)')

    args = ap.parse_args()

    if args.command == 'template':
        template = create_research_template(args.country, args.name)

        output_file = args.output or f"research_{args.country}.txt"
        with open(output_file, 'w') as f:
            f.write(template)

        print(f"[+] Template created: {output_file}")
        print(f"\nNext steps:")
        print(f"  1. Edit {output_file} and fill in the outlets")
        print(f"  2. Run: python discover_sources.py import -c {args.country} -f {output_file}")

    elif args.command == 'import':
        file_path = args.file or f"research_{args.country}.txt"
        outlets = import_from_file(args.country, file_path)

        if outlets:
            print(f"\n[+] Imported {len(outlets)} outlets:\n")
            for outlet in outlets:
                print(f"  • {outlet.get('name', 'Unknown')}")
                print(f"    {outlet.get('url', 'N/A')}\n")

            if add_to_find_sources(args.country, outlets):
                print(f"\n[S] Ready to validate!")
                print(f"    python find_sources.py -c {args.country} --validate")
        else:
            print("[!] No outlets found in research file")

    else:
        ap.print_help()


if __name__ == "__main__":
    main()
