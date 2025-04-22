#!/usr/bin/env python3

import os
import sys
import csv
import zipfile
import requests
import argparse
import sqlite3
from prettytable import PrettyTable

"""
Description of MASTER.txt file

AIRCRAFT REGISTRATION MASTER FILE
Contains the records of all U.S. Civil Aircraft maintained by the FAA, Civil Aviation Registry, Aircraft
Registration Branch, AFS-750
Element
Position
Location in
Record
Number of
Positions Descriptions
N-Number 1-5 5 Identification number assigned to aircraft.
Serial Number 7-36 30 The complete aircraft serial number
assigned to the aircraft by the
manufacturer.
Aircraft Mfr Model
Code
38-44 7 A code assigned to the aircraft
manufacturer, model and series.
Positions (38-40) - Manufacturer Code
Positions (41-42) - Model Code
Positions (43-44) - Series Code
Engine Mfr Mode Code 46-50 5 A code assigned to the engine
manufacturer and model.
Positions (46-48) - Manufacturer Code
Positions (49-50) - Model Code
Year Mfr 52-55 4 Year manufactured.
Type Registrant 57 1 1 - Individual
2 - Partnership
3 - Corporation
4 - Co-Owned
5 – Government
7 - LLC
8 - Non Citizen Corporation
9 - Non Citizen Co-Owned
Registrant's Name 59-108 50
The first registrant's name which appears
on the Application for Registration, AC
Form 8050-1.
Street1 110-142 33 The street address which appears on the
Application for Registration, AC Form
8050-1 or the latest street address
reported.
Street2 144-176 33 The 2nd street address which appears on
the Application for Registration, AC,
Form 8050-1, or the latest street address
reported.
12/3/2020 T:/ARS-DEV/ONLINE-SUPPORT/WEBFILES.DOC
Element
Position
Location in
Record
Number of
Positions Descriptions
Registrant's City 178-195 18 The city name which appears on the
Application for Registration, AC Form
8050-1 or the latest address reported.
Registrant's State 197-198 2 The state name which appears on the
Application for Registration, AC Form
8050-1 or the latest address reported.
Registrant's Zip Code 200-209 10 The postal Zip Code which appears on the
Application for Registration, AC Form
8050-1 or the latest address reported.
Registrant's Region 211 1 1 - Eastern
2 - Southwestern
3 - Central
4 - Western-Pacific
5 - Alaskan
7 - Southern
8 - European
C- Great Lakes
E - New England
S - Northwest Mountain
County Mail 213-215 3 A code representing the county which
appears on the Application for
Registration.
Country Mail 217-218 2 A code representing the country which
appears on the Application for
Registration.
Last Activity Date 220-227 8 Format YYYY/MM/DD
Certificate Issue Date 229-236 8 Format YYYY/MM/DD
Certification requested
and uses:

	A - Airworthiness
	Classification Code

238 1 The airworthiness certificate class which
is reported on the Application for
Airworthiness, FAA Form 8130-6.
1 - Standard
2 - Limited
3 - Restricted
4 - Experimental
5 - Provisional
6 – Multiple
7 - Primary
8 - Special Flight Permit
12/3/2020 T:/ARS-DEV/ONLINE-SUPPORT/WEBFILES.DOC
Element
Position
Location in
Record
Number of
Positions Descriptions
9 – Light Sport

	B - Approved
	Operation Codes

239-247 9 The approved operations (up to a
maximum of six) which are reported on
the Application for Airworthiness, FAA
Form 8130-6.

	Standard 238 1

239 1 Blank
N - Normal
U - Utility
A - Acrobatic
T - Transport
G - Glider
B - Balloon
C - Commuter
O - Other
240-247 8 Positions are blank.

	Limited 238 1

239-247 9 Positions are blank.

	Restricted 238 1

239-245 7 May contain a code of 0-7.
0 - Other
1 - Agriculture and Pest Control
2 - Aerial Surveying
3 - Aerial Advertising
4 - Forest
5 - Patrolling
6 - Weather Control
7 - Carriage of Cargo
246-247 2 Positions are blank

	Experimental 238 1

239-245 7 May contain a code of 0-9.
0 - To show compliance with FAR
1 - Research and Development
2 - Amateur Built
3 - Exhibition
4 - Racing
5 - Crew Training
6 - Market Survey
12/3/2020 T:/ARS-DEV/ONLINE-SUPPORT/WEBFILES.DOC
Element
Position
Location in
Record
Number of
Positions Descriptions
7 - Operating Kit Built Aircraft
8A - Reg. Prior to 01/31/08
8B - Operating Light-Sport Kit-Built
8C - Operating Light-Sport Previously

	issued cert under 21.190

9A - Unmanned Aircraft - Research and
Development
9B - Unmanned Aircraft - Market Survey
9C - Unmanned Aircraft - Crew Training
9D - Unmanned Aircraft – Exhibition
9E - Unmanned Aircraft – Compliance

	With CFR

246-247 2 Positions are blank

	Provisional 238 1

239 1 1 - Class I
2 - Class II
240-247 8 Positions are blank

	Multiple 238 1

239-240 2 May contain a code of 1-3.
1 - Standard
2 - Limited
3 - Restricted
241-247 7 May be blank or contain:
0 - Other
1 - Agriculture and Pest Control
2 - Aerial Surveying
3 - Aerial Advertising
4 - Forest
5 - Patrolling
6 - Weather Control
7 - Carriage of Cargo

	Primary 238 1

239-247 9 Positions are blank

	Special Flight
	Permit

238 1
239-247 9 May contain a code of 1-6.
1 - Ferry flight for repairs, alterations,
maintenance or storage
2 - Evacuate from area of impending
12/3/2020 T:/ARS-DEV/ONLINE-SUPPORT/WEBFILES.DOC
Element
Position
Location in
Record
Number of
Positions Descriptions
danger
3 - Operation in excess of maximum
certificated
4 - Delivery or export
5 - Production flight testing
6 - Customer Demo

	Light Sport 238 1

239 1 May contain a code of A-W.
A - Airplane
G - Glider
L - Lighter than Air
P - Power-Parachute
W- Weight-Shift-Control
240-247 8 Positions are blank
Type Aircraft 249 1 1 - Glider
2 - Balloon
3 - Blimp/Dirigible
4 - Fixed wing single engine
5 - Fixed wing multi engine
6 - Rotorcraft
7 - Weight-shift-control
8 - Powered Parachute
9 - Gyroplane
H - Hybrid Lift
O - Other
Type Engine 251-252 2 0 - None
1 - Reciprocating
2 - Turbo-prop
3 - Turbo-shaft
4 - Turbo-jet
5 - Turbo-fan
6 - Ramjet
7 - 2 Cycle
8 - 4 Cycle
9 – Unknown
10 – Electric
11 - Rotary
"""
class Aircraft:
    def __init__(self, data):
        self.n_number = data.get(0, "").strip()
        self.serial_number = data.get(1, "").strip()
        self.mfr_mdl_code = data.get(2, "").strip()
        self.eng_mfr_mdl = data.get(3, "").strip()
        self.year_mfr = data.get(4, "").strip()
        self.type_registrant = data.get(5, "").strip()
        self.name = data.get(6, "").strip()
        self.street = data.get(7, "").strip()
        self.street2 = data.get(8, "").strip()
        self.city = data.get(9, "").strip()
        self.state = data.get(10, "").strip()
        self.zip_code = data.get(11, "").strip()
        self.region = data.get(12, "").strip()
        self.county = data.get(13, "").strip()
        self.country = data.get(14, "").strip()
        self.last_action_date = data.get(15, "").strip()
        self.cert_issue_date = data.get(16, "").strip()
        self.certification = data.get(17, "").strip()
        self.type_aircraft = data.get(18, "").strip()
        self.type_engine = data.get(19, "").strip()
        self.status_code = data.get(20, "").strip()
        self.mode_s_code = data.get(21, "").strip()
        self.fract_owner = data.get(22, "").strip()
        self.air_worth_date = data.get(23, "").strip()
        self.other_names = [data.get(i, "").strip() for i in range(24, 29)]
        self.expiration_date = data.get(29, "").strip()
        self.unique_id = data.get(30, "").strip()
        self.kit_mfr = data.get(31, "").strip()
        self.kit_model = data.get(32, "").strip()
        self.mode_s_code_hex = data.get(33, "").strip() if len(data) > 33 else ""

