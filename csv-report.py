import csv

def csv_report(output, result):
    
    rows = ["vs_name"]
    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(rows)
        for non_healthy in result.get("non-healthy"):
            writer.writerow(non_healthy)

# csv_report.py

# function: takes the output path and the classification results
# step 1: open the output file for writing
# step 2: write the header row with the two columns from the spec
# step 3: loop over each VS in the classification results
# step 4: skip any VS that is healthy
# step 5: write one row with the name and the health of each non-healthy VS
# step 6: return nothing; errors are handled by the caller

# main.py
# step 7: read the output file name from config.json
# step 8: call the function; if writing fails, print one message and exit with code 1