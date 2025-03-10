import os
import json
import shutil
import webbrowser
import http.server
import socketserver
import random
import re
from pathlib import Path

def enhance_cluster_data(data):
    """Add necessary fields (name, size) to cluster data for visualization"""
    if not isinstance(data, dict) or "children" not in data:
        print("Warning: Invalid cluster data format")
        return data
        
    # Process each cluster
    for cluster in data["children"]:
        if "children" in cluster:
            for i, item in enumerate(cluster["children"]):
                # Add name if missing
                if "name" not in item:
                    if "path" in item:
                        item["name"] = os.path.basename(item["path"])
                    else:
                        item["name"] = f"Item_{i+1}"
                
                # Add size for circle packing visualization
                if "score" in item:
                    # Make sure score is converted to numeric value
                    try:
                        score_value = float(item["score"])
                        # Scale score to reasonable size (100-2000)
                        item["size"] = int(100 + score_value * 1900)
                    except (ValueError, TypeError):
                        item["size"] = 500  # Default size
                else:
                    item["size"] = 500  # Default size
    
    return data

def copy_dependencies(tika_html_dir, viz_dir):
    """Copy all necessary dependencies for visualizations"""
    # Create js directory if needed
    js_dir = viz_dir / "js"
    js_dir.mkdir(exist_ok=True)
    
    # Create css directory if needed
    css_dir = viz_dir / "css"
    css_dir.mkdir(exist_ok=True)
    
    # Copy JS files from tika
    tika_js_dir = tika_html_dir.parent / "js"
    if tika_js_dir.exists():
        for js_file in tika_js_dir.glob("*.js"):
            shutil.copy2(js_file, js_dir)
        print(f"Copied JS files to {js_dir}")
    
    # Copy CSS files from tika
    tika_css_dir = tika_html_dir.parent / "css"
    if tika_css_dir.exists():
        for css_file in tika_css_dir.glob("*.css"):
            shutil.copy2(css_file, css_dir)
        print(f"Copied CSS files to {css_dir}")
    
    # Create local d3.js if it doesn't exist
    d3_path = js_dir / "d3.v3.min.js"
    if not d3_path.exists():
        # Create a simple script that loads D3 from CDN
        with open(d3_path, "w") as f:
            f.write("""
// Local proxy for D3 v3
document.write('<script src="https://d3js.org/d3.v3.min.js"></script>');
""")
        print(f"Created D3.js proxy at {d3_path}")
    
    # Create a helper script for debugging
    debug_js = js_dir / "debug-helper.js"
    with open(debug_js, "w") as f:
        f.write("""
console.log("Debug helper loaded");

// Log all errors
window.onerror = function(msg, url, line) {
    console.error("Error:", msg, "at", url, "line", line);
    alert("Error loading visualization: " + msg);
    return false;
};

// Debug JSON loading
if (window.d3) {
    var originalD3Json = d3.json;
    d3.json = function(url, callback) {
        console.log("Loading JSON from:", url);
        
        originalD3Json(url, function(error, data) {
            if (error) {
                console.error("Error loading JSON:", error);
                alert("Failed to load data from " + url + ": " + error);
            } else {
                console.log("Successfully loaded data:", data);
            }
            callback(error, data);
        });
    };
}
""")
    print(f"Created debugging helper at {debug_js}")

def fix_html_references(viz_dir):
    """Fix references in HTML files to use local resources"""
    for html_file in viz_dir.glob("*.html"):
        print(f"Fixing references in {html_file}")
    
        with open(html_file, "r", encoding='utf-8', errors='ignore') as f:
            content = f.read()
    
        # Replace CDN references with local ones
        content = content.replace('http://d3js.org/d3.v3.min.js', 'js/d3.v3.min.js')
    
        # Add debugging script
        debug_script = """
<script src="js/debug-helper.js"></script>
"""
        if "<head>" in content:
            content = content.replace("</head>", debug_script + "</head>")
        else:
            content = debug_script + content
    
        # Add basic error handling directly in the HTML
        error_handler = """
<div id="error-display" style="display:none; color:red; border:1px solid red; padding:10px; margin:10px;">
  Error loading visualization. Check console for details.
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    // Check if visualization loaded successfully
    var viz = document.querySelector('svg');
    if (!viz || viz.childElementCount === 0) {
      document.getElementById('error-display').style.display = 'block';
      document.getElementById('error-display').innerHTML += 
        '<p>Failed to render visualization. Possible reasons:</p>' +
        '<ul>' +
        '<li>JSON data format incorrect</li>' +
        '<li>Missing dependencies</li>' +
        '<li>JavaScript errors</li>' +
        '</ul>';
    }
  }, 2000);
});
</script>
"""
        if "</body>" in content:
            content = content.replace("</body>", error_handler + "</body>")
        else:
            content += error_handler
    
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(content)

