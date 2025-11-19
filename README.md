# 540.635_Final_Project
MechTherm Analytics

A Python Toolkit for Automated Tensile, DMA, TGA, and DSC Data Analysis

Overview

This toolkit provides a unified Python workflow for analyzing several types of materials characterization data used in polymer and soft-materials research.
It automates calculations that are normally done manually in Excel and generates standardized, publication-quality plots.

The package supports four major characterization techniques:

Tensile testing (Instron)

Dynamic Mechanical Analysis (DMA)

Thermogravimetric Analysis (TGA)

Differential Scanning Calorimetry (DSC)

The goal is to make data processing faster, reproducible, and consistent across experiments.

Features
1. Tensile Analysis

Reads raw Instron text files

Computes:

Young’s modulus (automatic linear-region fit)

Ultimate tensile strength (UTS)

Strain at break

Toughness

Generates stress–strain curves for single or multiple samples

2. DMA Analysis

Imports E′, E″, and tan δ data

Extracts:

Glass transition temperature from E′ and tan δ

Storage modulus at selected temperatures (e.g., 25 °C)

Produces E′–T and tan δ–T plots

3. TGA Analysis

Converts mass to % weight

Computes derivative weight loss (DTG)

Determines:

T₅ (5% weight loss)

T₅₀

Tmax (DTG peak position)

Outputs TGA + DTG curves

4. DSC Analysis

Smooths and baseline-corrects heat-flow data

Identifies Tg (onset or midpoint)

Generates clean DSC thermograms
