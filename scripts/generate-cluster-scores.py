#!/usr/bin/env python3
import csv
import os
import subprocess
import sys
import json
import shutil
from pathlib import Path

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
            
        # With this new code:
        rows = []
        for row in reader:
            if len(row) >= 3:
                file1, file2, score = row[0], row[1], float(row[2])
                # Add both files to improve clustering
                rows.append((file1, score, file1))
                rows.append((file2, score, file2))

        # Sort by score descending
        rows.sort(key=lambda x: x[1], reverse=True)

        # Then write the sorted data
        count = 0
        for file_path, score, path in rows:
            f_out.write(f"{os.path.basename(file_path)},{score},{file_path}\n")
            count += 1
                
        print(f"Converted {csv_file} to {output_file} ({count} entries)")
        return True if count > 0 else False

def run_cluster_scores(script_path, working_dir, input_file, output_file, threshold=0.01):
    """Run the cluster-scores.py script"""
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")
        return False
        
    # Copy input file to working directory as similarity-scores.txt
    temp_input = os.path.join(working_dir, "similarity-scores.txt")
    if temp_input != input_file:
        shutil.copy2(input_file, temp_input)
    
    original_dir = os.getcwd()
    try:
        # Change to working directory
        os.chdir(working_dir)
        
        # Run the script
        command = ["python3", script_path, "-t", str(threshold)]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: cluster-scores.py returned error: {result.returncode}")
            print(f"STDERR: {result.stderr}")
        
        # Check if clusters.json was created
        if os.path.exists("clusters.json"):
            # Copy to output file
            shutil.copy2("clusters.json", output_file)
            print(f"Generated {output_file}")
            return True
        else:
            print("Error: clusters.json not found")
            return False
    
    finally:
        os.chdir(original_dir)
        # Clean up
        if os.path.exists(temp_input) and temp_input != input_file:
            os.remove(temp_input)
        
        temp_output = os.path.join(working_dir, "clusters.json")
        if os.path.exists(temp_output):
            os.remove(temp_output)

def extract_file_content(file_path, max_length=50):
    """Extract meaningful content from a file for display purposes"""
    try:
        print(f"DEBUG: Reading content from {file_path}")
        if not os.path.exists(file_path):
            print(f"DEBUG: File not found: {file_path}")
            return os.path.basename(file_path)
            
        with open(file_path, 'r') as f:
            content = f.read().strip()
            result = content[:50]
            print(f"DEBUG: Content: {result}")
            return result
    except Exception as e:
        print(f"DEBUG: Error reading {file_path}: {str(e)}")
        return os.path.basename(file_path)

def name_cluster_by_common_terms(items, content_dict=None):
    """Name a cluster based on common terms found in its items"""
    all_content = []
    for item in items:
        path = item.get("path", "")
        item_name = item.get("name", "")
        item_key = os.path.basename(path)
        content = None
        
        # Try all possible ways to get content
        if content_dict and item_key in content_dict:
            content = content_dict[item_key]
        elif content_dict and path in content_dict:
            content = content_dict[path]
        elif path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    content = f.read()
            except:
                pass
                
        if not content:
            content = item_name
            
        all_content.append(content)
    
    if not all_content:
        return "Cluster"
    
    # Extract meaningful words
    from collections import Counter
    import re
    
    words = []
    for content in all_content:
        words.extend(re.findall(r'\b[a-zA-Z]{4,}\b', content.lower()))
    
    # Expanded stopwords list
    stopwords = {'the', 'and', 'was', 'for', 'that', 'this', 'with', 'have', 
                'were', 'they', 'our', 'what', 'when', 'from', 'your', 'been'}
    words = [w for w in words if w not in stopwords]
    
    # Get most common terms
    most_common = Counter(words).most_common(3)
    if most_common:
        terms = [term for term, _ in most_common]
        return f"Cluster: {', '.join(terms)}"
    else:
        return "Cluster"

