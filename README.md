# NASA Battery Aging Analysis

This repository focuses on analyzing Li-ion battery aging using the NASA Battery Dataset. By extracting and visualizing key internal parameters—such as Electrolyte Resistance (Re) and Charge Transfer Resistance (Rct)—the project aims to assist researchers in understanding how battery characteristics evolve over time and usage cycles.

## Table of Contents

- [Introduction](#introduction)
- [Objectives](#objectives)
- [Dataset](#dataset)
- [Data Processing](#data-processing)
- [Installation](#installation)
- [Results](#results)
- [Contributing](#contributing)
- [Contact](#contact)

## Introduction

As Li-ion batteries age, their internal parameters change, impacting performance and lifespan. This project merges raw measurement CSV files with corresponding metadata to produce a clear picture of how Re and Rct vary over testing cycles. Through interactive plots, it provides a visual understanding of the aging process, supporting better diagnostics and maintenance strategies.

## Objectives

1. **Integrate Metadata and Measurements**: Combine multiple CSV files and metadata to create a unified dataset.
2. **Data Cleaning and Conversion**: Ensure Re and Rct are properly parsed as numeric values.
3. **Visualization**: Generate separate, interactive plots for Rct (full dataset) and Re  to illustrate aging trends.
4. **Insights for Researchers**: Support battery engineers and researchers in diagnosing battery health and predicting end-of-life conditions.

## Dataset

The NASA Battery Dataset includes:
- **Measurement Files**: Containing voltage, current, temperature, and time at various test cycles.
- **Metadata File**: Linking each measurement file to its test conditions, battery ID, Re, Rct, capacity, and ambient temperature.

## Data Processing

- Load and merge all measurement files using keys from the metadata.
- Convert columns (Re, Rct) to numeric, dropping rows where necessary for the Re-specific plot.
- Produce aggregated DataFrames suitable for plotting and analysis.

## Installation

### Prerequisites

- Python 3.x
- Pandas
- Dask
- Plotly

### Results
Rct Plot: Shows all batteries across their test cycles, unaffected by Re filtering.
Re Plot: Highlights only those cycles with valid Re values, offering a clean view of electrolyte resistance changes over time.

### Contact
For questions or suggestions, please open an issue or reach out at [utkarshtiwar89@gmail.com].
