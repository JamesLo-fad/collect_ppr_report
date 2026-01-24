"""
Web Scraping Script for CEPU Public Policy Research (PPR) Funding Scheme
Target URL: https://www.cepu.gov.hk/en/PRFS/ppr-reports.html
Purpose: Extract completed projects data with research report links

Author: [Your Name]
Date: January 2026
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from urllib.parse import urljoin
import json
from datetime import datetime
import os
import xml.etree.ElementTree as ET

# Configuration
BASE_URL = "https://www.cepu.gov.hk"
TARGET_URL = "https://www.cepu.gov.hk/en/PRFS/ppr-reports.html"
XML_DATA_URL = "https://www.cepu.gov.hk/en/filestore/ppr-reports.xml"
OUTPUT_DIR = "ppr_data_output"
DATA_EXPORTS_DIR = os.path.join(OUTPUT_DIR, "data_exports")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "research_reports")
DOWNLOAD_REPORTS = True  # Set to False to skip downloading PDFs
MAX_CONCURRENT_DOWNLOADS = 3  # Number of concurrent downloads

# Headers to mimic browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}


def create_output_directory():
    """Create output directories if they don't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(DATA_EXPORTS_DIR):
        os.makedirs(DATA_EXPORTS_DIR)
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    return OUTPUT_DIR


def fetch_page(url, retries=3, delay=2):
    """
    Fetch webpage content with retry mechanism
    
    Args:
        url: Target URL
        retries: Number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        BeautifulSoup object or None if failed
    """
    for attempt in range(retries):
        try:
            print(f"Fetching: {url} (Attempt {attempt + 1}/{retries})")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    return None


