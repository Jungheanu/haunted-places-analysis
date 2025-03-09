#!/usr/bin/env python3
"""
Main script for Haunted Places Analysis

This script orchestrates the complete workflow:
1. Convert TSV to JSON using convert-tsv-to-json script
2. Break JSON into individual files using the break-json script
3. Generate similarity metrics (cosine, jaccard, edit_value)
4. Convert similarity data to formats needed for clustering
5. Generate cluster visualizations
6. Set up an HTTP server to view the visualizations
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command with proper error handling"""
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False, e.stdout
    except Exception as e:
        print(f"Error: {e}")
        return False, str(e)
    
def convert_tsv_to_json(tsv_file):
    """
    Convert TSV to JSON using convert-tsv-to-json script
    
    Args:
        tsv_file (str): Path to the TSV file
        
    Returns:
        str: Path to the output JSON file
    """
    print("\nConverting TSV to JSON...")
    
    # Path to the conversion script
    project_root = Path(__file__).parent  # FIXED: parent instead of parent.parent
    converter_script = project_root / "scripts" / "convert-tsv-to-json.py"
    
    if not converter_script.exists():
        print(f"Error: Converter script not found: {converter_script}")
        return None
    
    # Output JSON file path
    output_json = project_root / "datasets" / "merged_dataset.json"
    
    # Run the conversion script
    command = [sys.executable, str(converter_script), "--input", str(tsv_file), "--output", str(output_json)]
    success, _ = run_command(command, "Converting TSV to JSON")
    
    if success:
        print(f"Successfully converted to JSON: {output_json}")
        return output_json
    else:
        print("Failed to convert TSV to JSON")
        return None

def break_json_to_files(json_file):
    """
    Break JSON into individual files using break-json script
    
    Args:
        json_file (str): Path to the JSON file
        
    Returns:
        str: Path to the directory with individual files
    """
    print("\nBreaking JSON into individual files...")
    
    # Path to the break-json script
    project_root = Path(__file__).parent  # FIXED: parent instead of parent.parent
    breaker_script = project_root / "scripts" / "break-json.py"
    
    if not breaker_script.exists():
        print(f"Error: Breaker script not found: {breaker_script}")
        return None
    
    # Output directory for individual files
    output_dir = project_root / "data" / "haunted_places"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the break-json script
    command = [sys.executable, str(breaker_script), "--input", str(json_file), "--output-dir", str(output_dir)]
    success, _ = run_command(command, "Breaking JSON into individual files")
    
    if success:
        print(f"Successfully created individual files in: {output_dir}")
        return output_dir
    else:
        print("Failed to break JSON into individual files")
        return None

def run_similarity_analysis(data_dir):
    """Run similarity analyses on the data"""
    print("\nRunning similarity analyses...")

    # Path to the similarity script
    project_root = Path(__file__).parent
    similarity_script = project_root / "scripts" / "run-tika-similarity.py"

    if not similarity_script.exists():
        print(f"Error: Similarity script not found: {similarity_script}")
        return None

    # Run the similarity script
    command = [
        sys.executable,
        str(similarity_script),
        "--input-dir", str(data_dir),
        "--type", "all"  # Run all similarity types
    ]

    success, _ = run_command(command, "Running similarity analysis")
    if success:
        print("Successfully generated similarity scores")
        results_dir = project_root / "similarity-results"
        return results_dir
    else:
        print("Failed to generate similarity scores")
        return None

def generate_cluster_data():
    """Generate cluster data and visualization JSON files"""
    print("\nGenerating cluster data...")
    
    # Path to the cluster generation script
    project_root = Path(__file__).parent  # FIXED: parent instead of parent.parent
    cluster_script = project_root / "scripts" / "generate-cluster-scores.py"
    
    if not cluster_script.exists():
        print(f"Error: Cluster script not found: {cluster_script}")
        return False
    
    # Run the cluster script
    command = [sys.executable, str(cluster_script)]
    success, _ = run_command(command, "Generating cluster data")
    return success

