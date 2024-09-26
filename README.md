# Google Trends Analyzer 📈

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)
![GitHub Issues](https://img.shields.io/github/issues/pydoug/GoogleTrendsAnalyzer)
![GitHub Stars](https://img.shields.io/github/stars/pydoug/GoogleTrendsAnalyzer?style=social)

**Google Trends Analyzer** is a powerful Python tool that automates the downloading and analysis of real-time Google Trends data. It provides insightful visualizations and metrics to help you stay updated with the latest trending topics.

![Google Trends Analyzer Screenshot](https://img001.prntscr.com/file/img001/YLiB6OeMRAKOSN9tXLqjHA.png)

## Demo
1. **Trends Index**: Highlights the top 25 trending topics based on a custom index.
2. **Started**: Lists the most recent trending topics.
3. **Search Volume**: Shows the top 25 topics sorted by search volume.

## Features

- **Automated Data Retrieval**: Periodically fetches the latest trending searches from Google Trends.
- **Data Processing**: Cleans and processes raw data, calculating a custom "Trends Index" for each topic.
- **Real-Time Visualization**: Utilizes the Rich library to present data in an organized and visually appealing console interface.
- **Time-Based Comparisons**: Compares trends over the last 15 and 60 minutes to identify emerging or declining topics.
- **User-Friendly Configuration**: Easily configure download intervals and data directories through interactive prompts.

## Installation

### Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System**: Windows, macOS, or Linux.
- **Python**: Version 3.6 or higher installed. 
- **Google Chrome Browser**: Installed on your system.
- **Chrome WebDriver**: Compatible with your installed Chrome version.

### Setup Steps

1. **Clone the Repository**

   Open your terminal or command prompt and run:

   ```bash
   git clone https://github.com/pydoug/GoogleTrendsAnalyzer.git
   cd GoogleTrendsAnalyzer
   
2. **Install Required Packages**
   pip install -r requirements.txt

3.  ### Install Chrome WebDriver
  
  The project uses **Chrome WebDriver** to automate interactions with the Chrome browser.
  
  #### Download Chrome WebDriver:
  
  - Visit the [Official ChromeDriver Downloads Page](https://chromedriver.chromium.org/downloads).
  - Download the version that matches your installed Chrome browser version. You can check your Chrome version by navigating to `chrome://version/` in the browser.
  
  #### Install Chrome WebDriver:
  
  - **Windows:**
      - Extract the downloaded ZIP file.
      - Move the `chromedriver.exe` file to a folder of your choice (e.g., `C:\WebDriver`).
      - Add this folder to your system's `PATH` environment variable or note the path for later use.
  
  - **macOS/Linux:**
      - Extract the downloaded ZIP file.
      - Move the `chromedriver` executable to `/usr/local/bin/` or another directory included in your `PATH`.
  


  Provide Required Paths When Prompted
  When running main.py, you will be prompted to provide the following paths:
  
  Temporary Download Directory: Directory where temporary CSV files will be downloaded (e.g., C:\Downloads or /home/user/Downloads).
  Final Data Directory: Directory where processed CSV files will be saved (e.g., C:\GoogleTrendsAnalyzer\data or /home/user/GoogleTrendsAnalyzer/data).
  ChromeDriver Path: Full path to the chromedriver executable (e.g., C:\WebDriver\chromedriver.exe or /usr/local/bin/chromedriver).

   
