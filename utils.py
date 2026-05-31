import yaml, os, gspread, json
from openai import OpenAI
#===================================================================================================================
def load_config(config_file='config.yaml'):
    '''
    Load configuration from environment variables first, then from config.yaml as fallback.
    
    <- str: Path to the .yaml configuration file (default: 'config.yaml')
    -> dict: Configuration data as a dictionary
    '''
    
    # Try environment variables first
    env_config = {
        'clients': [{'name': 'La Deliziosa Pizzeria Restaurant', 'google_place_id': os.getenv('GOOGLE_PLACE_ID')}],
        'api_keys': {
            'google_maps': os.getenv('GOOGLE_MAPS_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY')
        },
        'other_settings': {
            'credentials_file': os.getenv('CREDENTIALS_FILE', 'service-account-credentials.json'),
            'spreadsheet_url': os.getenv('SPREADSHEET_URL'),
            'report_document_id': os.getenv('REPORT_DOCUMENT_ID')
        }
    }
    
    # If any required env var exists, use environment config
    if os.getenv('OPENAI_API_KEY'):
        return env_config
    
    # Otherwise, fall back to YAML file (local development)
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)
#===================================================================================================================
def connect_spreadsheet(configs_data):
    '''
    <- dict: Configuration data containing API keys and spreadsheet URL.
    -> gspread.Worksheet Class Object
    This function establishes a connection to the Google Sheet using gspread and returns the first worksheet object.
    It uses the service account credentials file and spreadsheet URL specified in the config.yaml file.
    If the program is ran from railway it connects to Google Sheets using credentials from environment variable (Railway)
    otherwise it connects to Google Sheets using the service account credentials file.
    '''
    if os.getenv('CREDENTIALS_FILE'):
        # On Railway: parse env var as JSON dict
        creds_dict = json.loads(os.getenv('CREDENTIALS_FILE'))
        worksheet = gspread.service_account_from_dict(creds_dict).open_by_url(configs_data['other_settings']['spreadsheet_url']).sheet1
    else:
        # Open a gspread connection using the service account credentials file
        # -> gspread.Client
        gc = gspread.service_account(filename=configs_data['other_settings']['credentials_file'])
        # Open the Google Sheet by its URL
        # -> gspread.Spreadsheet
        sh = gc.open_by_url(configs_data['other_settings']['spreadsheet_url'])
        # Return Worksheet Class object that represents the first worksheet (index 0) in the Google Sheet
        # -> gspread.Worksheet
        worksheet = sh.get_worksheet(0)
    return worksheet
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