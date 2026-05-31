import gspread, json
import utils, prompts
import pandas as pd
from pprint import pprint
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
#===================================================================================================================
def process_summarized_reviews(tabular_data):
    '''
    <- list[dict]: a list of dictionaries. Each dictionary is a row keyed by column name.
    -> str: CSV-formatted string with columns: date, issue_type, count, pct_change, total_issues, pct_of_weekly_total.
    This function is part of the pipeline, it processes review data into structured issue counts and metrics by week.
    '''
    # -> pd.DataFrame
    reviews_df = pd.DataFrame(tabular_data)
    # convert the `date` column to datetime objects for time-based analysis
    # <- pd.Series[str]
    # -> pd.Series[datetime]
    reviews_df['date'] = pd.to_datetime(reviews_df['date'])
    # Week periods for each review date (e.g., 2026-05-11/2026-05-17)
    # -> pd.PeriodIndex
    week_periods = reviews_df['date'].dt.to_period('W')
    # Count of each issue_type per week with index reset and count column named
    # -> pd.DataFrame
    issue_type_counts_by_week = (
        reviews_df.groupby(week_periods)['issue_type']
        .value_counts()
        .reset_index(name='count')
    )
    # Final data sorted by issue_type and week for reporting output
    # -> pd.DataFrame
    issue_type_counts_sorted = (
        issue_type_counts_by_week
        .sort_values(['issue_type', 'date'], ascending=[True, True])
        .reset_index(drop=True)
    )
    # Week-over-week percentage change for each issue_type, aligned with DataFrame rows
    # -> pd.Series[float]
    issue_type_pct_change = (
        issue_type_counts_sorted
        .groupby('issue_type')['count']
        .pct_change(fill_method=None) * 100
    )
    # add the percentage change as a new column in the final DataFrame
    # <- pd.Series[float]
    # -> pd.Series[float]
    issue_type_counts_sorted['pct_change'] = issue_type_pct_change.round(2)
    # Sum of issue counts per week
    # -> pd.Series[int]
    total_issues = issue_type_counts_sorted.groupby('date')['count'].transform('sum')
    # add the total issues as a new column in the final DataFrame
    # <- pd.Series[int]
    issue_type_counts_sorted['total_issues'] = total_issues
    # Percentage of total weekly issues for each issue type
    # -> pd.Series[float]
    issue_type_counts_sorted['pct_of_weekly_total'] = (issue_type_counts_sorted['count'] / issue_type_counts_sorted['total_issues'] * 100).round(2)
    # Final processed data as CSV string (index excluded as it is not meaningful for the report)
    # -> str
    return issue_type_counts_sorted.to_csv(None, index=False)
#===================================================================================================================
def generate_report(csv_string_report, configs):
    '''
    <- str: CSV-formatted data with columns: date, issue_type, count, pct_change, total_issues, pct_of_weekly_total.
    -> str: A full report based on all fetched reviews interpreting the data for the restaurant owner.
    This functions is part of the pipeline, generates a consultative business report from structured issue data using OpenAI LLM.
    '''
    # -> OpenAI Class Object
    client = utils.create_openai_connection(configs)
    # -> openai.types.chat.ChatCompletion
    response = client.chat.completions.create(
        model="gpt-5.4-nano-2026-03-17",
        messages=[
            {
                "role": "system",
                "content": prompts.REPORTER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompts.get_reporter_user_prompt(csv_string_report)
            }
        ]
    )
    # Extract text from OpenAI response object and strip leading/trailing whitespace
    # -> str
    return response.choices[0].message.content.strip()
#===================================================================================================================
def write_report(text_string, configs):
    '''
    <- str: The narrative report content to write.
    -> None
    This functions is part of the pipeline, writes the generated report text to a Google Doc.
    '''
    # Path to service account credentials file
    # -> str
    credentials = configs['other_settings']['credentials_file']
    # Google Document ID where the report will be written
    # -> str
    DOCUMENT_ID = configs['other_settings']['report_document_id']
    # API scopes required for the service account to access Google Docs
    # -> list[str]
    SCOPES = ['https://www.googleapis.com/auth/documents']
    # -> google.oauth2.service_account.Credentials
    # Service account credentials loaded from the JSON credentials file
    creds = Credentials.from_service_account_file(credentials, scopes=SCOPES)
    # Authenticated Google Docs API service instance
    # -> googleapiclient.discovery.Resource
    docs_service = build('docs', 'v1', credentials=creds)
    # End index of the last element in the document body, used to define the deletion range
    # -> int
    end_index = docs_service.documents().get(documentId=DOCUMENT_ID).execute()['body']['content'][-1]['endIndex']
    # Clear the document first, then write the new report.
    # deleteContentRange removes all existing content (index 1 to end_index - 1, preserving the mandatory final newline).
    # insertText then writes the new report starting at index 1.
    # -> None
    docs_service.documents().batchUpdate(
        documentId=DOCUMENT_ID,
        body={
            'requests': [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index - 1
                        }
                    }
                },
                {
                    'insertText': {
                        'location': {'index': 1},  # Position 1 is the very first character position in the document body
                        'text': text_string
                    }
                }
            ]
        }
    ).execute()
    return None
#===================================================================================================================
def main(configs_data, worksheet):
    '''
    <- dict: Configuration data containing credentials, document ID, and other settings.
    -> None
    This is the function that is the orchestrator for this module, it executes the report generation pipeline.
    '''
    # Get all summarized reviews rows from Google Sheets
    # -> list[dict]
    worksheet_data = worksheet.get_all_records()
    # Process the raw data into a structured CSV string for reporting
    # <- list[dict]
    # -> str
    csv_report = process_summarized_reviews(worksheet_data)
    # Generate a narrative report from the structured data using OpenAI
    # <- str
    # -> str
    report_text = generate_report(csv_report, configs_data)
    # Write the generated report to a Google Doc
    # <- str
    # -> None
    write_report(report_text, configs_data)
#===================================================================================================================
if __name__ == "__main__":
    '''
    This function runs only when this script is executed directly (not imported as a module).
    It executes the main report generation pipeline.
    '''
    configs_data = utils.load_config('config.yaml')
    worksheet = utils.connect_spreasheet(configs_data)
    print("Starting report generation process...")
    main(configs_data, worksheet)