def create_circle_json(clusters_json_path, output_file, content_dict=None):

    if not os.path.exists(clusters_json_path):
        print(f"Error: Clusters file not found: {clusters_json_path}")
        return False
    
    try:
        with open(clusters_json_path, 'r') as f:
            clusters_data = json.load(f)
        
        # Convert to circle packing format
        circle_data = {
            "name": "root",
            "children": []
        }
        
        if "children" in clusters_data:
            for i, cluster in enumerate(clusters_data["children"]):
                # cluster_node = {
                #     "name": name_cluster_by_common_terms(cluster.get("children", [])),  # Using content-based name
                #     "children": []
                # }
                cluster_node = {
                    "name": name_cluster_by_common_terms(cluster.get("children", []), content_dict),  # Pass content_dict
                    "children": []
                }
                
                if "children" in cluster:
                    for j, item in enumerate(cluster["children"]):
                        item_path = item.get("path", "")
                        item_name_key = os.path.basename(item_path)  # This is the UUID filename
                        
                        # Try all possible ways to get meaningful content
                        if content_dict and item_name_key in content_dict:
                            item_name = content_dict[item_name_key]
                            print(f"Using content from dictionary: {item_name[:20]}...")
                        elif content_dict and item_path in content_dict:
                            item_name = content_dict[item_path]
                        elif os.path.exists(item_path):
                            # Direct file access as fallback
                            with open(item_path, 'r') as f:
                                item_name = f.readline().strip()[:50]
                        else:
                            # Last resort - use the name from JSON
                            item_name = item.get("name", f"Item {j+1}")
                                
                            # Add to the cluster node with score
                            try:
                                item_score = float(item.get("score", 0.5))
                            except (ValueError, TypeError):
                                item_score = 0.5
                            
                            cluster_node["children"].append({
                                "name": item_name,
                                "size": int(100 + item_score * 1900)
                            })
                
                circle_data["children"].append(cluster_node)
        
        with open(output_file, 'w') as f:
            json.dump(circle_data, f, indent=2)
        
        print(f"Created circle.json: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error creating circle.json: {e}")
        return False

def create_d3_cluster_json(clusters_json_path, output_file, content_dict=None):
    """
    Create a D3 cluster JSON from a clusters.json file
    
    Args:
        clusters_json_path (str): Path to the clusters.json file
        output_file (str): Path to write the D3 cluster file
    """
    if not os.path.exists(clusters_json_path):
        print(f"Error: Clusters file not found: {clusters_json_path}")
        return False
    
    try:
        with open(clusters_json_path, 'r') as f:
            clusters_data = json.load(f)
        
        # Create D3 force-directed graph format
        nodes = [{"name": "Root", "group": 1}]
        links = []
    
        if "children" in clusters_data:
            # First create cluster nodes
            for i, cluster in enumerate(clusters_data["children"]):
                cluster_id = len(nodes)
                #cluster_name = name_cluster_by_common_terms(cluster.get("children", []))
                cluster_name = name_cluster_by_common_terms(cluster.get("children", []), content_dict)
                nodes.append({"name": cluster_name, "group": 2})
                links.append({"source": 0, "target": cluster_id, "value": 2})  # Link to root
                
                # Then create item nodes that link to their parent cluster
                if "children" in cluster:
                    for j, item in enumerate(cluster["children"]):
                        item_id = len(nodes)
                        item_path = item.get("path", "")
                        
                        # Extract content for better naming
                        try:
                            if content_dict and os.path.basename(item_path) in content_dict:
                                item_name = content_dict[os.path.basename(item_path)]
                            elif content_dict and item_path in content_dict:
                                item_name = content_dict[item_path]
                            elif item_path and os.path.exists(item_path):
                                with open(item_path, 'r') as f:
                                    first_line = f.readline().strip()[:50]
                                    item_name = first_line if first_line else os.path.basename(item_path)
                            else:
                                item_name = item.get("name", f"Item {j+1}")
                        except:
                            item_name = item.get("name", f"Item {j+1}")
                        
                        nodes.append({"name": item_name, "group": 3})
                        links.append({"source": cluster_id, "target": item_id, "value": 1})  # Link to parent cluster
        
        d3_data = {"nodes": nodes, "links": links}
        with open(output_file, 'w') as f:
            json.dump(d3_data, f, indent=2)
        
        print(f"Created D3 cluster format: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error creating D3 cluster JSON: {e}")
        return False
    
