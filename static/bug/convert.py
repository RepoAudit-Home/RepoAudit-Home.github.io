import pandas as pd
import json

# # Read the HTML file
# df = pd.read_html("Bug Report.html")[0]

# # Convert to JSON format
# json_output = df.to_json(orient="records", force_ascii=False)

# # Save as JSON file
# with open("RawBugReport.json", "w", encoding="utf-8") as f:
#     f.write(json_output)

# print("Conversion complete! RawBugReport.json has been saved.")

# Read the JSON file
with open("RawBugReport.json", "r", encoding="utf-8") as f:
    data = json.load(f)

bug_reports = []

for item in data:
    if item["G"] is None or item["G"] == "exit" or item["G"] == "Declined" or item["H"] is None or item["A"] == "Project_Name":
        continue
    print(item)

    bug_report_item = {
        "repo_name": item["A"],
        "bug_type": item["B"],
        "patch/issue link": item["E"],
        "date": item["J"],
        "status": item["G"],
        "language": item["I"],
        "Bug Num": item["H"],
    }
    bug_reports.append(bug_report_item)

# sort by "date" descending
bug_reports.sort(key=lambda x: x["date"], reverse=True)


# Save as JSON file
with open("BugReport.json", "w", encoding="utf-8") as f:
    json.dump(bug_reports, f, ensure_ascii=False, indent=4)