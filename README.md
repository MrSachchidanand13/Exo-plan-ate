# 🌌 Exoplanet Database Explorer 🚀

> xoplanet Database Explorer is a vibrant and feature-rich command-line tool designed for astronomy enthusiasts, students, and data explorers to dive deep into the fascinating world of exoplanets using real data from NASA’s Exoplanet Archive. With a colorful and intuitive interface, this tool transforms raw CSV files into an interactive experience—allowing users to search, browse, filter, and visualize thousands of planets beyond our solar system. Whether you're curious about recently discovered gas giants, searching for potentially habitable Earth-like worlds, or generating scientific reports with stunning visualizations, this CLI app brings the cosmos closer to your terminal. It bridges scientific accuracy with accessibility by providing layman explanations, statistical summaries, and beautiful PDF reports—making complex astronomical data easy to understand and exciting to explore.

---

## 📚 Table of Contents

- 🚀 [Features](#-features)
  - 🔍 [Data Exploration](#-data-exploration)
  - 📊 [Visualization and Reporting](#-visualization-and-reporting)
  - 🖥️ [User Interface](#️-user-interface)
  - ⚙️ [Data Processing](#-data-processing)
- 🧠 [Technical Architecture](#-technical-architecture)
  - 🧱 [Class Structure](#-class-structure)
  - 🗃️ [Database Schema](#-database-schema)
  - 🔄 [Data Pipeline](#-data-pipeline)
  - 🖼️ [Visualization Engine](#-visualization-engine)
- 🛠️ [Prerequisites](#️-prerequisites)
- 🚦 [Getting Started](#-getting-started)
- 🧭 [Usage](#-usage)
- 🗂️ [File Structure](#-file-structure)
- 📦 [Dependencies](#-dependencies)
- 🚀 [Performance Considerations](#-performance-considerations)
- 🧰 [Troubleshooting](#-troubleshooting)
- 🔮 [Future Enhancements](#-future-enhancements)
- 🤝 [Contributing](#-contributing)
- 📄 [License](#-license)

---

## 🚀 Features

### 🔍 Data Exploration

- 📄 **Interactive Browsing**  
  Paginated list of exoplanets with:
  - Sorting by name, year, mass, etc.
  - Pagination controls (next, prev, jump)
  - Customizable page sizes

- 🔎 **Advanced Search**  
  Search by:
  - Planet name, host star, discovery method, etc.
  - Range queries for mass, distance, temp
  - Fuzzy text matching (SQL `LIKE`)

- 🧠 **Special Categories**  
  Curated filters:
  - 🌍 Earth-like Planets  
  - 🪐 Gas Giants  
  - 🌞 Habitable Zone  
  - 📅 Recently Discovered  
  - 🛰️ Custom orbital ranges

- 🎲 **Random Planet Explorer**  
  - Get a surprise planet with a card-style view
  - Compare with others or fetch new ones

- 📈 **Database Statistics**  
  - Total counts, averages
  - Distribution histograms and pie charts
  - Mass classes: Earth-like, Super-Earths, Neptunes, etc.
  - Completeness % for key fields

---

### 📊 Visualization and Reporting

- 📝 **PDF Report Generation**  
  Uses `matplotlib` and `PdfPages` to generate:
  - Summary Stats
  - Pie Charts (types, discovery methods)
  - Bar Graphs (discovery over time)
  - Scatter plots (mass vs. radius)
  - Histograms (distance, orbital period)
  - 🌍 Habitable Zone insights

- ✏️ **Customizable Reports**
  - Filter by type, distance, mass, or manual selection
  - Custom title and filename support

- 🌍 **Earth Similarity Index (ESI)**
  - Compare planets with Earth based on habitability factors

---

### 🖥️ User Interface

- 🎨 **Colorful CLI**
  - `termcolor` for rich outputs
  - Headers, menus, prompts all styled with love
  - ASCII banners with `pyfiglet`

- 🧭 **Interactive Menus**
  - Lettered/numbered inputs
  - Input prompts with color-coded hints
  - Unicode loading spinners ⏳

- 🧾 **Data Display**
  - Planet Cards (name, type, star, etc.)
  - Comparison Tables
  - Layman explanations for hard terms
  - 🌠 Fun facts shown randomly!

---

### ⚙️ Data Processing

- 🔁 **Data Pipeline**
  - Processes NASA’s raw CSV (`data.csv`)
  - Cleans, converts units, fills missing fields

- 🧑‍🏫 **Layman Explanations**
  - Translates data into human-readable insights
  - Explains mass, radius, orbit, etc.

- ✅ **Validation**
  - Handles missing/invalid entries gracefully
  - Marks unknowns clearly

---

## 🧠 Technical Architecture

### 🧱 Class Structure

- `ExoplanetDatabase`  
  - Connects to MySQL (`pymysql`)
  - Executes all query logic
  - Gets planets, stats, categories

- `ExoplanetDisplay`  
  - Handles CLI visuals & output
  - Displays reports and menus
  - Uses `matplotlib` and `PdfPages`

- `ExoplanetExplorer`  
  - Main CLI controller
  - Connects UI with database
  - Tracks current selections and menus

---

### 🗃️ Database Schema

MySQL Table: `exo_planets`

| Column Name             | Type        | Description                             |
|------------------------|-------------|-----------------------------------------|
| `planet_name`          | VARCHAR     | Unique planet name                      |
| `host_star`            | VARCHAR     | Host star name                          |
| `discovery_method`     | VARCHAR     | Transit, Radial, etc.                   |
| `discovery_year`       | INTEGER     | Year of discovery                       |
| `planet_type`          | VARCHAR     | Gas Giant, Rocky, etc.                  |
| `star_type`            | VARCHAR     | G-type, M-type, etc.                    |
| `distance_value`       | FLOAT       | Light years from Earth                  |
| `earth_mass_ratio`     | FLOAT       | Mass vs. Earth                          |
| `earth_radius_ratio`   | FLOAT       | Radius vs. Earth                        |
| `earth_gravity_ratio`  | FLOAT       | Gravity vs. Earth                       |
| `orbital_period_days`  | FLOAT       | Orbit length in days                    |
| `star_temperature`     | FLOAT       | Star temperature (Kelvin)               |
| `assessment`           | VARCHAR     | Habitability assessment                 |
| `..._answer` fields    | TEXT        | Layman explanations                     |

---

### 🔄 Data Pipeline

Scripts:

- `data_processor.py` – Cleans and prepares from`data.csv`  
- `layman.py` – Adds human-friendly explanations  
- `upload.py` – Uploads everything to MySQL using `pymysql`

---

### 🖼️ Visualization Engine

Implemented in `ExoplanetDisplay.generate_exoplanet_report` using `matplotlib`:

- 📊 Pie Charts
- 📈 Bar Graphs
- 🌍 Scatter (mass vs. radius)
- 📉 Histograms (distance, orbit)
- 📃 Text pages
- Output via `PdfPages`

---

## 🛠️ Prerequisites

- Python 3.8+
- MySQL Server (localhost or remote)
- Internet (to download data from NASA)
- Terminal (Linux/Mac/Windows)
- Space: ~50MB for data + PDFs

---

## 🚦 Getting Started

### 🛰️ Step 1: Download the Data

> From the [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/)

Save as `data.csv` in the root directory.

---

### 🧹 Step 2: Process and Upload

```bash
python data_processor.py     # Clean + normalize
python layman.py             # Add layman info
python upload.py             # Upload to MySQL
```

📝 Update your MySQL credentials in `upload.py`:
```python
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='YOUR_PASSWORD_HERE',
    database='exo'
)
```

---

### 🔧 Step 3: Configure CLI Connection

In `exocli.py`:

```python
class ExoplanetDatabase:
    def __init__(self, host="localhost", user="root", password="YOUR_PASSWORD_HERE", database="exo"):
```

---

### 📦 Step 4: Install Dependencies

```bash
pip install pymysql argparse tabulate termcolor pyfiglet matplotlib numpy
```

Or use `requirements.txt`:

```txt
pymysql==1.0.2
argparse==1.4.0
tabulate==0.8.10
termcolor==1.1.0
pyfiglet==0.8.post1
matplotlib==3.5.2
numpy==1.22.4
```

```bash
pip install -r requirements.txt
```

---

### ▶️ Step 5: Run the App

```bash
python exocli.py
# OR skip welcome screen:
python exocli.py --quick
```

---

## 🧭 Usage

Menu options:

1️⃣ Browse Planets  
2️⃣ Search Planets  
3️⃣ Explore Categories  
4️⃣ Generate Reports  
5️⃣ Random Planet  
6️⃣ Quit

Use numbers or keys to navigate. All interactions use color prompts and smart retries for errors.

---

## 🗂️ File Structure

```
exoplanet-explorer/
├── data.csv
├── data_processor.py
├── layman.py
├── upload.py
├── exocli.py
├── requirements.txt
└── exoplanet_report_*.pdf
```

---

## 📦 Dependencies

- `pymysql` 🐬 – MySQL database connector
- `argparse` 🧾 – CLI argument parsing
- `tabulate` 📊 – Pretty tables
- `termcolor` 🌈 – Colored terminal output
- `pyfiglet` 🎨 – ASCII art banners
- `matplotlib` 📈 – Graphs and reports
- `numpy` ➕ – Math and stats

---

## 🚀 Performance Considerations

- Pagination uses `LIMIT` and `OFFSET`
- Limit report size to 100 planets for speed
- Optimize MySQL indices for large data
- Use `Agg` backend for `matplotlib` in headless systems

---

## 🧰 Troubleshooting

- 🛑 **MySQL Errors:** Check password, DB name, server status  
- 📉 **Upload Fails:** Confirm CSV format  
- ❌ **Missing Modules:** Run `pip install -r requirements.txt`  
- 🐢 **Slow Reports:** Lower planet count in selection

---

## 🔮 Future Enhancements

- 🌐 Web interface with Flask/Django  
- 📡 Real-time API sync with NASA  
- 🌌 3D or interactive Plotly graphs  
- 🤖 Machine learning predictions  
- 🏁 Unit test coverage  
- 🌍 Multi-language support

---