def run_circle_packing(results_dir, sim_type):
    """Run the original circle-packing visualization"""
    project_root = Path(__file__).parent.parent
    circle_packing_script = project_root / "tika-similarity" / "tikasimilarity" / "cluster" / "circle-packing.py"
    
    if not os.path.exists(circle_packing_script):
        print(f"Error: Circle packing script not found: {circle_packing_script}")
        return False
        
    # Create a properly formatted similarity-scores.txt for the script
    txt_file = results_dir / f"{sim_type}_similarity-scores.txt"
    circle_json = results_dir / f"{sim_type}_metadata_circle.json"
    
    # Need to convert your CSV to the expected format
    csv_file = results_dir / f"{sim_type}_similarity.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        return False
    
    # Convert to the specific format needed by circle-packing.py
    with open(csv_file, 'r') as f_in, open(txt_file, 'w') as f_out:
        reader = csv.reader(f_in)
        header = next(reader, None)  # Skip header
        
        for row in reader:
            if len(row) >= 3:
                file1, file2, score = row[0], row[1], float(row[2])
                # Format needed by circle-packing.py:
                f_out.write(f"{os.path.basename(file1)},{score},{{}}\n")
    
    # Change to results directory
    original_dir = os.getcwd()
    os.chdir(results_dir)
    
    try:
        # Run the circle packing script
        command = [sys.executable, str(circle_packing_script)]
        subprocess.run(command, check=False)
        
        # Rename the output file
        if os.path.exists("circle.json"):
            shutil.move("circle.json", circle_json)
            print(f"Created metadata circle visualization: {circle_json}")
            return True
        else:
            print("Error: circle.json not created")
            return False
    finally:
        os.chdir(original_dir)

def main():
    # Get project paths
    project_root = Path(__file__).parent.parent
    results_dir = project_root / "similarity-results"
    tika_cluster_dir = project_root / "tika-similarity" / "tikasimilarity" / "cluster"
    
    # Create results directory if it doesn't exist
    results_dir.mkdir(exist_ok=True)
    document_content = {}
    
    # Start of main() function after loading document_content
    print(f"Loaded {len(document_content)} document contents:")
    for i, (key, value) in enumerate(list(document_content.items())[:5]):
        print(f"  Sample {i+1}: {key} -> {value[:30]}")
    
    # Get actual content from files in haunted_places directory
    data_dir = project_root / "data" / "haunted_places"
    if data_dir.exists():
        print("Pre-loading document content...")
        for file_path in data_dir.glob("*"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r') as f:
                        first_line = f.readline().strip()
                        content = first_line[:50]
                        # Store with both full path and basename as keys
                        document_content[str(file_path)] = content
                        document_content[file_path.name] = content
                        # Also store without extension
                        document_content[file_path.stem] = content
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
    
    # Define the similarity types to process
    similarity_types = [
        "cosine_similarity",
        "jaccard_similarity",
        "edit_value_similarity"  # Using edit_value instead of edit_distance
    ]
    
    for sim_type in similarity_types:
        print(f"\n===== Processing {sim_type} =====")
        
        # Define paths for this similarity type
        csv_file = results_dir / f"{sim_type}.csv"
        txt_file = results_dir / f"{sim_type}.txt"
        
        # Skip if CSV file doesn't exist
        if not csv_file.exists():
            print(f"Warning: CSV file not found: {csv_file}")
            continue
            
        # Step 1: Convert CSV to similarity scores format
        print(f"Converting CSV to similarity scores format")
        if not convert_csv_to_similarity_scores(str(csv_file), str(txt_file)):
            print(f"Error converting {csv_file} to similarity scores format")
            continue
        
        print(f"Running clustering scripts for {sim_type}")
        
        # Step 2: Run cluster-scores.py to generate clusters.json
        cluster_scores_script = tika_cluster_dir / "cluster-scores.py"
        clusters_json = results_dir / f"{sim_type}_clusters.json"
        print(f"  Generating clusters.json")
        run_cluster_scores(
            str(cluster_scores_script), 
            str(results_dir),
            str(txt_file),
            str(clusters_json),
            0.01  # Threshold
        )
        
        # Step 3: Create circle.json for circle packing visualization
        circle_json = results_dir / f"{sim_type}_circle.json"
        print(f"  Creating circle.json for circle packing visualization")
        create_circle_json(str(clusters_json), str(circle_json), document_content)
        
        # Step 4: Create D3 JSON for cluster visualization
        cluster_d3_json = results_dir / f"{sim_type}_cluster_d3.json"
        print(f"  Creating D3 cluster visualization format")
        create_d3_cluster_json(str(clusters_json), str(cluster_d3_json), document_content)
        
         # Step 5: Add the circle packing visualization (original Tika method)
        print(f"  Creating metadata-based circle packing visualization")
        run_circle_packing(results_dir, sim_type)
    
    print("\nAll JSON files generated successfully in:", results_dir)
    print("The following files can be used with visualization HTML files:")
    print("  *_clusters.json - Basic cluster visualization")
    print("  *_circle.json - Circle packing visualization")
    print("  *_cluster_d3.json - D3 cluster visualization")

if __name__ == "__main__":
    main()