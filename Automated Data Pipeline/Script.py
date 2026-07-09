# https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv

import requests, argparse, os, csv, json

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
    with open(r_path, "r") as file:
        reader=csv.DictReader(file)
        fieldname=reader.fieldnames
        for row in reader:
            is_missing=False
            for key,value in row.items():
                if value.strip()=="":
                    is_missing=True
                    break
            if not is_missing:
                out.append(row)
    
    with open(c_path, "w", newline="") as file:
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
            dict_tuple=tuple(row.items())
            out.add(dict_tuple)
    
    out= list(out)

    with open(c_path, "w", newline="") as file:
        writer=csv.DictWriter(file,fieldnames=fieldname)
        writer.writeheader()
        for row in out:
            writer.writerow(dict(row))  

    print("Successfully Removed Duplicate Rows!!")

def statistics_json(r_path,s_path):
    stats={}
    with open(r_path, "r") as file:
        reader=csv.DictReader(file)
        headers=reader.fieldnames

        for header in headers:
            tmp=[]
            for row in reader:
                try: 
                    row[header]=float(row[header])
                except ValueError:
                    continue
                else:
                    tmp.append(row[header]) 
            n=len(tmp)
            if n==0: continue
            srt_tmp=sorted(tmp)
            sq_tmp=[x**2 for x in tmp]
            mean=sum(tmp)/n
            mean_sq=sum(sq_tmp)/n
            median=(srt_tmp[n//2] if n%2!=0 else (srt_tmp[n//2-1]+srt_tmp[n//2])/2)
            mode=""
            std_dev=(mean_sq-(mean**2))**(1/2)
            stats[f"{header} average"]= mean
            stats[f"{header} median"]= median
            stats[f"{header} mode"]= mode
            stats[f"{header} std_dev"]= std_dev
            file.seek(0)
            reader = csv.DictReader(file)

    with open(s_path, "w") as file:
        json.dump(stats, file, indent=2)



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
    if args.stats=="Yes":
        s_path=os.path.join(args.output,"stats.json")
        statistics_json(c_path,s_path)

if __name__=="__main__":
    main()