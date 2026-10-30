import csv
def csv_report(output, result):
    with open(output, "w", newline="") as f:
        rows = ["name","health"]
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(rows)
        for non_healthy in result:
            writer.writerow(non_healthy)
    return None