def download_file(url, filename, retries=3, delay=2):
    """
    Download a file from URL with retry mechanism

    Args:
        url: File URL to download
        filename: Local filename to save to
        retries: Number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        True if successful, False otherwise
    """
    filepath = os.path.join(REPORTS_DIR, filename)

    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"  File already exists: {filename}")
        return True

    for attempt in range(retries):
        try:
            print(f"  Downloading: {filename} (Attempt {attempt + 1}/{retries})")
            response = requests.get(url, headers=HEADERS, timeout=60, stream=True)
            response.raise_for_status()

            # Write file in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = os.path.getsize(filepath)
            print(f"  Downloaded successfully: {filename} ({file_size:,} bytes)")
            return True

        except requests.RequestException as e:
            print(f"  Error downloading {filename}: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)  # Remove partial file
            if attempt < retries - 1:
                print(f"  Retrying in {delay} seconds...")
                time.sleep(delay)

    return False


def sanitize_filename(filename, max_length=200):
    """
    Sanitize filename to be filesystem-safe

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext

    return filename


def download_research_reports(projects):
    """
    Download all research reports from the projects list

    Args:
        projects: List of project dictionaries with research report URLs

    Returns:
        Dictionary with download statistics
    """
    if not DOWNLOAD_REPORTS:
        print("\nSkipping research report downloads (DOWNLOAD_REPORTS=False)")
        return {'total': 0, 'successful': 0, 'failed': 0, 'skipped': 0}

    print("\n" + "=" * 60)
    print("Downloading Research Reports")
    print("=" * 60)

    # Collect all unique report URLs
    report_downloads = []
    seen_urls = set()

    for project in projects:
        report_url = project.get('Research_Report_URL', '')
        report_title = project.get('Research_Report_Title', '')
        project_num = project.get('Project Number', '') or project.get('Project No.', '')

        if report_url and report_url not in seen_urls:
            seen_urls.add(report_url)

            # Generate filename
            if report_url.endswith('.pdf'):
                # Use project number and title for filename
                if project_num:
                    base_name = f"{project_num}_{report_title}" if report_title else project_num
                else:
                    base_name = report_title or 'report'

                filename = sanitize_filename(base_name) + '.pdf'
            else:
                # Extract filename from URL
                filename = os.path.basename(report_url.split('?')[0])
                if not filename:
                    filename = f"report_{len(report_downloads)}.pdf"

            report_downloads.append({
                'url': report_url,
                'filename': filename,
                'project_num': project_num,
                'title': report_title
            })

    total = len(report_downloads)
    successful = 0
    failed = 0

    print(f"\nFound {total} unique research reports to download")
    print(f"Download directory: {REPORTS_DIR}\n")

    # Download each report
    for idx, report in enumerate(report_downloads, 1):
        print(f"\n[{idx}/{total}] Project: {report['project_num']}")
        print(f"  Title: {report['title']}")

        if download_file(report['url'], report['filename']):
            successful += 1
        else:
            failed += 1
            print(f"  Failed to download: {report['filename']}")

        # Small delay between downloads to be respectful
        if idx < total:
            time.sleep(1)

    stats = {
        'total': total,
        'successful': successful,
        'failed': failed,
        'skipped': 0
    }

    print("\n" + "=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Total reports: {stats['total']}")
    print(f"Successfully downloaded: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print("=" * 60)

    return stats


def fetch_xml_data(url=XML_DATA_URL, retries=3, delay=2):
    """
    Fetch and parse XML data file

    Args:
        url: XML data URL
        retries: Number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        ElementTree root or None if failed
    """
    for attempt in range(retries):
        try:
            print(f"Fetching XML data: {url} (Attempt {attempt + 1}/{retries})")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'

            # Parse XML
            root = ET.fromstring(response.content)
            return root

        except (requests.RequestException, ET.ParseError) as e:
            print(f"Error fetching/parsing XML: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    return None


def parse_xml_projects(root):
    """
    Parse project data from XML

    Args:
        root: ElementTree root element

    Returns:
        List of project dictionaries
    """
    projects = []

    for record in root.findall('record'):
        project = {}

        # Extract basic fields
        project['Year'] = record.findtext('report-period', '').strip()
        project['Project Number'] = record.findtext('project-no', '').strip()
        project['Principal Investigator'] = record.findtext('principal-invest', '').strip()
        project['Institution'] = record.findtext('institution', '').strip()
        project['Project Title'] = record.findtext('title', '').strip()
        project['Duration (months)'] = record.findtext('duration', '').strip()
        project['Funding (HK$)'] = record.findtext('funding', '').strip()
        project['Major Themes'] = record.findtext('areas', '').strip()

        # Extract status and research report link
        status_elem = record.find('status')
        if status_elem is not None:
            # Get status text
            status_div = status_elem.find('div')
            if status_div is not None:
                status_text = status_div.text.strip() if status_div.text else ''
                project['Status'] = status_text

                # Check if completed
                if 'Completed' in status_text:
                    # Get research report link
                    report_link = status_elem.find('a')
                    if report_link is not None:
                        href = report_link.get('href', '')
                        link_text = report_link.text.strip() if report_link.text else 'Research Report'

                        # Only add if href is not nil and not empty
                        if href and report_link.get('{http://www.w3.org/2001/XMLSchema-instance}nil') != 'true':
                            # Fix relative URLs that start with /
                            if href.startswith('/'):
                                href = BASE_URL + href
                            project['Research_Report_URL'] = href
                            project['Research_Report_Title'] = link_text
                        else:
                            project['Research_Report_URL'] = ''
                            project['Research_Report_Title'] = ''

                    # Extract empirical data link
                    zip_elem = record.find('zip')
                    if zip_elem is not None:
                        zip_link = zip_elem.find('a')
                        if zip_link is not None:
                            zip_href = zip_link.get('href', '')
                            if zip_href and zip_link.get('{http://www.w3.org/2001/XMLSchema-instance}nil') != 'true':
                                # Fix relative URLs that start with /
                                if zip_href.startswith('/'):
                                    zip_href = BASE_URL + zip_href
                                project['Empirical_Data_URL'] = zip_href
                            else:
                                project['Empirical_Data_URL'] = ''

                    projects.append(project)

    return projects


def extract_project_data(soup):
    """
    Extract project data from the PPR reports page
    
    Args:
        soup: BeautifulSoup object of the page
    
    Returns:
        List of dictionaries containing project data
    """
    projects = []
    
    # Find the main table containing project data
    # The table structure may vary, so we try multiple selectors
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        
        # Skip header row
        header_row = rows[0] if rows else None
        headers = []
        
        if header_row:
            header_cells = header_row.find_all(['th', 'td'])
            headers = [cell.get_text(strip=True) for cell in header_cells]
            print(f"Found headers: {headers}")
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            
            if len(cells) >= 3:  # Ensure we have enough columns
                row_data = {}
                
                # Extract basic cell data
                for i, cell in enumerate(cells):
                    header_name = headers[i] if i < len(headers) else f"Column_{i}"
                    
                    # Get text content
                    text_content = cell.get_text(strip=True)
                    row_data[header_name] = text_content
                    
                    # Extract links (for research reports)
                    links = cell.find_all('a')
                    if links:
                        link_data = []
                        for link in links:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)
                            if href:
                                full_url = urljoin(BASE_URL, href)
                                link_data.append({
                                    'text': link_text,
                                    'url': full_url
                                })
                        if link_data:
                            row_data[f"{header_name}_links"] = link_data
                
                # Check if status is "Completed"
                status_value = row_data.get('Status^', '') or row_data.get('Status', '')
                if 'Completed' in status_value or 'completed' in status_value.lower():
                    projects.append(row_data)
    
    return projects


def parse_table_alternative(soup):
    """
    Alternative parsing method for different table structures
    Uses more flexible selectors
    """
    projects = []

    # Parse all tables systematically
    all_tables = soup.find_all('table')
    
    for table_idx, table in enumerate(all_tables):
        print(f"\nProcessing Table {table_idx + 1}...")
        
        # Get all rows
        rows = table.find_all('tr')
        if not rows:
            continue
            
        # Determine header structure
        header_cells = rows[0].find_all(['th', 'td'])
        headers = [cell.get_text(strip=True).replace('\n', ' ') for cell in header_cells]
        
        # Clean headers
        headers = [re.sub(r'\s+', ' ', h).strip() for h in headers]
        print(f"Headers found: {headers}")
        
        # Find status column index
        status_col_idx = None
        for idx, h in enumerate(headers):
            if 'status' in h.lower():
                status_col_idx = idx
                break
        
        # Process each data row
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = row.find_all(['td', 'th'])
            
            # Check if this is a completed project
            is_completed = False
            if status_col_idx is not None and status_col_idx < len(cells):
                status_text = cells[status_col_idx].get_text(strip=True)
                is_completed = 'completed' in status_text.lower()
            else:
                # Check all cells for "Completed" status
                for cell in cells:
                    if 'completed' in cell.get_text(strip=True).lower():
                        is_completed = True
                        break
            
            if not is_completed:
                continue
            
            # Extract project data
            project = {
                'row_index': row_idx,
                'table_index': table_idx + 1
            }
            
            for col_idx, cell in enumerate(cells):
                col_name = headers[col_idx] if col_idx < len(headers) else f'Column_{col_idx}'
                
                # Extract text
                cell_text = cell.get_text(strip=True)
                cell_text = re.sub(r'\s+', ' ', cell_text)  # Clean whitespace
                project[col_name] = cell_text
                
                # Extract all links in this cell
                links = cell.find_all('a')
                if links:
                    link_list = []
                    for link in links:
                        href = link.get('href', '')
                        link_text = link.get_text(strip=True)
                        
                        if href:
                            # Handle relative URLs
                            if href.startswith('/'):
                                full_url = BASE_URL + href
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                full_url = BASE_URL + '/en/PRFS/' + href
                            
                            link_list.append({
                                'link_text': link_text,
                                'url': full_url
                            })
                    
                    if link_list:
                        project[f'{col_name}_Links'] = link_list
            
            projects.append(project)
    
    return projects


def expand_research_reports(projects):
    """
    Expand projects with research reports into separate rows
    Each research report gets its own row
    
    Args:
        projects: List of project dictionaries
    
    Returns:
        Expanded list with separate rows for each research report
    """
    expanded_data = []
    
    for project in projects:
        # Find columns that contain links (research reports)
        report_links = []
        
        for key, value in project.items():
            if '_Links' in key and isinstance(value, list):
                for link_info in value:
                    if 'report' in link_info.get('link_text', '').lower() or \
                       'report' in link_info.get('url', '').lower() or \
                       '.pdf' in link_info.get('url', '').lower():
                        report_links.append(link_info)
        
        if report_links:
            # Create a row for each research report
            for report in report_links:
                new_row = project.copy()
                new_row['Research_Report_Title'] = report.get('link_text', '')
                new_row['Research_Report_URL'] = report.get('url', '')
                new_row['Is_Research_Report_Row'] = True
                expanded_data.append(new_row)
        else:
            # Keep original row without research report
            project['Research_Report_Title'] = ''
            project['Research_Report_URL'] = ''
            project['Is_Research_Report_Row'] = False
            expanded_data.append(project)
    
    return expanded_data


def clean_dataframe(df):
    """
    Clean and format the dataframe
    """
    # Remove link columns (keep only the extracted report links)
    cols_to_drop = [col for col in df.columns if '_Links' in col]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # Reorder columns - put important ones first
    priority_cols = [
        'Project Number', 'Project No.', 'Project Title', 'Title',
        'Principal Investigator', 'PI', 'Institution',
        'Status^', 'Status', 'Funding Amount', 'Amount',
        'Research_Report_Title', 'Research_Report_URL'
    ]
    
    existing_priority = [col for col in priority_cols if col in df.columns]
    other_cols = [col for col in df.columns if col not in priority_cols]
    new_order = existing_priority + other_cols
    
    df = df.reindex(columns=new_order)
    
    return df


def save_results(projects, expanded_projects):
    """
    Save results to multiple formats in the data_exports folder
    """
    create_output_directory()

    # Save raw JSON
    json_path = os.path.join(DATA_EXPORTS_DIR, 'ppr_completed_projects_RAW.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    print(f"Raw data saved to: {json_path}")

    # Save expanded JSON
    expanded_json_path = os.path.join(DATA_EXPORTS_DIR, 'ppr_completed_projects_FINAL.json')
    with open(expanded_json_path, 'w', encoding='utf-8') as f:
        json.dump(expanded_projects, f, ensure_ascii=False, indent=2)
    print(f"Final data saved to: {expanded_json_path}")

    # Convert to DataFrame and save as CSV
    if expanded_projects:
        df = pd.DataFrame(expanded_projects)
        df = clean_dataframe(df)

        csv_path = os.path.join(DATA_EXPORTS_DIR, 'ppr_completed_projects_FINAL.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"CSV saved to: {csv_path}")

        # Save as Excel
        excel_path = os.path.join(DATA_EXPORTS_DIR, 'ppr_completed_projects_FINAL.xlsx')
        try:
            df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"Excel saved to: {excel_path}")
        except ImportError:
            print("openpyxl not installed. Skipping Excel export.")
            print("Install with: pip install openpyxl")

        return df

    return None


def generate_summary_report(df):
    """
    Generate a summary report of the scraped data in data_exports folder
    """
    if df is None or df.empty:
        print("No data to summarize.")
        return

    report_path = os.path.join(DATA_EXPORTS_DIR, 'SUMMARY_REPORT.txt')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("CEPU PPR Funding Scheme - Data Collection Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data Source: {XML_DATA_URL}\n\n")

        f.write("-" * 40 + "\n")
        f.write("DATA SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Completed Projects: {len(df)}\n")
        f.write(f"Projects with Research Reports: {df['Research_Report_URL'].notna().sum()}\n")
        f.write(f"Data Fields: {len(df.columns)}\n\n")

        f.write("Data Fields:\n")
        for col in df.columns:
            f.write(f"  - {col}\n")

        f.write("\n" + "-" * 40 + "\n")
        f.write("SAMPLE DATA (First 5 Projects)\n")
        f.write("-" * 40 + "\n")
        f.write(df.head().to_string())

    print(f"Summary report saved to: {report_path}")


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("CEPU PPR Funding Scheme - Web Scraper")
    print("Target: Completed Projects with Research Reports")
    print("=" * 60)
    print()

    # Step 1: Fetch XML data
    print("Step 1: Fetching XML data file...")
    xml_root = fetch_xml_data()

    if xml_root is None:
        print("Failed to fetch XML data. Exiting.")
        return

    # Step 2: Parse XML and extract completed projects
    print("\nStep 2: Parsing XML and extracting completed projects...")
    projects = parse_xml_projects(xml_root)

    if not projects:
        print("\nNo completed projects found in XML data.")
        return

    print(f"\nFound {len(projects)} completed projects.")

    # Step 3: Save results (no need to expand since XML already has clean structure)
    print("\nStep 3: Saving results...")
    df = save_results(projects, projects)

    # Step 4: Download research reports
    print("\nStep 4: Downloading research reports...")
    download_stats = download_research_reports(projects)

    # Step 5: Generate summary report
    print("\nStep 5: Generating summary report...")
    generate_summary_report(df)

    print("\n" + "=" * 60)
    print("Scraping completed successfully!")
    print("=" * 60)

    # Display final statistics
    print(f"\nProjects found: {len(projects)}")
    print(f"Research reports found: {download_stats['total']}")
    print(f"Reports downloaded: {download_stats['successful']}")
    if download_stats['failed'] > 0:
        print(f"Failed downloads: {download_stats['failed']}")

    # Display sample data
    if df is not None and not df.empty:
        print("\nSample of extracted data (first 5 projects):")
        print(df[['Project Number', 'Project Title', 'Status', 'Research_Report_URL']].head().to_string())


if __name__ == "__main__":
    main()