def prepare_json_for_visualization(data, viz_type):
    """Prepare JSON data for specific visualization types"""
    enhanced_data = enhance_cluster_data(data)
    
    if viz_type == "dynamic-circlepacking":
        # Dynamic cluster needs specific format
        formatted_data = {
            "name": "Root",
            "children": enhanced_data.get("children", [])
        }
    elif viz_type == "cluster-d3":
        # Cluster-d3 needs a specific format with name and children properties
        children = enhanced_data.get("children", [])
        
        # LIMIT THE NUMBER OF CLUSTERS - only take the first 50 clusters that have at least 2 items
        limited_children = []
        for cluster in children:
            if "children" in cluster and len(cluster["children"]) >= 2:  # Only include clusters with at least 2 items
                if "name" not in cluster:
                    cluster["name"] = f"Cluster_{cluster.get('id', 'unknown')}"
                
                # Limit items in each cluster if there are too many
                if len(cluster["children"]) > 10:
                    cluster["children"] = cluster["children"][:10]  # Take only first 10 items
                
                # Ensure each item has a name
                for item in cluster["children"]:
                    if "name" not in item and "path" in item:
                        item["name"] = os.path.basename(item["path"])
                
                limited_children.append(cluster)
                
                # Stop after we have 50 clusters
                if len(limited_children) >= 50:
                    break
        
        formatted_data = {
            "name": "clusters",
            "children": limited_children
        }
    else:
        # Default format for circle packing
        formatted_data = enhanced_data
    
    return formatted_data

def setup_visualization_directory():
    """Set up the visualization directory structure"""
    # Get project paths
    project_root = Path(__file__).parent.parent
    similarity_results = project_root / "similarity-results"
    tika_html_dir = project_root / "tika-similarity" / "html"
    
    # Create visualization directories
    viz_root = project_root / "visualizations"
    viz_root.mkdir(exist_ok=True)
    
    # Dictionary to track visualization directories
    viz_dirs = {}
    
    # Process each similarity type
    for sim_type in ["cosine", "jaccard", "edit_value"]:
        # Create directory for this similarity type
        viz_dir = viz_root / sim_type
        viz_dir.mkdir(exist_ok=True)
        viz_dirs[sim_type] = viz_dir
        
        # Copy dependencies first
        copy_dependencies(tika_html_dir, viz_dir)
        
        # Copy HTML visualization files
        html_files = ["circlepacking.html", "cluster-d3.html", "dynamic-circlepacking.html"]
        for html_file in html_files:
            src_file = tika_html_dir / html_file
            if src_file.exists():
                shutil.copy2(src_file, viz_dir / html_file)
                print(f"Copied {html_file} to {viz_dir}")
    
        # Fix HTML references
        fix_html_references(viz_dir)
    
        # Process the clusters JSON file
        clusters_file = similarity_results / f"{sim_type}_similarity_clusters.json"
        if clusters_file.exists():
            try:
                with open(clusters_file, 'r') as f:
                    data = json.load(f)
            
                # Save specialized formats for different visualizations
                viz_types = ["circlepacking", "cluster-d3", "dynamic-circlepacking"]  # Updated to match HTML files
                for viz_type in viz_types:
                    formatted_data = prepare_json_for_visualization(data, viz_type)
                
                    # Determine output file name
                    if viz_type == "circlepacking":
                        output_file = viz_dir / "circle.json"
                    elif viz_type == "cluster-d3":
                        output_file = viz_dir / "clusters.json"
                    elif viz_type == "dynamic-circlepacking":  # Changed from dynamic-cluster
                        # Note: You need to check what file dynamic-circlepacking.html is looking for
                        # It's likely circle.json or dynamic_circle.json
                        output_file = viz_dir / "dynamic_circle.json"  # Adjust this based on what you find
                    
                    # Write the file
                    with open(output_file, 'w') as f:
                        json.dump(formatted_data, f, indent=2)
                    print(f"Created JSON for {viz_type} in {output_file}")
            
                # Create a backup copy with clear naming
                with open(viz_dir / f"{sim_type}_data.json", 'w') as f:
                    json.dump(data, f, indent=2)
            
            except json.JSONDecodeError:
                print(f"Error: Could not parse {clusters_file} as valid JSON")
            except Exception as e:
                print(f"Error processing {clusters_file}: {str(e)}")
        else:
            print(f"Warning: {clusters_file} does not exist")

    # Create the main index.html
    create_main_index(viz_root, viz_dirs)

    return viz_root

