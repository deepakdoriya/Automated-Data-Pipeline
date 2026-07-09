# https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv

import requests
import argparse
import os
import csv

clean_help="drop_mv: removes rows with missing values" \
            "drop_dr: remove duplicate rows only" \
            "all: remove rows with missing values as well as duplicate rows"


parser=argparse.ArgumentParser(description="a CLI tool that downloads a CSV from a URL, cleans it, computes summary statistics, and outputs the results to a file")

parser.add_argument("--url", type=str, help="URL", default="https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
# parser.add_argument("--url", type=str, help="URL",)
parser.add_argument("--output", type=str, default="data/", help="Output folder path")
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

        d_path=os.path.join(output,"raw_data.csv")
        with open(d_path,"wb") as data:
            data.write(data_bytes)


def rm_missing(r_path,c_path):

    out=[]
    fieldname=None
    with open(r_path, "r") as file:
        reader=csv.DictReader(file)
        fieldname=reader.fieldnames
        for row in reader:
            is_missing=False
            for key,value in row.items():
                if value.strip()=="":
                    is_missing=True
                    break
            for key, value in row.items():
                try:
                    if isinstance(value,float):
                        row[key]=float(value)
                    elif isinstance(value,int):
                        row[key]=int(value)
                except ValueError:
                    continue
            if not is_missing:
                out.append(row)
    
    with open(c_path, "w") as file:
        writer=csv.DictWriter(file,fieldnames=fieldname)
        writer.writeheader()
        writer.writerows(out)

    print("Successfully Removed Rows with Missing Values!!")

def rm_duplicate(r_path,c_path):
    
    out=set()
    fieldname=None
    with open(r_path, "r") as file:
        reader=csv.DictReader(file)
        fieldname=reader.fieldnames
        for row in reader:
            for key, value in row.items():
                try:
                    if isinstance(value,float):
                        row[key]=float(value)
                    elif isinstance(value,int):
                        row[key]=int(value)
                except ValueError:
                    continue
            dict_tuple=tuple(row.items())
            out.add(dict_tuple)
    
    out= sorted(list(out))

    with open(c_path, "w") as file:
        writer=csv.DictWriter(file,fieldnames=fieldname)
        writer.writeheader()
        for row in out:
            writer.writerow(dict(row))  

    print("Successfully Removed Duplicate Rows!!")

def main():
    r_path=os.path.join(args.output,"raw_data.csv")
    c_path=os.path.join(args.output,"cleaned_data.csv")
    download_csv(args.url, args.output)
    if args.clean=="drop_mv":
        rm_missing(r_path,c_path)
    elif args.clean=="drop_dr":
        rm_duplicate(r_path,c_path)
    elif args.clean=="all":
        rm_missing(r_path,c_path)
        rm_duplicate(c_path,c_path)

if __name__=="__main__":
    main()