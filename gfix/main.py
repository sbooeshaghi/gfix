#!/usr/bin/env python3
import pandas as pd
import numpy as np
import re
from datetime import datetime
import argparse


def format_datetime_to_gene(dt):
    """
    Convert a datetime object to the standard gene name format (e.g., 'MAR-01').
    Special case: any June date returns 'JUN'
    """
    month_map = {
        1: "JAN",
        2: "FEB",
        3: "MAR",
        4: "APR",
        5: "MAY",
        6: "JUN",
        7: "JUL",
        8: "AUG",
        9: "SEP",
        10: "OCT",
        11: "NOV",
        12: "DEC",
    }

    # Special case: if it's June, return JUN as the gene name
    if dt.month == 6:
        return "JUN"

    month = month_map[dt.month]
    day = str(dt.day).zfill(2)
    return f"{month}-{day}"


def try_convert_to_datetime(x):
    """
    Try to convert a value to datetime, handling various formats and errors.
    Returns None if the value is not a valid date.
    """
    # If it's already a datetime, return it
    if isinstance(x, datetime):
        return x

    # If it's a float or looks like a float, it's not a date
    try:
        if isinstance(x, (float, int)) or (isinstance(x, str) and float(x)):
            return None
    except ValueError:
        pass

    # If it's a string, try to parse it as a date
    if isinstance(x, str):
        # Remove any whitespace
        x = x.strip()

        # Skip if it starts with ST (to prevent ST genes from being converted)
        if x.upper().startswith("ST"):
            return None

        # Skip if it looks like a number
        if x.replace(".", "").replace("-", "").isdigit():
            return None

        # Try parsing with various formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
            try:
                dt = pd.to_datetime(x, format=fmt)
                # If this date is in June, return a special marker
                if dt.month == 6:
                    # Create a dummy datetime that will be recognized as a JUN gene
                    return datetime(2000, 6, 1)  # Any June date will do
                return dt
            except ValueError:
                continue

    try:
        # Last resort: try pandas to_datetime, but only for string input
        if isinstance(x, str):
            result = pd.to_datetime(x, errors="coerce")
            if pd.isna(result):
                return None
            # Check for June dates here as well
            if result.month == 6:
                return datetime(2000, 6, 1)
            return result
        return None
    except (ValueError, TypeError):
        return None


def load_reference_data():
    """
    Dictionary mapping date-format gene names to their correct HGNC symbols.
    """
    return {
        "MAR-01": "MARCHF1",  # Default to MARCHF1, but could also be MTARC1
        "MAR-12": "MARCHF1",  # for some reason gene names have an additional number added to them
        "MAR-13": "MARCHF1",
        "MAR-14": "MARCHF1",
        "MAR-15": "MARCHF1",
        "MAR-16": "MARCHF1",
        "MAR-02": "MARCHF2",  # Default to MARCHF2, but could also be MTARC2
        "MAR-03": "MARCHF3",
        "MAR-31": "MARCHF3",  # for some reason gene names have an additional number added to them
        "MAR-04": "MARCHF4",
        "MAR-05": "MARCHF5",
        "MAR-06": "MARCHF6",
        "MAR-07": "MARCHF7",
        "MAR-08": "MARCHF8",
        "MAR-09": "MARCHF9",
        "MAR-10": "MARCHF10",
        "MAR-11": "MARCHF11",
        "SEP-01": "SEPTIN1",
        "SEP-02": "SEPTIN2",
        "SEP-03": "SEPTIN3",
        "SEP-04": "SEPTIN4",
        "SEP-05": "SEPTIN5",
        "SEP-06": "SEPTIN6",
        "SEP-07": "SEPTIN7",
        "SEP-08": "SEPTIN8",
        "SEP-09": "SEPTIN9",
        "SEP-10": "SEPTIN10",
        "SEP-11": "SEPTIN11",
        "SEP-12": "SEPTIN12",
        "SEP-13": "SEPTIN7P2",
        "SEP-14": "SEPTIN14",
        "SEP-15": "SELENOF",
        "DEC-01": "DELEC1",
    }


def process_cell_value(value, gene_map):
    """
    Process a single cell value, checking only for dates.
    Returns the processed value and whether it was changed.
    """
    if pd.isna(value):
        return value, False

    # Check if it's a datetime
    dt = try_convert_to_datetime(value)
    if dt is not None:
        date_format = format_datetime_to_gene(dt)
        # Check if the formatted date is in the gene map
        if date_format in gene_map:
            return gene_map[date_format], True
        return date_format, True

    return value, False


def scan_and_fix_excel(input_path, output_path):
    """
    Scan and fix every cell in every sheet of an Excel file, but only modify dates.
    """
    print(f"Processing {input_path}...")

    # Load the gene mapping
    gene_map = load_reference_data()

    # Read all sheets without specifying an index
    xlsx = pd.read_excel(input_path, sheet_name=None)

    all_changes = []
    processed_sheets = {}

    # Process each sheet
    for sheet_name, df in xlsx.items():
        print(f"\nProcessing sheet: {sheet_name}")
        changes = []

        # Process column names
        new_columns = df.columns.tolist()
        for i, col in enumerate(new_columns):
            new_value, changed = process_cell_value(col, gene_map)
            if changed:
                changes.append(
                    {
                        "sheet": sheet_name,
                        "location": f"Column header {i}",
                        "old_value": str(col),
                        "new_value": str(new_value),
                    }
                )
                new_columns[i] = new_value

        # Create a new DataFrame with the processed column names
        new_df = pd.DataFrame(df.values, columns=new_columns)

        # Process each cell in the dataframe
        for i in range(len(df)):
            for j in range(len(df.columns)):
                old_value = df.iat[i, j]
                new_value, changed = process_cell_value(old_value, gene_map)

                if changed:
                    changes.append(
                        {
                            "sheet": sheet_name,
                            "location": f"Row {i}, Column {j} ({new_columns[j]})",
                            "old_value": str(old_value),
                            "new_value": str(new_value),
                        }
                    )
                    new_df.iat[i, j] = new_value

        # Store the processed dataframe
        processed_sheets[sheet_name] = new_df
        all_changes.extend(changes)

        # Print changes for this sheet
        if changes:
            print(f"Changes in sheet '{sheet_name}':")
            print("-" * 80)
            for change in changes:
                print(f"Location: {change['location']}")
                print(f"Old value: {change['old_value']}")
                print(f"New value: {change['new_value']}")
                print("-" * 80)

    # Save all processed sheets to a new Excel file
    with pd.ExcelWriter(output_path) as writer:
        for sheet_name, df in processed_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Print summary
    print(f"\nSummary:")
    print(f"Total sheets processed: {len(processed_sheets)}")
    print(f"Total changes made: {len(all_changes)}")
    print(f"Saved corrected data to {output_path}")

    return len(all_changes)


def main():
    parser = argparse.ArgumentParser(
        description="Fix Excel-converted gene names in data files."
    )
    parser.add_argument("-o", "--output_file", help="Output Excel file path")
    parser.add_argument("input_file", help="Input Excel file path")

    args = parser.parse_args()

    try:
        total_changes = scan_and_fix_excel(args.input_file, args.output_file)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        raise


if __name__ == "__main__":
    main()
