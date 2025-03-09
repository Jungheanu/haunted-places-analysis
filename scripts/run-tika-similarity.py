import os
import sys
import argparse
import subprocess
import time
import random 

def run_similarity_analysis(similarity_type="cosine", input_dir=None, sample_size=None):

    start_time = time.time()
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Use provided input directory or default
    if not input_dir:
        input_dir = os.path.join(project_root, "data", "haunted_places")
    
    # Validate input directory
    try:
        all_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        file_count = len(all_files)
        print(f"Found {file_count} files in {input_dir}")
        
        if file_count == 0:
            print("Error: No files found in input directory!")
            return 1
            
        # Apply sampling if requested
        if sample_size and sample_size < file_count:
            print(f"Using a random sample of {sample_size} files (out of {file_count})")
            
            # Create a temporary directory for the sample
            temp_dir = os.path.join(project_root, "data", "sample_files")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Clear any existing files in the temp directory
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # Select a random sample of files
            sampled_files = random.sample(all_files, sample_size)
            
            # Create symbolic links to the sampled files
            for file in sampled_files:
                src = os.path.join(input_dir, file)
                dst = os.path.join(temp_dir, file)
                os.symlink(src, dst)
            
            # Use the temporary directory for analysis
            actual_input_dir = temp_dir
            print(f"Created sample directory at: {temp_dir}")
        else:
            actual_input_dir = input_dir
            if sample_size:
                print(f"Sample size {sample_size} >= file count {file_count}, using all files")
    
    except FileNotFoundError:
        print(f"Error: Directory not found: {input_dir}")
        return 1
    
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
        return 1
    
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
        return 1
    
    # Build the command
    command = [
        "python3",
        script_path,
        "--inputDir", actual_input_dir,
        "--outCSV", output_file
    ]
    
    print(f"Running {similarity_type} similarity analysis...")
    print(f"Command: {' '.join(command)}")
    
    try:
        start = time.time()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Show progress
        print("Processing files, please wait...")
        
        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Get the return code
        returncode = process.poll()
        
        # Print any remaining output
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout)
        
        elapsed = time.time() - start
        
        if returncode == 0:
            print(f"Successfully generated {similarity_type} similarity scores in {elapsed:.2f} seconds")
            
            # If we used sampling, add a note to the output file
            if sample_size and sample_size < file_count:
                with open(output_file, 'a') as f:
                    f.write(f"\n# Note: This file was generated using a random sample of {sample_size} files out of {file_count} total files.\n")
            
            return 0
        else:
            print(f"Error running similarity script: {stderr}")
            return returncode
            
    except Exception as e:
        print(f"Error running similarity script: {e}")
        return 1
    finally:
        # Clean up the temporary directory if we created one
        if sample_size and sample_size < file_count and 'temp_dir' in locals():
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"Removed temporary sample directory: {temp_dir}")
            except Exception as e:
                print(f"Warning: Failed to remove temporary directory: {e}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Run similarity analysis on a directory of files")
    parser.add_argument("--type", choices=["cosine", "jaccard", "edit_value", "all"], 
                      default="cosine", help="Type of similarity to calculate")
    parser.add_argument("--input-dir", help="Directory containing the files to analyze")
    parser.add_argument("--sample-size", type=int, help="Number of files to randomly sample (speeds up processing)")
    
    args = parser.parse_args()
    
    # Record the start time
    start_time = time.time()
    
    if args.type == "all":
        # Run all three similarity analyses
        for sim_type in ["cosine", "jaccard", "edit_value"]:
            print(f"\n{'-'*80}")
            print(f"Running {sim_type} similarity analysis")
            print(f"{'-'*80}")
            
            type_start = time.time()
            return_code = run_similarity_analysis(sim_type, args.input_dir, args.sample_size)
            type_elapsed = time.time() - type_start
            
            print(f"{sim_type} analysis completed in {type_elapsed:.2f} seconds")
            
            if return_code != 0:
                sys.exit(return_code)
    else:
        # Run just the specified similarity type
        return_code = run_similarity_analysis(args.type, args.input_dir, args.sample_size)
        if return_code != 0:
            sys.exit(return_code)
    
    # Print the total execution time
    total_elapsed = time.time() - start_time
    print(f"\nTotal execution time: {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} minutes)")
    
    sys.exit(0)

if __name__ == "__main__":
    main()