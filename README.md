# CEPU PPR Funding Scheme - Data Collection Tool

Automated tool to collect and download all completed research projects from the Hong Kong CEPU Public Policy Research (PPR) Funding Scheme.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python main.py
```

## What This Tool Does

1. **Fetches** project data from CEPU's XML data file
2. **Extracts** all 248 completed projects with research reports
3. **Downloads** all research report PDFs (automatically)
4. **Exports** data in multiple formats (CSV, Excel, JSON)
5. **Organizes** everything into a clean folder structure

## Output Structure

```
ppr_data_output/
├── data_exports/                    # All data files
│   ├── DATA_DICTIONARY.md          # Complete data documentation
│   ├── ppr_completed_projects_FINAL.csv    # Main database (use this!)
│   ├── ppr_completed_projects_FINAL.xlsx   # Excel format
│   ├── ppr_completed_projects_FINAL.json   # JSON format
│   └── ppr_completed_projects_RAW.json     # Raw data
│
└── research_reports/                # All 248 PDF files
    ├── 2013.A2.001.13A_Research Report.pdf
    ├── 2013.A3.002.13A_Research Report.pdf
    └── ... (248 files total)
```

## Data Summary

- **Total Projects:** 248 completed projects
- **Research Reports:** 248 PDFs downloaded (~1.2 GB)
- **Date Range:** 2013-2023
- **Data Fields:** 12 columns including project details, funding, URLs
- **Format:** CSV, Excel, JSON

## Key Features

✅ **Complete Data Collection** - All 248 completed projects
✅ **Automatic PDF Downloads** - All research reports downloaded
✅ **Resume Capability** - Skips already downloaded files
✅ **Error Handling** - Automatic retries for failed downloads
✅ **Multiple Formats** - CSV, Excel, JSON exports
✅ **Clean Structure** - Organized folders and clear documentation

## Usage

### Basic Usage
```bash
python main.py
```

### Configuration
Edit `main.py` to customize:
```python
DOWNLOAD_REPORTS = True   # Set to False to skip PDF downloads
```

### Using the Data

**Excel/Google Sheets:**
- Open `ppr_data_output/data_exports/ppr_completed_projects_FINAL.xlsx`
- Filter, sort, analyze as needed

**Python:**
```python
import pandas as pd
df = pd.read_csv('ppr_data_output/data_exports/ppr_completed_projects_FINAL.csv')
print(df.head())
```

**R:**
```r
data <- read.csv('ppr_data_output/data_exports/ppr_completed_projects_FINAL.csv')
summary(data)
```

## Data Fields

| Field | Description |
|-------|-------------|
| Project Number | Unique identifier (e.g., 2013.A2.001.13A) |
| Project Title | Full research project title |
| Principal Investigator | Lead researcher name |
| Institution | University/research institution |
| Year | Funding round (e.g., 2013-14 First Round) |
| Duration (months) | Project duration |
| Funding (HK$) | Funding amount |
| Major Themes | Research categories |
| Research_Report_URL | Direct PDF download link |
| Empirical_Data_URL | Data archive link (if available) |

See `ppr_data_output/data_exports/DATA_DICTIONARY.md` for complete documentation.

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- pandas
- openpyxl
- lxml

## Installation

```bash
# Clone or download this repository
cd collect_ppr_report

# Install dependencies
pip install -r requirements.txt

# Run the scraper
python main.py
```

## Technical Details

- **Data Source:** https://www.cepu.gov.hk/en/filestore/ppr-reports.xml
- **Method:** XML parsing (not HTML scraping)
- **Download Speed:** ~1 second per PDF (respectful rate limiting)
- **Total Runtime:** ~5-10 minutes for full collection

## Troubleshooting

**No projects found:**
- Check internet connection
- Verify the XML URL is accessible

**Download failures:**
- Script automatically retries 3 times
- Re-run the script to resume downloads

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

## License & Citation

The copyrights of research reports belong to the Principal Investigators. Views expressed are those of the research teams, not the Government.

**Citation:**
```
Central Policy Unit, Hong Kong SAR Government. (2026).
Public Policy Research Funding Scheme - Completed Projects.
Retrieved from https://www.cepu.gov.hk/en/PRFS/ppr-reports.html
```

## Updates

To get the latest data, simply run:
```bash
python main.py
```

The script will:
- Fetch the latest XML data
- Download any new research reports
- Skip existing files (resume capability)

---

**Last Updated:** January 2026
**Data Current As Of:** January 24, 2026
