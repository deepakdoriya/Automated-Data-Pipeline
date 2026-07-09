# https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv

import requests, argparse, os, csv, json
from statistics import mean, median, multimode, stdev

clean_help="drop_mv: removes rows with missing values" \
            "drop_dr: remove duplicate rows only" \
            "all: remove rows with missing values as well as duplicate rows"


parser=argparse.ArgumentParser(description="a CLI tool that downloads a CSV from a URL, cleans it, computes summary statistics, and outputs the results to a file")

parser.add_argument("--url", type=str, help="URL", default="https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
# parser.add_argument("--url", type=str, help="URL",)
parser.add_argument("--output", type=str, default="data/", help="Output folder path")
parser.add_argument("--clean", type=str, help=clean_help, choices=["drop_mv", "drop_dr", "all"], default="all")
parser.add_argument("--stats", type=str, help="Calculate stats Yes(y)/No(n)", choices=["Yes", "y", "No", "n"], default="Yes")
args=parser.parse_args()

def download_csv(url, output):
        
    response=requests.get(url, timeout=10)
    response.raise_for_status()

    if not os.path.exists(output):
        os.makedirs(output)
    
    d_path=os.path.join(output,"raw_data.csv")
    
    with open(d_path,"wb") as data:
        data.write(response.content)
    
    print("Download Successful!!")


def rm_missing(r_path,c_path):

    out=[]
    fieldname=None

    if not is_empty_file(r_path):
        with open(r_path, "r") as file:
            try:
                reader=csv.DictReader(file)
            except csv.Error:
                print("Error: Failed to parse CSV. Please verify that the source file is a valid CSV text file.")
            else:
                fieldname=reader.fieldnames
                for row in reader:
                    is_missing=False
                    for key,value in row.items():
                        if value.strip()=="":
                            is_missing=True
                            break
                    if not is_missing:
                        out.append(row)
    else:
        print("Error: The dataset is empty or corrupted.")
    
    try:
        with open(c_path, "w", newline="") as file:
            writer=csv.DictWriter(file,fieldnames=fieldname)
            writer.writeheader()
            writer.writerows(out)
        print("Successfully Removed Rows with Missing Values!!")
    except (FileNotFoundError, PermissionError):
        print("Error: Permission denied. Please check if the output files are open in another program or if you have write access to the folder.")


def rm_duplicate(r_path,c_path):
    
    out=set()
    fieldname=None
    
    if not is_empty_file(r_path):
        with open(r_path, "r") as file:
            try:
                reader=csv.DictReader(file)
            except csv.Error:
                print("Error: Failed to parse CSV. Please verify that the source file is a valid CSV text file.")
            else:
                fieldname=reader.fieldnames
                for row in reader:
                    dict_tuple=tuple(row.items())
                    out.add(dict_tuple)
    else:
        print("Error: The dataset is empty or corrupted.")
        

    
    out= list(out)

    try:
        with open(c_path, "w", newline="") as file:
            writer=csv.DictWriter(file,fieldnames=fieldname)
            writer.writeheader()
            for row in out:
                writer.writerow(dict(row))  
        print("Successfully Removed Duplicate Rows!!")
    except (FileNotFoundError, PermissionError):
        print("Error: Permission denied. Please check if the output files are open in another program or if you have write access to the folder.")
        

def statistics_json(r_path,s_path):
    stats={}

    if not is_empty_file(r_path):
        with open(r_path, "r") as file:
            try:
                reader=csv.DictReader(file)
            except csv.Error:
                print("Error: Failed to parse CSV. Please verify that the source file is a valid CSV text file.")
            else:
                headers=reader.fieldnames

                dict_list=[]
                for row in reader:
                    dict_list.append(row)
                
                for header in headers:
                    tmp=[]
                    for dict in dict_list:
                        try: 
                            dict[header]=float(dict[header])
                        except ValueError:
                            continue
                        else:
                            tmp.append(dict[header])
                    n=len(tmp)
                    mode=multimode(tmp)
                    if n==0 : continue
                    stats[f"{header} average"]= mean(tmp)
                    stats[f"{header} median"]= median(tmp)
                    if n>1 and len(mode)==n:
                        stats[f"{header} mode"]= "No unique Value"
                    else:
                        stats[f"{header} mode"]= mode
                    if n>1:
                        stats[f"{header} std_dev"]= stdev(tmp)
                    else:
                        stats[f"{header} std_dev"]= "Insufficient Data"
    else:
        print("Error: The dataset is empty or corrupted.")

    try:
        with open(s_path, "w") as file:
            json.dump(stats, file, indent=2)
    except (FileNotFoundError, PermissionError):
        print("Error: Permission denied. Please check if the output files are open in another program or if you have write access to the folder.")


def is_empty_file(f_path):
    
    rows=[]
    if os.path.exists(f_path):
        with open(f_path) as f:
            try:
                reader=csv.DictReader(f)
            except csv.Error:
                print("Error: Failed to parse CSV. Please verify that the source file is a valid CSV text file.")
            else:
                for row in reader:
                    rows.append(row)
            
        if not os.path.getsize(f_path)==0 or len(rows)!=0:
            return False
    return True
    

def main():
    r_path=os.path.join(args.output,"raw_data.csv")
    c_path=os.path.join(args.output,"cleaned_data.csv")
    
    try: 
        download_csv(args.url, args.output)
    except requests.exceptions.RequestException as error:
        print(f"Network Error: {error}")
        return 
    
    if args.clean=="drop_mv":
        rm_missing(r_path,c_path)
    elif args.clean=="drop_dr":
        rm_duplicate(r_path,c_path)
    elif args.clean=="all":
        rm_missing(r_path,c_path)
        rm_duplicate(c_path,c_path)
    if args.stats in {"Yes", "y"}:
        s_path=os.path.join(args.output,"stats.json")

        if not is_empty_file(c_path):
            statistics_json(c_path,s_path)
        else:
            print("Warning: No rows remained after data cleaning. Skipping statistics calculation.")

if __name__=="__main__":
    main()