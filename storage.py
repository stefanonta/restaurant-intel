import gc

import gspread
import utils

# def connect_spreasheet(configs_data):
#     '''
#     <- dict: Configuration data containing API keys and spreadsheet URL.
#     -> gspread.Worksheet Class Object
#     This function establishes a connection to the Google Sheet using gspread and returns the first worksheet object.
#     It uses the service account credentials file and spreadsheet URL specified in the config.yaml file.
#     '''
#     # Open a gspread connection using the service account credentials file
#     # -> gspread.Client
#     gc = gspread.service_account(filename=configs_data['other_settings']['credentials_file'])
#     # Open the Google Sheet by its URL
#     # -> gspread.Spreadsheet
#     sh = gc.open_by_url(configs_data['other_settings']['spreadsheet_url'])
#     # Return Worksheet Class object that represents the first worksheet (index 0) in the Google Sheet
#     # -> gspread.Worksheet
#     return sh.get_worksheet(0) 
#===================================================================================================================
def clear_sheet(worksheet):
    '''
    <- Worksheet Class Object: A gspread Worksheet object representing the Google Sheet to clear.
    -> None
    This functions clears all data from the first worksheet in the Google Sheet.
    '''
    worksheet.clear()
#===================================================================================================================
def write_row(worksheet, data_row):
    '''
    <- Worksheet Class Object: A gspread Worksheet object representing the Google Sheet to write to.
    <- dict: A dictionary whose keys represent the columns: date, issue_type, severity, note.
    -> None
    This functions appends a single row of analyzed review data to the Google Sheet.
    The input dictionary must have the following keys: date, issue_type, severity, note.
    '''
    # Build the row as a list in the correct order matching the Google Sheet columns: date, issue_type, severity, note
    # -> list
    row = [data_row['date'], data_row['issue_type'], data_row['severity'], data_row['note']]
    # Append the row as a new entry at the bottom of the worksheet
    worksheet.append_row(row)
    return None
#===================================================================================================================
if __name__ == "__main__":
    '''
    This function runs only when this script is executed directly (not imported as a module).
    It tests the connection to the Google Sheet and prints the content of cell A1.
    '''
    # Test the connection by reading cell A1 from the first worksheet
    # -> list
    # print(sh.get_worksheet(0).get('A1'))