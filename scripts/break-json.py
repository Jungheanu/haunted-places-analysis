#!/usr/bin/env python3
import argparse
import json
import os
import re

def clean_filename(name):
    # Convert to a safe filename by removing problematic characters
    return re.sub(r'[^a-zA-Z0-9_-]', '_', str(name))

def break_json_to_files(input_file, output_dir):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {input_file}")
            print(f"JSON error: {e}")
            return
    
    # Handle different JSON structures
    if isinstance(data, dict) and "haunted_places" in data:
        # Format: {"haunted_places": [...]}
        items = data["haunted_places"]
    elif isinstance(data, list):
        # Format: [...]
        items = data
    else:
        print(f"Error: Unexpected JSON format in {input_file}")
        print(f"Expected a list or a dict with 'haunted_places' key")
        print(f"Got: {type(data)}")
        return
    
    if not isinstance(items, list):
        print(f"Error: Expected an array but got {type(items)}")
        return
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a file for each JSON object
    for i, item in enumerate(items):
        # Generate a descriptive filename if possible, otherwise use index
        if isinstance(item, dict):
            if 'id' in item:
                filename = f"{clean_filename(item['id'])}.txt"
            elif 'name' in item:
                filename = f"{clean_filename(item['name'])}.txt"
            elif 'State' in item:
                filename = f"{clean_filename(item['State'])}_{i}.txt"
            else:
                filename = f"item_{i}.txt"
            
            file_path = os.path.join(output_dir, filename)
            
            # Write each field as a line in the text file
            with open(file_path, 'w') as f:
                for key, value in item.items():
                    f.write(f"{key}: {value}\n")
        else:
            print(f"Warning: Skipping non-dict item at index {i}")
    
    file_count = len([f for f in os.listdir(output_dir) if f.endswith('.txt')])
    print(f"Created {file_count} files in {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Break JSON array into individual files")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output-dir", required=True, help="Output directory for individual files")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1
        
    break_json_to_files(args.input, args.output_dir)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())