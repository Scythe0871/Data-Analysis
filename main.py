import sqlite3
import urllib.request
from pypdf import PdfReader
import ssl
import certifi
import os
from io import BytesIO

def fetchincidents(url):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    }
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request, context=ssl_context)
    pdf_data = response.read()
    return pdf_data

def extractincidents(pdf_data):
    pdf_buffer = BytesIO(pdf_data)
    reader = PdfReader(pdf_buffer)
    incidents = []
    for page in reader.pages:
        text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False)
        if text:
            lines = text.split("\n")
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split("  ")  
                parts = [part.strip() for part in parts if part.strip()]
                if len(parts) == 5:
                    date_time, incident_number, location, nature, incident_ori = parts
                    incident = {
                        'date_time': date_time,
                        'incident_number': incident_number,
                        'location': location,
                        'nature': nature,
                        'incident_ori': incident_ori
                    }
                    incidents.append(incident)
    return incidents

def createdb(test_id=None):
    db_filename = f'resources/normanpd_{test_id}.db' if test_id else 'resources/normanpd.db'
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS incidents")  
    cursor.execute('''CREATE TABLE incidents (
                        incident_time TEXT,
                        incident_number TEXT UNIQUE,
                        incident_location TEXT,
                        nature TEXT,
                        incident_ori TEXT
                      )''')
    conn.commit()
    return conn

def populatedb(db, incidents):
    cursor = db.cursor()
    for incident in incidents:
        cursor.execute('''INSERT OR IGNORE INTO incidents 
                          (incident_time, incident_number, incident_location, nature, incident_ori)
                          VALUES (?, ?, ?, ?, ?)''', 
                       (incident['date_time'], incident['incident_number'], 
                        incident['location'], incident['nature'], incident['incident_ori']))
    db.commit()

def status(db):
    cursor = db.cursor()
    cursor.execute('''SELECT nature, COUNT(*) as count FROM incidents 
                      GROUP BY nature ORDER BY nature ASC''')
    results = cursor.fetchall()
    for row in results:
        print(f"{row[0]}|{row[1]}")

def main(urls):
    db = createdb()
    for url in urls:
        pdf_data = fetchincidents(url)
        incidents = extractincidents(pdf_data)
        populatedb(db, incidents)
    status(db)
    db.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", nargs='+', type=str, required=True, help="Incident summary URLs, space-separated.")
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
