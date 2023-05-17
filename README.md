# RuPaul's Drag Race — Web Scraping

This repository contains a Python script for web scraping and data extraction related to various seasons of RuPaul's Drag Race and related shows. The script downloads web pages, processes their content, and extracts information such as contestants, contestant progress, episodes, ratings, guest judges, and lipsyncs.

The resulting file is a JSON file, which contains all the information, organised in a way that can be used for further data visualisation, data analysis, etc.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3.x installed
- Required Python libraries: requests, pathlib, datetime, pyyaml, beautifulsoup4, slugify

## Getting Started

To get started with the script, follow these steps:

1. Clone this repository to your local machine.
2. Install the required Python libraries by running the following command:

   ```sh
   $ pip install -r requirements.txt
   ```

3. Create a `settings.yml` file in the root directory of the repository. The `settings.yml` file should contain the necessary access tokens and configurations required for accessing the Wikipedia API. Refer to the example `settings_template.yml` file for the required format.
4. Customise the list of page names (`PAGES`) in the script according to your needs. Add or remove page names to scrape the desired information.
5. Run the script by executing the following command:

   ```sh
   $ python scrape.py
   ```

The script will download the HTML content of the web pages, process the content, and store the extracted information in JSON format. The output will be saved in separate JSON files for each page as well as a combined JSON file named `all_shows.json`.

## License

This project is licensed under the [MIT License](LICENSE).

Feel free to customise and extend the script according to your requirements. Contributions are welcome!