def download_file(url, filepath):
    print(f"Downloading US FAA Aircraft Database: {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    response = requests.get(url, stream=True, headers=headers)
    total_size_bytes = int(response.headers.get('content-length', 0))
    total_size_mb = total_size_bytes / (1024 * 1024)
    
    if response.status_code != 200:
        print(f"Error downloading file: HTTP status {response.status_code}")
        return False
        
    with open(filepath, 'wb') as f:
        downloaded_bytes = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded_bytes += len(chunk)
                downloaded_mb = downloaded_bytes / (1024 * 1024)
                percentage = int(100 * downloaded_bytes / total_size_bytes) if total_size_bytes else 0
                bar_length = 40
                done = int(bar_length * downloaded_bytes / total_size_bytes) if total_size_bytes else 0
                
                # Create the progress bar
                bar = "█" * done + "░" * (bar_length - done)
                
                sys.stdout.write(f"\r|{bar}| {percentage}% ({downloaded_mb:.2f}/{total_size_mb:.2f} MB)")
                sys.stdout.flush()
    
    print("\nDownload complete!")
    return True

def unzip_file(zipfile_path, outfile, extract_acftref=False):
    print(f"Extracting to {outfile} from zip archive...")
    try:
        outdir = os.path.dirname(outfile)
        with zipfile.ZipFile(zipfile_path, 'r') as zip_ref:
            # Look for MASTER.txt in the zip file
            for file in zip_ref.namelist():
                if file == "MASTER.txt" or file.endswith('/MASTER.txt'):
                    # Extract to a temporary location
                    temp_path = os.path.join(outdir, file)
                    zip_ref.extract(file, outdir)
                    
                    # Move the extracted file to the desired output location
                    if os.path.exists(temp_path) and temp_path != outfile:
                        # Move the file to the new location
                        # If the file already exists, replace it
                        if os.path.exists(outfile):
                            os.remove(outfile)
                        os.rename(temp_path, outfile)
                    
                    print(f"Successfully extracted to {outfile}")
                    
                    # If we also need to extract ACFTREF.txt
                    if extract_acftref:
                        acftref_outfile = os.path.join(outdir, "ACFTREF.txt")
                        for acftref_file in zip_ref.namelist():
                            if acftref_file == "ACFTREF.txt" or acftref_file.endswith('/ACFTREF.txt'):
                                # Extract ACFTREF.txt
                                zip_ref.extract(acftref_file, outdir)
                                temp_acftref_path = os.path.join(outdir, acftref_file)
                                
                                if os.path.exists(temp_acftref_path) and temp_acftref_path != acftref_outfile:
                                    if os.path.exists(acftref_outfile):
                                        os.remove(acftref_outfile)
                                    os.rename(temp_acftref_path, acftref_outfile)
                                
                                print(f"Successfully extracted ACFTREF.txt to {acftref_outfile}")
                                break
                        else:
                            print("File ACFTREF.txt not found in zip archive")
                    
                    return True
                    
            print("File MASTER.txt not found in zip archive")
            return False
    except Exception as e:
        print(f"Error extracting file: {e}")
        return False

def convert_to_sqlite(csv_file, db_file):
    """Convert the FAA CSV data to a SQLite database."""
    print(f"Converting {csv_file} to SQLite database {db_file}...")
    
    # First, count total lines to get an estimate for progress calculation
    try:
        total_lines = 0
        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            print("Counting total records for progress tracking...")
            for _ in f:
                total_lines += 1
        # Subtract 1 for the header row
        total_lines -= 1
        print(f"Found {total_lines} total records to process")
    except Exception as e:
        print(f"Error counting lines: {e}")
        total_lines = 0
    
    # Remove existing db file if it exists
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create the table structure
    cursor.execute('''
    CREATE TABLE aircraft (
        n_number TEXT PRIMARY KEY,
        serial_number TEXT,
        mfr_mdl_code TEXT,
        eng_mfr_mdl TEXT,
        year_mfr TEXT,
        type_registrant TEXT,
        name TEXT,
        street TEXT,
        street2 TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        region TEXT,
        county TEXT,
        country TEXT,
        last_action_date TEXT,
        cert_issue_date TEXT,
        certification TEXT,
        type_aircraft TEXT,
        type_engine TEXT,
        status_code TEXT,
        mode_s_code TEXT,
        fract_owner TEXT,
        air_worth_date TEXT,
        other_name1 TEXT,
        other_name2 TEXT,
        other_name3 TEXT,
        other_name4 TEXT,
        other_name5 TEXT,
        expiration_date TEXT,
        unique_id TEXT,
        kit_mfr TEXT,
        kit_model TEXT,
        mode_s_code_hex TEXT
    )
    ''')
    
    # Create indexes for faster searching
    cursor.execute('CREATE INDEX idx_mfr_mdl_code ON aircraft (mfr_mdl_code)')
    cursor.execute('CREATE INDEX idx_kit_mfr ON aircraft (kit_mfr)')
    cursor.execute('CREATE INDEX idx_kit_model ON aircraft (kit_model)')
    cursor.execute('CREATE INDEX idx_n_number ON aircraft (n_number)')
    
    try:
        # Read and insert data
        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            total_rows = 0
            batch_size = 1000
            batch = []
            
            for i, row in enumerate(reader):
                # Extend row if it's too short
                while len(row) < 34:
                    row.append('')
                
                # Extract other names (columns 24-28 in your Aircraft class)
                other_names = row[24:29] if len(row) >= 29 else [''] * 5
                while len(other_names) < 5:
                    other_names.append('')
                
                # Create a row tuple with 34 columns
                db_row = (
                    row[0].strip(),  # n_number
                    row[1].strip(),  # serial_number
                    row[2].strip(),  # mfr_mdl_code
                    row[3].strip(),  # eng_mfr_mdl
                    row[4].strip(),  # year_mfr
                    row[5].strip(),  # type_registrant
                    row[6].strip(),  # name
                    row[7].strip(),  # street
                    row[8].strip(),  # street2
                    row[9].strip(),  # city
                    row[10].strip(),  # state
                    row[11].strip(),  # zip_code
                    row[12].strip(),  # region
                    row[13].strip(),  # county
                    row[14].strip(),  # country
                    row[15].strip(),  # last_action_date
                    row[16].strip(),  # cert_issue_date
                    row[17].strip(),  # certification
                    row[18].strip(),  # type_aircraft
                    row[19].strip(),  # type_engine
                    row[20].strip(),  # status_code
                    row[21].strip(),  # mode_s_code
                    row[22].strip(),  # fract_owner
                    row[23].strip(),  # air_worth_date
                    other_names[0],   # other_name1
                    other_names[1],   # other_name2
                    other_names[2],   # other_name3
                    other_names[3],   # other_name4
                    other_names[4],   # other_name5
                    row[29].strip() if len(row) > 29 else '',  # expiration_date
                    row[30].strip() if len(row) > 30 else '',  # unique_id
                    row[31].strip() if len(row) > 31 else '',  # kit_mfr
                    row[32].strip() if len(row) > 32 else '',  # kit_model
                    row[33].strip() if len(row) > 33 else ''   # mode_s_code_hex
                )
                
                batch.append(db_row)
                total_rows += 1
                
                # Insert in batches for better performance
                if len(batch) >= batch_size:
                    cursor.executemany(
                        'INSERT OR REPLACE INTO aircraft VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        batch
                    )
                    conn.commit()
                    batch = []
                    
                    # Calculate and show percentage if we have a total line count
                    percentage = (total_rows / total_lines * 100) if total_lines > 0 else 0
                    sys.stdout.write(f"\rProcessed {total_rows} records ({percentage:.1f}%)...")
                    sys.stdout.flush()
            
            # Insert any remaining records
            if batch:
                cursor.executemany(
                    'INSERT OR REPLACE INTO aircraft VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    batch
                )
                conn.commit()
                
        print(f"\nConverted {total_rows} records to SQLite database")
        
    except Exception as e:
        print(f"Error converting to SQLite: {e}")
        conn.close()
        return False
        
    conn.close()
    return True

def find_aircraft_by_n_number(db_file, n_number):
    """Search for an aircraft by N-Number using SQLite."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM aircraft WHERE n_number = ?', (n_number,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None, "", ""
    
    # Create an aircraft object from the row
    data = {i: row[i] for i in range(len(row))}
    aircraft = Aircraft(data)
    
    conn.close()
    return aircraft, aircraft.mfr_mdl_code, (aircraft.kit_mfr, aircraft.kit_model)

def find_matching_aircraft(db_file, model_code, kit_mfr, kit_model):
    """Find all aircraft matching a model code or kit info using SQLite."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    matching_aircraft = []
    
    # Build query based on what we're searching for
    params = []
    query_parts = []
    
    if model_code:
        query_parts.append("mfr_mdl_code = ?")
        params.append(model_code)
    
    if kit_mfr and kit_model:
        query_parts.append("(kit_mfr = ? AND kit_model = ?)")
        params.extend([kit_mfr, kit_model])
    
    if not query_parts:
        conn.close()
        return []
    
    query = "SELECT * FROM aircraft WHERE " + " OR ".join(query_parts)
    cursor.execute(query, params)
    
    rows = cursor.fetchall()
    for row in rows:
        data = {i: row[i] for i in range(len(row))}
        aircraft = Aircraft(data)
        matching_aircraft.append(aircraft)
    
    conn.close()
    return matching_aircraft

def process_aircraft_reference(db_dir):
    """use ACFTREF.txt file to add manufacturer/model descriptions to the SQLite database."""
    # this file is in the same zip as the FAA N-Number database
    # and has the following columns: 
    # CODE	MFR	MODEL	TYPE-ACFT	TYPE-ENG	AC-CAT	BUILD-CERT-IND	NO-ENG	NO-SEATS	AC-WEIGHT	SPEED	TC-DATA-SHEET	TC-DATA-HOLDER
    
    return True

def add_aircraft_reference_to_db(db_file, reference_file):
    """Add aircraft reference data to the SQLite database."""
    print("Adding aircraft reference data to database...")
    
    if not os.path.exists(reference_file):
        print(f"Error: Reference file {reference_file} not found")
        return False
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create the table for aircraft reference data if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS aircraft_reference (
        code TEXT PRIMARY KEY,
        mfr TEXT,
        model TEXT,
        type_acft TEXT,
        type_eng TEXT,
        ac_cat TEXT,
        build_cert_ind TEXT,
        no_eng TEXT,
        no_seats TEXT,
        ac_weight TEXT,
        speed TEXT,
        tc_data_sheet TEXT,
        tc_data_holder TEXT
    )
    ''')
    
    # Create index on the code column
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_code ON aircraft_reference (code)')
    
    try:
        # First, count total lines to get an estimate for progress calculation
        total_lines = 0
        with open(reference_file, 'r', encoding='utf-8', errors='replace') as f:
            print("Counting total records for progress tracking...")
            for _ in f:
                total_lines += 1
        # Subtract 1 for the header row
        total_lines -= 1
        print(f"Found {total_lines} aircraft reference records to process")
        
        with open(reference_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            batch = []
            batch_size = 1000
            total_rows = 0
            
            for row in reader:
                # Ensure row has enough elements
                while len(row) < 13:
                    row.append('')
                
                # Create a row tuple
                db_row = tuple(item.strip() for item in row[:13])
                batch.append(db_row)
                total_rows += 1
                
                if len(batch) >= batch_size:
                    cursor.executemany(
                        'INSERT OR REPLACE INTO aircraft_reference VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        batch
                    )
                    conn.commit()
                    batch = []
                    
                    percentage = (total_rows / total_lines * 100) if total_lines > 0 else 0
                    sys.stdout.write(f"\rProcessed {total_rows} records ({percentage:.1f}%)...")
                    sys.stdout.flush()
            
            # Insert any remaining records
            if batch:
                cursor.executemany(
                    'INSERT OR REPLACE INTO aircraft_reference VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    batch
                )
                conn.commit()
            
            print(f"\nAdded {total_rows} aircraft reference records to the database")
            
    except Exception as e:
        print(f"Error adding aircraft reference data: {e}")
        conn.close()
        return False
    
    conn.close()
    return True

def update_database_timestamp(db_file):
    """Update the timestamp for when the database was last updated."""
    import datetime
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create the database_info table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS database_info (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    # Get the current timestamp in ISO format
    current_time = datetime.datetime.now().isoformat()
    
    # Update the last_updated timestamp
    cursor.execute(
        'INSERT OR REPLACE INTO database_info (key, value) VALUES (?, ?)',
        ('last_updated', current_time)
    )
    
    conn.commit()
    conn.close()
    
    return current_time

def get_database_timestamp(db_file):
    """Get the timestamp for when the database was last updated."""
    if not os.path.exists(db_file):
        return "Database not found"
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if the database_info table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='database_info'")
    if not cursor.fetchone():
        conn.close()
        return "Never updated"
    
    # Get the last_updated timestamp
    cursor.execute('SELECT value FROM database_info WHERE key = ?', ('last_updated',))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        # Convert ISO format to a more readable format
        import datetime
        try:
            timestamp = datetime.datetime.fromisoformat(result[0])
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return result[0]
    else:
        return "Never updated"

def get_aircraft_description(db_file, mfr_mdl_code):
    """Get the manufacturer and model description for an aircraft code."""
    if not mfr_mdl_code:
        return "Unknown aircraft type"
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if the aircraft_reference table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='aircraft_reference'")
    if not cursor.fetchone():
        conn.close()
        return f"Code: {mfr_mdl_code} (Reference data not available)"
    
    cursor.execute('SELECT mfr, model FROM aircraft_reference WHERE code = ?', (mfr_mdl_code,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        mfr, model = result
        return f"{mfr} {model}"
    else:
        return f"Code: {mfr_mdl_code} (Description not found)"

def main():
    parser = argparse.ArgumentParser(description='Search the FAA Aircraft Registration Database')
    parser.add_argument('--n-number', type=str, help='N-Number to search')
    parser.add_argument('--download-only', action='store_true', help='Only download the database without searching')
    parser.add_argument('--rebuild-db', action='store_true', help='Force rebuild of the SQLite database')
    parser.add_argument('--describe', type=str, help='Get description for an aircraft code')
    parser.add_argument('--show-timestamp', action='store_true', help='Show when the database was last updated')
    args = parser.parse_args()

    # Create directory structure for storing database files
    db_dir = "data/system/db"
    os.makedirs(db_dir, exist_ok=True)
    
    faa_url = "https://registry.faa.gov/database/ReleasableAircraft.zip"
    zip_file = os.path.join(db_dir, "ReleasableAircraft.zip")
    master_file = os.path.join(db_dir, "faa_nnumbers.txt")
    sqlite_db = os.path.join(db_dir, "faa_aircraft.db")
    acftref_file = os.path.join(db_dir, "ACFTREF.txt")
    
    # Check if user just wants to see the timestamp
    if args.show_timestamp:
        timestamp = get_database_timestamp(sqlite_db)
        print(f"FAA Database last updated: {timestamp}")
        return
    
    # Download and extract files if needed
    if not os.path.exists(master_file) or args.download_only:
        if not os.path.exists(zip_file) or args.download_only:
            if not download_file(faa_url, zip_file):
                return
                
        if not unzip_file(zip_file, master_file, extract_acftref=True):
            return
    
    # Convert to SQLite if needed
    db_updated = False
    if not os.path.exists(sqlite_db) or args.rebuild_db or args.download_only:
        if not convert_to_sqlite(master_file, sqlite_db):
            return
        db_updated = True
        
        # Add aircraft reference data to the database
        if os.path.exists(acftref_file):
            if not add_aircraft_reference_to_db(sqlite_db, acftref_file):
                print("Warning: Could not add aircraft reference data to the database")
        
        # Update the database timestamp
        timestamp = update_database_timestamp(sqlite_db)
        print(f"Database timestamp updated: {timestamp}")
    
    if args.download_only:
        print("Download and database conversion complete. Exiting.")
        return
    
    # If --describe argument is provided, just show the description for that code
    if args.describe:
        description = get_aircraft_description(sqlite_db, args.describe)
        print(f"Aircraft code {args.describe}: {description}")
        return
            
    if not args.n_number:
        print("Error: Missing required argument --n-number")
        parser.print_help()
        return
    
    # Show database timestamp
    timestamp = get_database_timestamp(sqlite_db)
    print(f"FAA Database last updated: {timestamp}")
    
    # Search for the aircraft in the SQLite database
    aircraft, model_code, kit_info = find_aircraft_by_n_number(sqlite_db, args.n_number)
    
    if not aircraft:
        print(f"No aircraft found with N-Number {args.n_number}")
        return
    
    # Get aircraft description
    aircraft_description = get_aircraft_description(sqlite_db, aircraft.mfr_mdl_code)
    
    # Display results for the single aircraft
    table = PrettyTable()
    table.field_names = [
        "N-Number", "SerialNumber", "Aircraft Type", "EngMfrMdl", "YearMfr", 
        "Name", "Street", "City", "State", "ZipCode", "LastActionDate", 
        "CertIssueDate", "Certification", "ModeSCode", "AirWorthDate", 
        "ExpirationDate", "KitMfr", "KitModel", "ModeSCodeHex"
    ]
    
    table.add_row([
        aircraft.n_number, aircraft.serial_number, aircraft_description,
        aircraft.eng_mfr_mdl, aircraft.year_mfr, aircraft.name,
        aircraft.street, aircraft.city, aircraft.state, aircraft.zip_code,
        aircraft.last_action_date, aircraft.cert_issue_date, aircraft.certification,
        aircraft.mode_s_code, aircraft.air_worth_date, aircraft.expiration_date,
        aircraft.kit_mfr, aircraft.kit_model, aircraft.mode_s_code_hex
    ])
    
    print(table)
    print(f"Found aircraft with N-Number {args.n_number}")

if __name__ == "__main__":
    main()
