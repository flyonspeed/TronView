import sqlite3
import os

class FAA_Aircraft:
    """Aircraft class to store aircraft data."""

    def __init__(self, data):
        self.n_number = data.get(0, "").strip()
        self.serial_number = data.get(1, "").strip()
        self.mfr_mdl_code = data.get(2, "").strip()
        self.eng_mfr_mdl = data.get(3, "").strip()
        self.year_mfr = data.get(4, "").strip()
        self.type_registrant = data.get(5, "").strip()
        self.owner_name = data.get(6, "").strip()
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

        self.aircraft_desc_mfr = ""   # final resolved manufacturer (either from FAA or from kit_mfr)
        self.aircraft_desc_model = "" # final resolved model (either from FAA or from kit_model)


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
        return f"{mfr}", f"{model}"
    else:
        return "",""


def find_aircraft_by_n_number(n_number)->FAA_Aircraft: # returns an Aircraft object
    """Search for an aircraft by N-Number using SQLite."""
    db_dir = "data/system/db"
    db_file = os.path.join(db_dir, "faa_aircraft.db")

    # if it starts with a n or N then remove it
    if n_number.startswith("n") or n_number.startswith("N"):
        n_number = n_number[1:]

    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.OperationalError as e:
        #print(f"Error connecting to SQLite database: {e}")
        return None, "", ""

    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM aircraft WHERE n_number = ?', (n_number,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Create an aircraft object from the row
    data = {i: row[i] for i in range(len(row))}
    aircraft = FAA_Aircraft(data)

    # If the kit_mfr is empty, try to get the manufacturer and model from the FAA database
    if aircraft.kit_mfr == "":
        aircraft_mfr, aircraft_model = get_aircraft_description(db_file, aircraft.mfr_mdl_code)

        if aircraft_mfr != "":
            aircraft.aircraft_desc_mfr = aircraft_mfr

        if aircraft_model != "":
            aircraft.aircraft_desc_model = aircraft_model
        else:
            aircraft.aircraft_desc_model = "Unknown"
    else:
        aircraft.aircraft_desc_mfr = aircraft.kit_mfr
        aircraft.aircraft_desc_model = aircraft.kit_model


    conn.close()
    return aircraft