def create_main_index(viz_root, viz_dirs):
    """Create a main index.html to navigate between visualizations"""
        
    links_html = ""
    for sim_type, viz_dir in viz_dirs.items():
        type_name = sim_type.replace("_", " ").title()
        rel_path = os.path.relpath(viz_dir, viz_root)
        
        links_html += f"""
        <div class="viz-type">
            <h2>{type_name}</h2>
            <ul>
                <li><a href="{rel_path}/circlepacking.html" target="_blank">Circle Packing Visualization</a></li>
                <li><a href="{rel_path}/cluster-d3.html" target="_blank">Cluster Visualization</a></li>
                <li><a href="{rel_path}/dynamic-circlepacking.html" target="_blank">Dynamic Cluster Visualization</a></li>
                <li><a href="{rel_path}/circlepacking.html?file={sim_type}_similarity_metadata_circle.json" target="_blank">
                    Metadata Circle Packing</a></li>
            </ul>
        </div>
        """
    
    index_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Haunted Places Similarity Visualizations</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
        .viz-type {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .viz-type h2 {{ color: #0066cc; margin-top: 0; }}
        ul {{ padding-left: 20px; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .description {{ background-color: #f9f9f9; padding: 15px; margin-bottom: 30px; border-left: 4px solid #0066cc; }}
    </style>
</head>
<body>
    <h1>Haunted Places Similarity Visualizations</h1>
    
    <div class="description">
        <p>This page provides visualizations of similarity analyses for haunted places documents.</p>
        <p>Each visualization type shows different aspects of how the documents relate to each other.</p>
        <ul>
            <li><strong>Circle Packing:</strong> Shows document clusters as nested circles</li>
            <li><strong>Cluster Visualization:</strong> Shows document clusters in a node graph</li>
            <li><strong>Dynamic Cluster:</strong> Shows an interactive cluster visualization</li>
        </ul>
        <p><em>Note: If visualizations don't load correctly, try using a different browser or check the browser console for errors.</em></p>
    </div>
    
    {links_html}
    
    <div style="margin-top: 30px; text-align: center; color: #666; font-size: 0.9em;">
        <p>Generated using Tika Similarity Analysis</p>
    </div>
</body>
</html>
    """
    
    with open(viz_root / "index.html", 'w') as f:
        f.write(index_content)
    
    print("Created main index.html navigation page")

def start_visualization_server(directory):
    """Start an HTTP server for viewing the visualizations"""
    os.chdir(directory)
    
    # Try to find an available port starting from 8000
    port = 8000
    max_attempts = 10
    
    for attempt in range(max_attempts):
        try:
            # Try a range of ports to avoid conflicts
            port = 8000 + random.randint(0, 1000)
            handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", port), handler)
            
            print(f"\nStarting server at http://localhost:{port}")
            print("Press Ctrl+C to stop the server")
            
            # Open the browser
            webbrowser.open(f"http://localhost:{port}/index.html")
            
            # Start server
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
                break
            finally:
                httpd.shutdown()  # Ensure server shuts down
                httpd.server_close()  # Close the socket
            
            break
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"Port {port} is already in use, trying another port...")
                if attempt == max_attempts - 1:
                    print("Could not find an available port after multiple attempts.")
                    print("Please try again later or manually open the index.html file in your browser.")
                    print(f"Visualization files are available at: {directory}")
                    return
            else:
                print(f"Server error: {e}")
                return
        except Exception as e:
            print(f"Server error: {e}")
            return

def open_visualizations_without_server(directory):
    """Open the index.html file directly without starting a server"""
    index_path = os.path.join(directory, "index.html")
    if os.path.exists(index_path):
        file_url = 'file://' + os.path.abspath(index_path)
        print(f"Opening {file_url} in browser")
        webbrowser.open(file_url)
    else:
        print(f"Error: Could not find {index_path}")

if __name__ == "__main__":
    print("Setting up visualization directory...")
    viz_dir = setup_visualization_directory()
    
    try:
        print("\nStarting visualization server...")
        start_visualization_server(viz_dir)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Trying to open visualizations directly...")
        open_visualizations_without_server(viz_dir)