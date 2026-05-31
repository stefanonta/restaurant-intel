import analyzer, storage, reporter, fetcher, utils
import json, pprint, yaml
from datetime import datetime
#===================================================================================================================
def main():
    '''
    <- None
    -> None
    This function is main "orchestrator" for the full review ingestion pipeline:
    1. Loads reviews from Google Maps API.
    2. Analyzes each review using the OpenAI LLM via analyzer.analyze_review().
    3. Writes each analyzed review as a new row in Google Sheets via storage.write_row().
    4. Generates and writes the weekly report to Google Docs via reporter.main().
    '''
    # Get the configuration data from the config.yaml file
    # -> dict
    configs = utils.load_config('config.yaml')
    # Connect to the Google Sheet and get the first worksheet object
    # -> gspread.Worksheet Class Object
    worksheet = utils.connect_spreasheet(configs)
    # Call the fetch_reviews function to get the reviews data from Google Maps API
    # -> dict
    reviews_data = fetcher.fetch_reviews(configs)
    # Handle the case where fetching reviews failed (reviews_data is None)
    if reviews_data is None:
        print("Failed to fetch reviews. Quitting the program.")
        return
    # Clear the Google Sheet before writing new data
    # -> None
    storage.clear_sheet(worksheet)
    # Write the header row to the Google Sheet
    # <- Worksheet Class Object: A gspread Worksheet object representing the Google Sheet to write to.
    # <- dict: A dictionary that represents a row to write in the Google Sheet
    storage.write_row(worksheet, {'date': 'date', 'issue_type': 'issue_type', 'severity': 'severity', 'note': 'note'})
    # Loop through each review and run the full ingestion pipeline
    for review in reviews_data['result']['reviews']:
        # Extract the raw review text
        # -> str
        review_text = review['text']
        # Extract the review date as a Unix timestamp and convert to YYYY-MM-DD format
        # -> int (Unix timestamp)
        review_date = datetime.fromtimestamp(review['time']).strftime('%Y-%m-%d')
        # Send the review text to the LLM for categorization
        # <- str
        # -> dict
        review_analysis = analyzer.analyze_review(review_text, configs)
        # Add the formatted date to the analysis result dictionary
        # <- str
        review_analysis['date'] = review_date
        # Write the completed single review analysis as a new row in Google Sheets
        # <- dict
        # -> None
        storage.write_row(worksheet, review_analysis)
    # Run the full reporting pipeline: load from Google Sheets, process the data, generate and write report to a Google Docs
    # -> dict
    reporter.main(configs, worksheet)
#===================================================================================================================
if __name__ == "__main__":
    '''
    This is the entry point of the program.
    Only runs the main() function if this script is executed directly (not imported as a module).
    '''
    print('Program Started...')
    main()
    print('Program Finished...')
    # Uncomment the line below to print each review analysis to the console during testing
    # pprint.pprint(review_analysis)