# MechTherm Analytics
A Python Toolkit for Automated Tensile, DMA, TGA, and DSC Data Analysis

---

## Overview
This toolkit provides a unified Python workflow for analyzing materials characterization data commonly used in polymer and soft-materials research. It automates calculations normally performed manually in Excel and generates clean, publication-style plots.

The package currently supports:
- Tensile testing (Instron)
- Dynamic Mechanical Analysis (DMA)
- Thermogravimetric Analysis (TGA)
- Differential Scanning Calorimetry (DSC)

---

## Features

### Tensile Analysis
- Reads raw Instron `.txt` files  
- Computes:
  - Young’s modulus  
  - Ultimate tensile strength (UTS)  
  - Strain at break  
  - Toughness  
- Generates stress–strain curves

### DMA Analysis
- Imports E′, E″, and tan δ vs. temperature data  
- Extracts:
  - Glass transition temperature (Tg) from E′ onset and tan δ peak  
  - Storage modulus at chosen temperatures  
- Generates E′–temperature and tan δ–temperature plots

### TGA Analysis
- Converts mass to percent weight  
- Computes derivative weight loss (DTG)  
- Extracts:
  - T5  
  - T50  
  - Tmax  
- Generates TGA and DTG curves

### DSC Analysis
- Smooths and baseline-corrects heat-flow data  
- Identifies Tg (onset or midpoint)  
- Generates DSC thermograms

---

## Project Structure
materials_analysis/
│
├── io/               # data loaders
│   ├── read_tensile.py
│   ├── read_dma.py
│   ├── read_tga.py
│   └── read_dsc.py
│
├── analysis/         # computation logic
│   ├── tensile.py
│   ├── dma.py
│   ├── tga.py
│   └── dsc.py
│
├── plots/            # plotting utilities
│   ├── tensile_plot.py
│   ├── dma_plot.py
│   ├── tga_plot.py
│   ├── dsc_plot.py
│   └── style.py
│
├── examples/         # demo scripts and example datasets
├── tests/            # unit tests
└── README.md
