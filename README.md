# Incident Report Submission and Analysis System

## Overview

This project is a web application designed to facilitate the submission, analysis, and visualization of incident reports. Users can either upload incident reports in PDF format or provide URLs to PDFs hosted online. The system extracts data from these reports, stores it in a database, and generates visualizations to aid in understanding the nature and frequency of incidents.

---

## Features

1. **Incident Submission**
    - Users can submit incident reports via:
      - Directly entering URLs to incident report PDFs(one or multiple urls).
      - Uploading PDF files.

2. **Data Extraction**
    - Extracts incident details from the PDF files, including:
      - Date and time
      - Incident number
      - Location
      - Nature of the incident
      - Origin of the incident

3. **Database Management**
    - Stores the extracted incident data in a SQLite database.
    - Ensures data integrity by using unique constraints on incident numbers.

4. **Visualizations**
    - **Bar Graph:** Displays the frequency of various types of incidents.
    - **Cluster Visualization:** Groups incidents into clusters based on their nature and frequency.
    - **Pie Chart:** Shows the distribution of incidents by origin.

5. **User Interface**
    - An intuitive web-based interface for submitting reports and viewing analysis results.

---

## File Structure

- **index.html**:
  - Entry point of the application.
  - Contains a form for submitting URLs or uploading PDF files.

- **results.html**:
  - Displays the generated visualizations including:
    - Bar graph of incident types.
    - Clustered analysis of incidents.

- **app.py**:
  - Core backend logic implemented using Flask.
  - Handles routes for:
    - Incident submission (`/`)
    - Displaying visualizations (`/graph`)
  - Contains functions for:
    - Fetching and parsing incident data from PDFs.
    - Database creation and population.
    - Generating visualizations.

---

## Installation and Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.7+
- pip

### Installation Steps
1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up the project structure:
    ```bash
    mkdir static
    mkdir resources
    ```

4. Run the application:
    ```bash
    python app.py
    ```

5. Access the application at `http://127.0.0.1:5000` in your web browser.

---

## Usage

1. **Submit Incident Reports:**
   - Navigate to the homepage.
   - Enter URLs for incident PDFs or upload a file.
   - Click "Submit" to process the data.

2. **View Results:**
   - Upon successful submission, you will be redirected to a results page.
   - View the bar graph and clustered visualizations of the submitted data.

3. **Submit More Reports:**
   - Use the link on the results page to return to the submission form.

---

## Key Technologies

- **Backend:** Flask
- **Database:** SQLite
- **Data Processing:** PyPDF, Matplotlib, NumPy, scikit-learn (KMeans)
- **Frontend:** HTML, CSS

---

## Future Enhancements

- Support for additional file formats (e.g., Word documents).
- Advanced clustering algorithms for better incident categorization.
- Integration with external APIs for real-time incident data.
- User authentication and role-based access control.

---

## Troubleshooting

1. **Error: PDF data not extracted**
   - Ensure the PDFs contain selectable text and are not scanned images.

2. **Database errors**
   - Check if the `resources` directory exists and has write permissions.

3. **Static files not loading**
   - Ensure the `static` directory exists and is correctly configured.

---



