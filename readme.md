# Haunted Places Analysis Project

This project analyzes a dataset of haunted places to identify patterns and similarities using natural language processing and data visualization techniques.

## Workflow

The analysis workflow consists of the following steps:

1.  **Data Conversion**: Convert the input TSV file to JSON format.
2.  **Data Preparation**: Break the JSON data into individual text files for analysis.
3.  **Similarity Analysis**: Calculate similarity scores between the text files using cosine similarity, Jaccard index, and edit distance.
4.  **Clustering**: Group similar haunted places based on the calculated similarity scores.
5.  **Visualization**: Generate interactive visualizations to explore the clusters and patterns in the data.

## Scripts

The project includes the following scripts:

*   `main.py`: Orchestrates the entire analysis workflow.
*   `convert-tsv-to-json.py`: Converts a TSV file to JSON format.
*   `break-json.py`: Breaks a JSON file into individual text files.
*   `run-tika-similarity.py`: Runs similarity analysis using Tika similarity algorithms.
*   `generate-cluster-scores.py`: Generates cluster data from similarity scores.
*   `visualize-results.py`: Sets up a web server to visualize the results.

## Usage

### Prerequisites

*   Python 3.6+
*   Required Python packages (install using `pip install -r requirements.txt`)

### Setup

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd haunted-places-analysis
    ```

2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Analysis

To run the entire analysis workflow, use the `main.py` script:

1. Delete all of the existing files:
- everything in the `data` folder
- everything in the `datasets` folder
- everything in the `similarity-results` folder
- everything in the `cluster-results` folder


2. Upload your TSV file to the `datasets` folder.

3. Rename the TSV file to `merged_dataset.tsv`. ## TODO: Update this to be a command line argument

4. Run the `main.py` script from the main project directory:

```bash
python main.py
```

## List of Commands

Here's a list of commands you can use to run the analysis, along with their descriptions:

*   `python main.py`: Runs the entire analysis workflow, including TSV to JSON conversion, breaking JSON into files, similarity analysis, clustering, and visualization setup.

*   `python main.py --tsv-file <path_to_tsv_file>`: Runs the entire analysis workflow, using the specified TSV file as input. Replace `<path_to_tsv_file>` with the actual path to your TSV file.

*   `python main.py --skip-convert`: Skips the TSV to JSON conversion step. Assumes a `haunted_places.json` file already exists in the `data` directory.

*   `python main.py --skip-break`: Skips the breaking JSON into individual files step. Assumes individual text files already exist in the `data/haunted_places` directory.

*   `python main.py --skip-similarity`: Skips the similarity analysis step. Assumes similarity results already exist in the `similarity-results` directory.

*   `python main.py --skip-clustering`: Skips the clustering step. Assumes cluster results already exist in the `cluster-results` directory.

*   `python main.py --skip-visualization`: Skips the visualization setup step.

You can combine these `--skip-*` arguments to skip multiple steps. For example:

*   `python main.py --skip-convert --skip-break`: Skips the TSV to JSON conversion and breaking JSON into files steps.

*   `python main.py --skip-similarity --skip-clustering --skip-visualization`: Skips the similarity analysis, clustering, and visualization setup steps.



