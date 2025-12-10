# MechTherm Analytics
A Comprehensive GUI Application for Automated Materials Characterization Data Analysis

## Overview
MechTherm Analytics is a user-friendly desktop application designed for polymer and materials researchers. It provides automated analysis and visualization of common characterization techniques without requiring programming knowledge or complex software training.

Key Philosophy: Import Data → One-Click Analysis → Publication-Ready Results

The application currently supports:
- Tensile Testing - Stress-strain analysis with statistical processing
- Thermogravimetric Analysis (TGA) - Thermal decomposition characterization  
- Differential Scanning Calorimetry (DSC) - Glass transition temperature detection
- Dynamic Mechanical Analysis (DMA) - Coming soon

## Features

### Intuitive GUI Interface
- Clean tabbed interface for different analysis types
- Real-time status feedback and progress tracking
- No programming knowledge required
- Drag-and-drop file loading support

### Tensile Testing Analysis
- File Support: Instron .txt files, batch folder processing
- Automated Calculations:
  - Young's modulus (adaptive strain range detection)
  - Ultimate tensile strength (UTS)
  - Strain at break
  - Toughness (area under curve)
- Statistical Analysis: Mean ± standard deviation for multiple trials
- Output: Publication-ready stress-strain plots and summary tables

### TGA Analysis
- File Support: CSV format with temperature/weight data
- Automated Detection:
  - T5 (5% weight loss temperature)
  - T50 (50% weight loss temperature)  
  - Tmax (maximum decomposition rate temperature)
  - Residue at 600°C
- Visualization: Weight loss curves and derivative (DTG) plots
- Multi-sample comparison with overlay plotting

### DSC Analysis
- File Support: Multi-sheet Excel files (.xls/.xlsx)
- Smart Data Selection: Automatically identifies second heating cycle
- Tg Detection Methods:
  - Midpoint method (primary)
  - Inflection point method
  - Onset method
- Temperature Range: Optimized for polymer glass transitions (-60°C to +40°C)
- Output: Heat flow curves with Tg markers and analysis tables

### Export & Reporting
- Excel Export: Comprehensive results with multiple worksheets
- Publication Tables: Formatted mean ± std tables ready for papers
- High-Quality Plots: Professional formatting with customizable legends
- Batch Processing: Analyze multiple samples simultaneously

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
