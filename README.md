# gfix

A command line tool to fix Excel-converted gene names in spreadsheets. Excel automatically converts some gene names (like MARCH1, SEPT2) to dates - this tool converts them back.

## Features

- Fixes common gene-to-date conversions (MARCH1 → Mar-1 → MARCHF1)
- Processes all sheets in an Excel file
- Preserves original data format
- Detailed change logging

The list of genes that are modified can be found here: https://github.com/sbooeshaghi/gfix/blob/a854d9b8fc0643154d290a1dc2d534c5a9f823a5/gfix/main.py#L94

## Installation

```bash
# devel
pip install git+https://github.com/sbooeshaghi/gfix.git

# pypi
pip install gfix
```

## Usage

```bash
gfix -o output.xlsx input.xlsx
```

## Example

If your Excel file has converted gene names to dates (e.g., MARCH1 appears as "Mar-1" or "3/1/2024"), running gfix will restore the correct gene symbols:

```bash
$ gfix -o fixed_data.xlsx raw_data.xlsx
Processing raw_data.xlsx...
Processing sheet: Sheet1
Changes in sheet 'Sheet1':
Location: Row 5, Column 0
Old value: 3/1/2024
New value: MARCHF1
...
```
