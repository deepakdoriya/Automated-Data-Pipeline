import requests
import argparse
import os

clean_help="drop_mv: removes rows with missing values" \
            "drop_dr: remove duplicate rows only" \
            "all: remove rows with missing values as well as duplicate rows"


parser=argparse.ArgumentParser(description="a CLI tool that downloads a CSV from a URL, cleans it, computes summary statistics, and outputs the results to a file")

parser.add_argument("--url", type=str, help="URL")
parser.add_argument("--output", type=str, default="data/cleaned_data.csv", help="Output file path")
parser.add_argument("--clean", type=str, help=clean_help, choices=["drop_mv", "drop_dr", "all"], default="all")
args=parser.parse_args()

def download_csv(url, output):
    try: 
        response=requests.get(url, timeout=10)
        response.raise_for_status()
    
    except requests.exceptions.RequestException as error:
        print(f"Network Error: {error}")

    else:
        data_bytes=response.content
        print("Download Successful!!")

        dir=os.path.dirname(output)
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(output, "wb") as data:
            data.write(data_bytes)

download_csv(args.url, args.output)


