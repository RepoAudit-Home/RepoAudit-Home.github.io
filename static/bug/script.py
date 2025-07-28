import json

def add_sort_weight_to_bug_reports(file_path):
    with open(file_path, "r") as file:
        bug_reports = json.load(file)
    
    for item in bug_reports:
        if item["repo_name"] == "challenge-004-nginx-source":
            item["sort_weight"] = 100
        else:
            item["sort_weight"] = 0
        
    return bug_reports

if __name__ == "__main__":
    bug_reports = add_sort_weight_to_bug_reports("BugReport.json")
    with open("BugReport_new.json", "w") as file:
        json.dump(bug_reports, file, indent=4)