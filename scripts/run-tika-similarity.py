import subprocess
import os
import sys
import argparse

def run_similarity_analysis(similarity_type="cosine"):
    """
    Runs a specified similarity analysis on the haunted places files
    
    Args:
        similarity_type (str): Type of similarity to calculate ('cosine', 'jaccard', or 'edit-value')
    """
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the directory containing the files to analyze
    input_dir = os.path.join(project_root, "datasets", "haunted_places_files")
    
    # Validate input directory
    try:
        files = os.listdir(input_dir)
        print(f"Found {len(files)} files in the input directory: {files[:5] if len(files) >= 5 else files}")
        if not files:
            print("Error: No files found in input directory!")
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Directory not found: {input_dir}")
        sys.exit(1)
    
    # Create similarity-results directory if it doesn't exist
    results_dir = os.path.join(project_root, "similarity-results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Determine which similarity script to use
    if similarity_type == "cosine":
        similarity_script = "cosine_similarity.py"
        output_file = os.path.join(results_dir, "cosine_similarity.csv")
    elif similarity_type == "jaccard":
        similarity_script = "jaccard_similarity.py"
        output_file = os.path.join(results_dir, "jaccard_similarity.csv")
    elif similarity_type == "edit-value":
        similarity_script = "edit-value-similarity.py" 
        output_file = os.path.join(results_dir, "edit_value_similarity.csv")
    else:
        print(f"Error: Unknown similarity type: {similarity_type}")
        sys.exit(1)
    
    # Path to the similarity script
    script_path = os.path.join(
        project_root,
        "tika-similarity",
        "tikasimilarity",
        "distance",
        similarity_script
    )
    
    # Build the command
    command = [
        "python3",
        script_path,
        "--inputDir", input_dir,
        "--outCSV", output_file
    ]
    
    print(f"Running {similarity_type} similarity analysis...")
    print(f"Command: {' '.join(command)}")
    print(f"Input directory: {input_dir}")
    print(f"Output file: {output_file}")
    
    try:
        # Execute with captured output to see errors
        process = subprocess.run(command, check=False, capture_output=True, text=True)
        if process.returncode != 0:
            print(f"Error running script. Return code: {process.returncode}")
            print(f"STDERR: {process.stderr}")
            sys.exit(1)
        else:
            print(f"Successfully generated {similarity_type} similarity scores at: {output_file}")
            print(f"STDOUT: {process.stdout}")
    except Exception as e:
        print(f"Error running {similarity_type} similarity analysis: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run similarity analysis on haunted places files")
    parser.add_argument("--type", choices=["cosine", "jaccard", "edit-value", "all"], 
                        default="all", help="Type of similarity to calculate")
    
    args = parser.parse_args()
    
    if args.type == "all":
        # Run all three similarity analyses
        for similarity_type in ["cosine", "jaccard", "edit-value"]:
            run_similarity_analysis(similarity_type)
    else:
        # Run just the specified similarity type
        run_similarity_analysis(args.type)

if __name__ == "__main__":
    main()