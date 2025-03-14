import pandas as pd
import argparse

def convert_csv_to_tsv(input_file, output_file):
    df = pd.read_csv(input_file)
    df.to_csv(output_file, sep='\t', index=False)
    print(f"Converted {input_file} to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV to TSV")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output TSV file")
    args = parser.parse_args()
    
    convert_csv_to_tsv(args.input, args.output)
