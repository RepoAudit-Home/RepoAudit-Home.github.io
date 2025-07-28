import json
import pandas as pd
from datetime import datetime
import os

def update_bug_reports(excel_file, json_file, output_file=None):
    """
    Update bug reports in the JSON file with data from the Excel file.
    
    Args:
        excel_file: Path to the Excel file with new bug data
        json_file: Path to the existing JSON file with bug reports
        output_file: Path to save the updated JSON (defaults to overwriting json_file)
    """
    print(f"Reading Excel file: {excel_file}")
    
    # Get today's date for empty date fields
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # Read the Excel file
    try:
        df = pd.read_excel(excel_file)
        print(f"Successfully loaded Excel file with {len(df)} entries")
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return False
    
    # Read the existing JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            bug_reports = json.load(f)
        print(f"Successfully loaded JSON file with {len(bug_reports)} entries")
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return False
    
    # Create a dictionary for quick lookup of existing reports by link
    existing_links = {}
    for i, report in enumerate(bug_reports):
        link = report.get("patch/issue link", "")
        if link:
            existing_links[link] = i
    
    # Keep track of updates and additions
    updates = 0
    additions = 0
    
    # Process each row in the Excel file
    for _, row in df.iterrows():
        # Extract data from the Excel row
        link = row.get('Link', '')
        if not link or pd.isna(link):
            continue  # Skip rows with empty links
        
        # Format date if available, otherwise use today's date
        excel_date = row.get('date')
        if pd.isna(excel_date) or not excel_date:
            # For new entries, use today's date
            # For existing entries, we'll check and keep the original date below
            date_str = today_date
        else:
            # If date is already a datetime object
            if isinstance(excel_date, datetime):
                date_str = excel_date.strftime("%Y-%m-%d")
            else:
                # Try to parse string date in different formats
                try:
                    # Try parsing M/D/YYYY format
                    date_obj = datetime.strptime(str(excel_date), "%m/%d/%Y")
                    date_str = date_obj.strftime("%Y-%m-%d")
                except:
                    date_str = str(excel_date)
        try:
            bug_num = int(row.get('Bug Num')) if pd.notna(row.get('Bug Num')) else 1
        except (ValueError, TypeError):
            bug_num = 1

        # Create a new entry with Excel data
        new_entry = {
            "repo_name": row.get('Project_Name', ''),
            "patch/issue link": link,
            "status": row.get('Status', ''),
            "date": date_str,  # This will be overridden for existing entries if they already have a date
            "language": row.get('language', ''),
            "Bug Num": str(bug_num),
            "Agent": "bugscan",  # Default agent
            "bug_type": row.get('Bug Type', ''),
            "sort_weight": 0     # Default sort weight
        }
        
        # Check if this link already exists in the bug reports
        if link in existing_links:
            # Update existing entry
            index = existing_links[link]
            
            # Prioritize existing date if it exists
            existing_date = bug_reports[index].get("date")
            if existing_date and existing_date.strip():
                # Keep existing date
                new_entry["date"] = existing_date
            
            # Update other fields
            for key, value in new_entry.items():
                if value:  # Only update non-empty values
                    bug_reports[index][key] = value
                    
            updates += 1
        else:
            # Add new entry
            bug_reports.append(new_entry)
            existing_links[link] = len(bug_reports) - 1
            additions += 1
    
    # Save the updated bug reports
    if output_file is None:
        output_file = json_file
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bug_reports, f, indent=4)
        print(f"Successfully updated bug reports file: {output_file}")
        print(f"  - Updated {updates} existing entries")
        print(f"  - Added {additions} new entries")
        print(f"  - Total entries: {len(bug_reports)}")
        return True
    except Exception as e:
        print(f"Error writing updated JSON file: {str(e)}")
        return False

if __name__ == "__main__":
    # Define file paths
    excel_file = "Update0720.xlsx"
    json_file = "BugReport.json"
    
    # Create backup of original file
    backup_file = f"bug_reports_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(json_file, 'r', encoding='utf-8') as src:
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"Created backup file: {backup_file}")
    except Exception as e:
        print(f"Failed to create backup: {str(e)}")
    
    # Update the bug reports
    update_bug_reports(excel_file, json_file)