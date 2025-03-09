import sys
import subprocess
import csv
import os
import json
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert TSV to JSON")
    parser.add_argument("--input", required=True, help="Input TSV file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--threshold", type=float, default=1.0, 
                      help="Similarity threshold (1.0 means keep everything)")
    args = parser.parse_args()
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    datasets_dir = os.path.join(project_root, 'datasets')
    
    # Use the paths from command line arguments
    tsv_file = args.input
    json_file = args.output
    column_headers_file = os.path.join(datasets_dir, 'column_headers.txt')
    object_type = 'haunted_places'
    threshold = args.threshold
    
    print(f"Converting {tsv_file} to {json_file} with threshold {threshold}")
    
    # Create the column_headers.txt file from the TSV headers
    create_column_headers_file(tsv_file, column_headers_file)
    
    command = [
        'python3', os.path.join(project_root, 'etllib/etl/tsvtojson.py'),
        '-t', tsv_file,
        '-j', json_file,
        '-c', column_headers_file,
        '-o', object_type,
        '-s', str(threshold)
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Successfully converted {tsv_file} to {json_file}")
        
        # Post-process the JSON to remove the header row
        remove_header_row_from_json(json_file, object_type)
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while converting TSV to JSON: {e}", file=sys.stderr)
        
    # At the end of your main() function in convert-tsv-to-json.py, add:
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            print(f"TOTAL RECORDS IN JSON: {len(data['haunted_places'])}")
    except Exception as e:
        print(f"Error counting records: {e}")

def create_column_headers_file(tsv_file, column_headers_file):
    """Create a column headers file from the TSV headers."""
    try:
        # Try to read the first line of the TSV file to get the headers
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            headers = next(reader)  # Get the first row which contains headers
        
        # Write the headers to the column_headers.txt file
        with open(column_headers_file, 'w', encoding='utf-8') as f:
            for header in headers:
                f.write(f"{header}\n")
        
        print(f"Created column headers file: {column_headers_file} with {len(headers)} headers")
    except Exception as e:
        print(f"Error creating column headers file: {e}", file=sys.stderr)
        sys.exit(1)

def remove_header_row_from_json(json_file, object_type):
    """Remove the first object (header row) from the JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if there's at least one object
        if object_type in data and len(data[object_type]) > 0:
            # Remove the first object (header row)
            data[object_type] = data[object_type][1:]
            
            # Write back the modified JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            print(f"Removed header row from JSON. Remaining objects: {len(data[object_type])}")
        else:
            print("No objects found in JSON or empty array.")
    except Exception as e:
        print(f"Error removing header row from JSON: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()