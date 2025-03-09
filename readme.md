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

```bash
python main.py --tsv-file datasets/your_data.tsv