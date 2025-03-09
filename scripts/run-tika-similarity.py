import subprocess
import os
import sys
import argparse

def run_similarity_analysis(similarity_type="cosine", input_dir=None):
    """
    Runs a specified similarity analysis on the haunted places files
    
    Args:
        similarity_type (str): Type of similarity to calculate ('cosine', 'jaccard', or 'edit_value')
        input_dir (str): Path to the directory containing the files to analyze
    """
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Use provided input directory or default
    if not input_dir:
        input_dir = os.path.join(project_root, "data", "haunted_places")
    
    # Validate input directory
    try:
        files = os.listdir(input_dir)
        print(f"Found {len(files)} files in the input directory: {input_dir}")
        if not files:
            print("Error: No files found in input directory!")
            return 1  # Exit with an error code
    except FileNotFoundError:
        print(f"Error: Directory not found: {input_dir}")
        return 1  # Exit with an error code
    
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
    elif similarity_type == "edit_value":
        similarity_script = "edit-value-similarity.py"
        output_file = os.path.join(results_dir, "edit_value_similarity.csv")
    else:
        print(f"Error: Unknown similarity type: {similarity_type}")
        return 1  # Exit with an error code
    
    # Path to the similarity script
    script_path = os.path.join(
        project_root,
        "tika-similarity",
        "tikasimilarity",
        "distance",
        similarity_script
    )
    
    # Check if the script exists
    if not os.path.exists(script_path):
        print(f"Error: Similarity script not found: {script_path}")
        return 1  # Exit with an error code
    
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
            return process.returncode  # Exit with the same error code
        else:
            print(f"Successfully generated {similarity_type} similarity scores at: {output_file}")
            print(f"STDOUT: {process.stdout}")
            return 0  # Exit with a success code
    except Exception as e:
        print(f"Error running {similarity_type} similarity analysis: {e}", file=sys.stderr)
        return 1  # Exit with an error code

def main():
    parser = argparse.ArgumentParser(description="Run similarity analysis on haunted places files")
    parser.add_argument("--type", choices=["cosine", "jaccard", "edit_value", "all"], 
                        default="all", help="Type of similarity to calculate")
    parser.add_argument("--input-dir", help="Path to the input directory")
    
    args = parser.parse_args()
    
    if args.type == "all":
        # Run all three similarity analyses
        for similarity_type in ["cosine", "jaccard", "edit_value"]:
            return_code = run_similarity_analysis(similarity_type, args.input_dir)
            if return_code != 0:
                sys.exit(return_code)  # Exit immediately if any analysis fails
    else:
        # Run just the specified similarity type
        return_code = run_similarity_analysis(args.type, args.input_dir)
        if return_code != 0:
            sys.exit(return_code)  # Exit immediately if the analysis fails
    
    sys.exit(0)  # Exit with a success code if all analyses complete

if __name__ == "__main__":
    sys.exit(main())