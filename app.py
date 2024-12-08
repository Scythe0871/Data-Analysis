from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import sqlite3
import urllib.request
from pypdf import PdfReader
import ssl
import certifi
from io import BytesIO
import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

app = Flask(__name__)

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
    return results or []

def generate_bar_graph(data):
    if not data:
        return
    plt.figure(figsize=(20, 8))
    categories = [item[0] for item in data]
    counts = [item[1] for item in data]
    plt.bar(categories, counts, color='skyblue')
    plt.xlabel('Incident Nature')
    plt.ylabel('Counts')
    plt.title('Bar Graph Visualization [Nature of Incidents]')
    plt.xticks(rotation=90)
    plt.tight_layout()
    static_folder = os.path.join(app.root_path, 'static')
    os.makedirs(static_folder, exist_ok=True)
    file_path = os.path.join(static_folder, 'bargraph.png')
    plt.savefig(file_path)
    plt.close()

def cluster_incidents(data, k=5):
    if not data:
        return
    
    categories = [item[0] for item in data]
    counts = np.array([item[1] for item in data])
    
    X = np.column_stack((
        counts,  
        np.arange(len(counts))  
    ))
    
    X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X_normalized)
    
    plt.figure(figsize=(10, 8))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
    for i in range(k):
        mask = labels == i
        plt.scatter(X_normalized[mask, 0], 
                   X_normalized[mask, 1],
                   c=colors[i],
                   label=f'Cluster {i}',
                   alpha=0.6,
                   s=100)
    
    # Customize plot
    plt.title('Incident Clusters')
    plt.xlabel('Normalized Incident Count')
    plt.ylabel('Normalized Position')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.margins(0.1)
    static_folder = os.path.join(app.root_path, 'static')
    os.makedirs(static_folder, exist_ok=True)
    plt.savefig(os.path.join(static_folder, 'clusters.png'), 
                bbox_inches='tight', 
                dpi=300)
    plt.close()


def generate_pie_chart(data, top_n=5):
    if not data:
        return
    # Sort data by frequency (descending) and select top N incidents
    sorted_data = sorted(data, key=lambda x: x[1], reverse=True)[:top_n]
    labels = [item[0] for item in sorted_data]
    sizes = [item[1] for item in sorted_data]
    
    # Add "Other" category for remaining incidents
    other_size = sum([item[1] for item in data[top_n:]])
    if other_size > 0:
        labels.append('Other')
        sizes.append(other_size)
    
    plt.figure(figsize=(12, 12))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Pie Chart Visualization [Top Incident Types]')
    plt.tight_layout()
    static_folder = os.path.join(app.root_path, 'static')
    os.makedirs(static_folder, exist_ok=True)
    file_path = os.path.join(static_folder, 'piechart.png')
    plt.savefig(file_path)
    plt.close()

@app.route('/graph')
def graph():
    return render_template('results.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'url' in request.form and request.form['url']:
            urls = request.form['url'].split()
            db = createdb()
            for url in urls:
                pdf_data = fetchincidents(url)
                incidents = extractincidents(pdf_data)
                populatedb(db, incidents)
            results = status(db)
            db.close()
            if results:
                generate_bar_graph(results)
                cluster_incidents(results, k=5)
                generate_pie_chart(results, top_n=5)  # Pass top_n parameter
                return redirect(url_for('graph'))
            return 'No incidents found to display.', 404
        elif 'file' in request.files:
            file = request.files['file']
            if file:
                pdf_data = file.read()
                incidents = extractincidents(pdf_data)
                db = createdb()
                populatedb(db, incidents)
                results = status(db)
                db.close()
                if results:
                    generate_bar_graph(results)
                    cluster_incidents(results, k=5)
                    generate_pie_chart(results, top_n=5)  # Pass top_n parameter
                    return redirect(url_for('graph'))
                return 'No incidents found to display.', 404
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
