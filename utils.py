import yaml, gspread
from openai import OpenAI
#===================================================================================================================
def load_config(config_file):
    '''
    <- str: Path to the .yaml configuration file.
    -> dict: Configuration data as a dictionary.
    This function reads a .yaml config file and returns the content as a dictionary.
    '''
    with open(config_file, 'r') as file:
        # -> dict
        return yaml.safe_load(file)
#===================================================================================================================
def connect_spreasheet(configs_data):
    '''
    <- dict: Configuration data containing API keys and spreadsheet URL.
    -> gspread.Worksheet Class Object
    This function establishes a connection to the Google Sheet using gspread and returns the first worksheet object.
    It uses the service account credentials file and spreadsheet URL specified in the config.yaml file.
    '''
    # Open a gspread connection using the service account credentials file
    # -> gspread.Client
    gc = gspread.service_account(filename=configs_data['other_settings']['credentials_file'])
    # Open the Google Sheet by its URL
    # -> gspread.Spreadsheet
    sh = gc.open_by_url(configs_data['other_settings']['spreadsheet_url'])
    # Return Worksheet Class object that represents the first worksheet (index 0) in the Google Sheet
    # -> gspread.Worksheet
    return sh.get_worksheet(0) 
#===================================================================================================================
def create_openai_connection(configs_data):
    '''
    <- dict 
    -> Class OpenAI object used to connect to the openai LLM
    ''' 
    # Get the OpenAI API key from config data if provided
    api_key = configs_data['api_keys']['openai']
    # Instantiate the OpenAI client with the API key from config
    # -> OpenAI
    return OpenAI(api_key=api_key)