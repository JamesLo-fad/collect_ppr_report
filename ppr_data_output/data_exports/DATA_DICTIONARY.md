# CEPU PPR Funding Scheme - Data Dictionary

## Overview
This folder contains the complete database of **248 completed projects** from the CEPU Public Policy Research (PPR) Funding Scheme, along with all downloaded research reports.

**Data Collection Date:** January 24, 2026
**Source:** https://www.cepu.gov.hk/en/PRFS/ppr-reports.html
**Data Format:** XML (converted to CSV, Excel, JSON)

---

## Files in This Folder

### 1. `ppr_completed_projects_FINAL.csv` (93 KB)
**Primary database file** - Use this for data analysis in Excel, Python, R, etc.

- **Format:** CSV (UTF-8 with BOM)
- **Records:** 248 completed projects
- **Columns:** 12 fields (see Data Fields section below)
- **Best for:** Data analysis, filtering, sorting, pivot tables

### 2. `ppr_completed_projects_FINAL.xlsx` (38 KB)
**Excel workbook** - Same data as CSV but in Excel format

- **Format:** Microsoft Excel (.xlsx)
- **Records:** 248 completed projects
- **Best for:** Quick viewing and analysis in Microsoft Excel

### 3. `ppr_completed_projects_FINAL.json` (164 KB)
**Structured JSON** - Same data in JSON format

- **Format:** JSON (UTF-8)
- **Records:** 248 completed projects
- **Best for:** Web applications, APIs, programmatic access

### 4. `ppr_completed_projects_RAW.json` (164 KB)
**Raw JSON** - Original parsed data from XML

- **Format:** JSON (UTF-8)
- **Records:** 248 completed projects
- **Best for:** Debugging, data validation

### 5. `README.txt`
Summary report with statistics and sample data

---

## Data Fields

| Field Name | Description | Example | Notes |
|------------|-------------|---------|-------|
| **Project Number** | Unique project identifier | 2013.A2.001.13A | Primary key |
| **Project Title** | Full title of the research project | Land and Housing Policies in Post-Handover Hong Kong | |
| **Principal Investigator** | Name of the lead researcher | Prof LI Si Ming | May include title (Prof, Dr) |
| **Institution** | University or research institution | Hong Kong Baptist University | |
| **Status** | Project completion status | Completed | All records are "Completed" |
| **Research_Report_Title** | Title of the research report | Research Report | May include language note |
| **Research_Report_URL** | Direct download link to PDF | https://www.cepu.gov.hk/doc/en/... | Full URL to PDF file |
| **Year** | Funding round/period | 2013-14 (First Round) | Format: YYYY-YY (Round) |
| **Duration (months)** | Project duration in months | 15 | Numeric value |
| **Funding (HK$)** | Funding amount in HK dollars | 416760 | Numeric value (no commas) |
| **Major Themes** | Research theme categories | Land and Housing | May have multiple themes |
| **Empirical_Data_URL** | Link to empirical data (if available) | https://www.cepu.gov.hk/doc/en/... | May be empty if no data |

---

## Data Statistics

- **Total Projects:** 248
- **Date Range:** 2013-14 to 2023
- **Projects with Research Reports:** 248 (100%)
- **Projects with Empirical Data:** ~50 (varies)
- **Total PDF Files Downloaded:** 248

### Breakdown by Major Themes
The projects cover various policy research areas including:
- Land and Housing
- Livelihood Issues
- Political Development and Governance
- Education
- Healthcare
- Economic Development
- Social Welfare
- And more...

### Breakdown by Institution
Projects are conducted by researchers from major Hong Kong universities:
- The Chinese University of Hong Kong
- The University of Hong Kong
- Hong Kong Baptist University
- City University of Hong Kong
- The Hong Kong Polytechnic University
- Lingnan University
- The Education University of Hong Kong
- The Hang Seng University of Hong Kong
- Hong Kong Metropolitan University

---

## Research Reports

All 248 research reports (PDF files) are stored in the `../research_reports/` folder.

**Naming Convention:** `{Project_Number}_{Report_Title}.pdf`

Example:
- `2013.A2.001.13A_Research Report.pdf`
- `2021.A4.073.21A_Research Report (Chinese Version only).pdf`

**Total Size:** ~1.2 GB (varies)

---

## Usage Examples

### Excel/Google Sheets
1. Open `ppr_completed_projects_FINAL.xlsx` or import the CSV
2. Use filters to find projects by theme, institution, or year
3. Create pivot tables for analysis
4. Sort by funding amount, duration, etc.

### Python (pandas)
```python
import pandas as pd

# Load the data
df = pd.read_csv('ppr_completed_projects_FINAL.csv')

# View basic info
print(df.info())
print(df.head())

# Filter by institution
hku_projects = df[df['Institution'].str.contains('University of Hong Kong')]

# Calculate total funding
total_funding = df['Funding (HK$)'].sum()

# Group by year
by_year = df.groupby('Year').size()
```

### R
```r
# Load the data
data <- read.csv('ppr_completed_projects_FINAL.csv', encoding='UTF-8')

# View structure
str(data)

# Summary statistics
summary(data$`Funding (HK$)`)

# Filter by theme
housing_projects <- data[grepl('Housing', data$Major.Themes), ]
```

---

## Data Quality Notes

1. **Completeness:** All 248 completed projects with research reports are included
2. **Accuracy:** Data is directly from the official CEPU XML data file
3. **Currency:** Data is current as of January 24, 2026
4. **Language:** Some reports are Chinese Version only (noted in title)
5. **URLs:** All research report URLs have been validated and PDFs downloaded

---

## Citation

If you use this data in your research, please cite:

```
Central Policy Unit, Hong Kong SAR Government. (2026).
Public Policy Research Funding Scheme - Completed Projects Database.
Retrieved from https://www.cepu.gov.hk/en/PRFS/ppr-reports.html
Data compiled: January 24, 2026
```

---

## Contact & Updates

For the latest data, visit: https://www.cepu.gov.hk/en/PRFS/ppr-reports.html

To update this database, run the scraper script: `python main.py`

---

## License & Disclaimer

The copyrights of the research reports belong to the Principal Investigator and Co-Investigator(s). The views expressed in the reports are those of the Research Team and do not represent the views of the Government and/or the Assessment Panel.

This database is compiled for research and educational purposes. Users should acknowledge the research team and the Government when using the data.
