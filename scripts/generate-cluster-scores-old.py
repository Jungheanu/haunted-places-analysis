import csv
import os
import subprocess
import sys

def convert_csv_to_similarity_scores(csv_file, output_file):
    """
    Converts a CSV file from similarity analysis to the format expected by cluster-scores.py
    
    Args:
        csv_file (str): Path to the CSV file
        output_file (str): Path to write the output file
    """
    if not os.path.exists(csv_file):
        print(f"Warning: File not found: {csv_file}")
        return False
        
    with open(csv_file, 'r') as f_in, open(output_file, 'w') as f_out:
        reader = csv.reader(f_in)
        header = next(reader, None)  # Skip header
        
        if not header:
            print(f"Warning: Empty file or no header: {csv_file}")
            return False
            
        count = 0
        for row in reader:
            if len(row) >= 3:
                file1, file2, score = row[0], row[1], row[2]
                # Format: filename,score,path
                f_out.write(f"{os.path.basename(file1)},{score},{file1}\n")
                count += 1
                
        print(f"Converted {csv_file} to {output_file} ({count} entries)")
        return True if count > 0 else False

def run_cluster_script(input_file, output_file, threshold=0.01):
    """
    Runs the cluster-scores.py script on the input file
    
    Args:
        input_file (str): Path to the input file
        output_file (str): Path to write the output JSON file
        threshold (float): Threshold value for clustering
    """
    # Path to the cluster-scores.py script
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cluster_script = os.path.join(
        project_root, 
        "tika-similarity", 
        "tikasimilarity", 
        "cluster", 
        "cluster-scores.py"
    )
    
    # Create a temporary working directory
    temp_dir = os.path.dirname(input_file)
    
    # Create a symlink to the input file in the working directory
    temp_input = os.path.join(temp_dir, "similarity-scores.txt")
    
    # If it's different from our input file, create a symlink or copy
    if temp_input != input_file:
        # Copy the file
        with open(input_file, 'r') as src, open(temp_input, 'w') as dst:
            dst.write(src.read())
    
    # Current directory to restore later
    original_dir = os.getcwd()
    
    try:
        # Change to the temporary directory
        os.chdir(temp_dir)
        
        # Build the command
        command = [
            "python3",
            cluster_script,
            "-t", str(threshold)
        ]
        
        # Run the command
        subprocess.run(command, check=True)
        
        # Verify the clusters.json file was created
        temp_output = os.path.join(temp_dir, "clusters.json")
        if os.path.exists(temp_output):
            # Move/rename to the desired output file
            if temp_output != output_file:
                with open(temp_output, 'r') as src, open(output_file, 'w') as dst:
                    dst.write(src.read())
                os.remove(temp_output)  # Clean up
            
            print(f"Successfully created cluster file: {output_file}")
            return True
        else:
            print(f"Error: Cluster file not created: {temp_output}")
            return False
            
    finally:
        # Restore the original working directory
        os.chdir(original_dir)
        
        # Clean up
        if os.path.exists(temp_input) and temp_input != input_file:
            os.remove(temp_input)

def main():
    # Path to the CSV files
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(project_root, "similarity-results")
    
    # Create the directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    # List of similarity types to process
    similarity_types = [
        "cosine_similarity",
        "jaccard_similarity",
        "edit_distance_similarity"
    ]
    
    # Process each similarity type
    for sim_type in similarity_types:
        csv_file = os.path.join(results_dir, f"{sim_type}.csv")
        txt_file = os.path.join(results_dir, f"{sim_type}.txt")
        json_file = os.path.join(results_dir, f"{sim_type}_clusters.json")
        
        print(f"\nProcessing {sim_type}...")
        
        # Convert CSV to similarity scores format
        if convert_csv_to_similarity_scores(csv_file, txt_file):
            # Run the cluster-scores.py script on the converted file
            run_cluster_script(txt_file, json_file)
        else:
            print(f"Skipping clustering for {sim_type} due to conversion errors")
    
    print("\nProcessing complete. Files generated in:", results_dir)
    
if __name__ == "__main__":
    main()