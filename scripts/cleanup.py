import shutil
from pathlib import Path

def delete_path(path):
    if path.exists():
        if path.is_file():
            path.unlink()
            print(f"Deleted file: {path}")
        elif path.is_dir():
            shutil.rmtree(path)
            print(f"Deleted directory: {path}")

def main():
    import shutil
    from pathlib import Path

    project_root = Path(__file__).parent.parent

    paths_to_delete = [
        project_root / "datasets" / "merged_dataset.json",
        project_root / "datasets" / "column_headers.txt",
        project_root / "data" / "haunted_places",
        project_root / "data" / "sample_files",
        project_root / "similarity-results",
        project_root / "visualizations"
    ]

    for path in paths_to_delete:
        if path.exists():
            if path.is_file():
                path.unlink()
                print(f"Deleted file: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"Deleted directory: {path}")
        else:
            print(f"Path not found, skipping: {path}")

if __name__ == "__main__":
    main()