def setup_visualizations():
    """Set up visualization server"""
    print("\nSetting up visualization server...")
    
    # Path to the visualization script
    project_root = Path(__file__).parent  # FIXED: parent instead of parent.parent
    viz_script = project_root / "scripts" / "visualize-results.py"
    
    if not viz_script.exists():
        print(f"Error: Visualization script not found: {viz_script}")
        return False
    
    # Run the visualization script in a separate process so it doesn't block
    command = [sys.executable, str(viz_script)]
    
    # We don't use run_command here because we want to start the server in the background
    try:
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Visualization server started in the background")
        return True
    except Exception as e:
        print(f"Failed to start visualization server: {e}")
        return False

def main():
    """Main function that orchestrates the entire workflow"""
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Run Haunted Places Analysis")
    parser.add_argument("--tsv-file", default=None, help="Path to the TSV dataset file")
    parser.add_argument("--skip-convert", action="store_true", help="Skip TSV to JSON conversion")
    parser.add_argument("--skip-break", action="store_true", help="Skip breaking JSON to files")
    parser.add_argument("--skip-similarity", action="store_true", help="Skip similarity analysis")
    parser.add_argument("--skip-clustering", action="store_true", help="Skip clustering")
    parser.add_argument("--skip-visualization", action="store_true", help="Skip visualization")
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Step 1: Convert TSV to JSON
    if not args.skip_convert:
        # Use provided TSV file or default
        tsv_file = args.tsv_file if args.tsv_file else project_root / "datasets" / "merged_dataset.tsv"
        
        if not os.path.exists(tsv_file):
            print(f"Error: TSV file not found: {tsv_file}")
            print("Please specify a valid TSV file with --tsv-file option")
            return 1
        
        json_file = convert_tsv_to_json(tsv_file)
        if not json_file:
            return 1
    else:
        print("\nSkipping TSV to JSON conversion...")
        json_file = project_root / "datasets" / "merged_dataset.json"
    
    # Step 2: Break JSON into individual files
    if not args.skip_break:
        if not os.path.exists(json_file):
            print(f"Error: JSON file not found: {json_file}")
            return 1
            
        data_dir = break_json_to_files(json_file)
        if not data_dir:
            return 1
    else:
        print("\nSkipping JSON to files step...")
        data_dir = project_root / "data" / "haunted_places"
    
    # Validate data directory
    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found: {data_dir}")
        return 1
    
    print("\n=== Haunted Places Analysis ===")
    print(f"Project root: {project_root}")
    print(f"Data directory: {data_dir}")
    
    # Step 3: Run similarity analysis
    if not args.skip_similarity:
        results_dir = run_similarity_analysis(data_dir)
    else:
        print("\nSkipping similarity analysis step...")
        results_dir = project_root / "similarity-results"
    
    # Validate results
    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
    
    csv_files = list(Path(results_dir).glob("*.csv"))
    if not csv_files:
        print(f"Warning: No CSV files found in {results_dir}")
        print("Similarity analysis may not have produced results.")
    
    # Step 4: Generate cluster data
    if not args.skip_clustering:
        if not generate_cluster_data():
            print("Warning: Cluster data generation failed or produced warnings.")
    else:
        print("\nSkipping clustering step...")
    
    # Step 5: Set up visualizations
    if not args.skip_visualization:
        print("\nSetting up visualization server...")
        setup_visualizations()
        
        print("\n=== Analysis Complete ===")
        print("To view the results:")
        print(f"1. Open http://localhost:8000 in your browser")
        print(f"   If that doesn't work, check for any messages about an alternative port")
        print(f"2. If no server is running, manually view visualizations/index.html in your browser")
    else:
        print("\nSkipping visualization setup...")
        print("\n=== Analysis Complete ===")
        print("To view the results:")
        print(f"1. Run: python {project_root}/scripts/visualize-results.py to start a web server")
        print(f"2. Or open visualizations/index.html directly in your browser")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())