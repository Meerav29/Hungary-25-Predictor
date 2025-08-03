# 🗂️ **Data Collection Plan** (`docs/data_plan.md`)

---

## **Project Goal**

Collect all relevant data needed to predict the 2025 Hungarian Grand Prix winner, leveraging historical F1 race results, driver/car performance metrics, and weather information.

---

### **1. Data Types & Requirements**

| Data Type         | Source(s)              | Coverage/Years                                | Description                                    |
| ----------------- | ---------------------- | --------------------------------------------- | ---------------------------------------------- |
| Race Results      | FastF1 API             | 2018–2024 Hungarian GP, all 2025 races so far | Finishing position, time gaps, DNFs            |
| Qualifying Data   | FastF1 API             | Same as above                                 | Grid positions, qualifying times               |
| Lap Times/Sectors | FastF1 API             | Same as above                                 | Per-lap and per-sector times                   |
| Pit Stops         | FastF1 API             | Same as above                                 | Number, timing, duration, tire choice          |
| Weather           | FastF1, OpenWeatherMap | Same as above                                 | Track temp, ambient temp, rainfall, wind, etc. |
| Driver/Team Info  | FastF1, FIA, Wikipedia | All relevant years                            | Team, driver, car info, mid-season changes     |
| Track Data        | FastF1                 | All relevant years                            | Track layout, DRS zones, SC/incident frequency |

---

### **2. Data Sources**

* **FastF1 API:**
  Primary source for all timing, session, car, driver, and some weather data
  [FastF1 Docs & Examples](https://theoehrly.github.io/Fast-F1/)
* **OpenWeatherMap API:**
  For more detailed weather data (especially for historical or forecasted sessions)
  [OpenWeatherMap](https://openweathermap.org/api)
* **FIA, Wikipedia:**
  For supplementary data: car/driver changes, entry lists, etc.

---

### **3. File Formats**

* **Raw Data:** CSV (for portability and transparency)
* **Processed Data:** Parquet or Pickle (for performance and pipeline)
* **Documentation:** Markdown (`docs/`)

---

### **4. Data Collection Workflow**

1. **Create scripts in `src/data/` for:**

   * Downloading Hungarian GP and all 2025 races from FastF1
   * Downloading weather data for each relevant session
   * Storing all files in `/data/raw/` with clear naming

2. **Log data sources and file versions in a `data_log.md`**

---

### **5. To-Do:**

* [ ] List years and races to collect (start with 2018–2024 Hungary + 2025 season to-date)
* [ ] Script to download and save session data for each event
* [ ] Script/API calls to fetch matching weather data
* [ ] Documentation of any data limitations/missing fields

---

### **6. Potential Challenges & Notes**

* Some weather data may be missing; document any gaps.
* If driver lineups change mid-season, make sure to track it per race.
* Some data (e.g., SC periods, incidents) might need additional parsing or manual checks.

---

### **References**

* FastF1 documentation and examples
* OpenWeatherMap documentation

---

## **Next Steps**

**Now that the data plan is clear:**

1. **Create the file in `/docs` and push to GitHub**
2. **Start working on .gitignore (I can give you a template)**
3. **Open GitHub Issues for each of the initial scripts and tasks**
