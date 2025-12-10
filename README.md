# MechTherm Analytics  
*A Comprehensive GUI Application for Automated Materials Characterization Data Analysis*

---

## Overview

**MechTherm Analytics** is a standalone, user-friendly desktop application designed for materials and polymer researchers.  
It automates the analysis and visualization of common characterization techniques—no coding, no Excel scripting, no specialized software required.

**Philosophy:**  
 *Import Data → One Click → Publication-Ready Results*

Currently supported modules:

- **Tensile Testing** – Stress–strain processing with statistics  
- **Thermogravimetric Analysis (TGA)** – Decomposition profiling  
- **Differential Scanning Calorimetry (DSC)** – Tg detection  
- **Dynamic Mechanical Analysis (DMA)** – *Coming soon*

---

## Features

### Intuitive Graphical Interface
- Clean tab-based layout (Tensile, TGA, DSC, Results)
- Drag-and-drop file loading
- Real-time status and error logging
- Designed for non-programmers

---

## Tensile Testing Module

**Supported Files:** Instron `.txt` files and `.csv` formats

### Automated Calculations
- Young’s modulus with adaptive linear-range detection  
- Ultimate tensile strength (UTS)  
- Strain at break  
- Toughness (area under the stress–strain curve)

### Statistical Tools
- Multi-trial mean ± standard deviation  
- Coefficient of variation  
- Ready-to-publish summary tables

### Visualization
- Overlayed stress–strain curves  
- Professional journal-style plots  
- Interactive viewing inside the GUI

---

## Thermogravimetric Analysis (TGA)

**Supported Files:** `.csv` with *Time*, *Unsubtracted Weight*, *Temperature*

### Extracted Parameters
- **T5** – 5% weight-loss temperature  
- **T50** – 50% weight-loss temperature  
- **Tmax** – Maximum decomposition rate  
- **Residue at 600°C**

### Visual Outputs
- Weight (%) vs temperature curves  
- DTG (derivative) curves  
- Multi-sample overlays

---

## Differential Scanning Calorimetry (DSC)

**Supported Files:** `.xls` and `.xlsx` multi-sheet files

### Smart Data Selection
Automatically identifies the **second heating cycle (-90°C to 200°C)**.

### Tg Detection Methods
- **Midpoint method** *(primary)*  
- **Inflection point** *(derivative peak)*  
- **Onset method** *(baseline intersection)*  

### Outputs
- Heat flow curves  
- Tg markers  
- Summary tables for all samples  

---
## Export & Reporting

- **Excel Export**  
  - Statistical summaries  
  - Mean ± standard deviation tables  
  - Raw processed data  
- **Plot Export**
  - Publication-ready PNG/SVG plots
- **Batch Processing**
  - Load and analyze entire folders at once  

---
## Installation & Usage

### Requirements
pip install pandas numpy matplotlib scipy openpyxl xlrd tkinter

### Quick Start
1. Run the application:
   python materials_analyzer_app.py

2. Load your data:
   - Select appropriate analysis tab (Tensile/TGA/DSC)
   - Use "Load Files" or "Load from Folder"
   - Set analysis parameters if needed

3. Analyze & Export:
   - Click "Analyze Data" for automated processing
   - Generate plots with "Generate Plots"
   - Export results to Excel format

### Supported File Formats
- Tensile: .txt files (Instron format)
- TGA: .csv files with Time, Weight, Temperature columns
- DSC: .xls/.xlsx files with multiple heating cycles

## Application Architecture

GUI Interface (Tkinter)
├── Home Tab - Welcome & quick start
├── Tensile Tab - Stress-strain analysis
├── TGA Tab - Thermal decomposition
├── DSC Tab - Glass transition detection  
└── Results Tab - Formatted output display

Core Modules:
├── File I/O - Multi-format data readers
├── Analysis Engine - Automated calculations
├── Visualization - Publication-ready plotting
└── Export System - Excel & table generation

## Development Team
Developed for materials science research groups requiring efficient, standardized analysis workflows for polymer characterization.

Target Users: Graduate students, postdocs, and faculty working with polymer materials who need reliable, consistent analysis without extensive software training.

## Future Enhancements
- Dynamic Mechanical Analysis (DMA) module
- Advanced statistical analysis options
- Custom plot styling and themes
- Automated report generation
- Database integration for sample tracking
