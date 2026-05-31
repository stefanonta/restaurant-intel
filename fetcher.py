import requests, json
import utils
from pprint import pprint

#===================================================================================================================
def fetch_reviews(configs_data):
    '''
    <- dict: Configuration data containing API keys and place ID.
    This function fetches the business name and all reviews from Google Maps using the Places API.
    '''
    # Extract API key and place ID from the configuration data
    google_maps_api_key = configs_data['api_keys']['google_maps']
    google_place_id = configs_data['clients'][0]['google_place_id']

    # Build the Google Places API request URL with the required fields
    # -> str
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json?"
        f"place_id={google_place_id}&fields=name,reviews&key={google_maps_api_key}"
    )
    # Make the API request to fetch reviews  from Google Maps and handle potential errors
    try:
        # -> requests.Response
        response = requests.get(url, timeout=10)
        # Checks if the HTTP request was successful (status code 200-299). If not, it raises an HTTPError.
        response.raise_for_status()
        # -> dict
        data = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    # if try succeeded, return the API response data as a dictionary; otherwise, return None
    else:
        # -> dict
        return data
#===================================================================================================================

if __name__ == "__main__":
    # Load configuration data from config.yaml
    # -> dict
    configs = utils.load_config('config.yaml')
    google_maps_api_key = configs['api_keys']['google_maps']
    google_place_id = configs['clients'][0]['google_place_id']
    
    # Fetch reviews using the API key and place ID from config
    # -> dict
    reviews = fetch_reviews(google_maps_api_key, google_place_id)
    # Save the raw API response to a local JSON file for inspection
    with open('sample_review.json', mode='w') as f:
        json.dump(reviews, f, indent=2)
    print('Program Finished...')
    