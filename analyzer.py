import json, utils, prompts
#===================================================================================================================
def analyze_review(review, configs_data):
    '''
    <- str: text of a customer review.
    -> dict: a dictionary with keys: issue_type, severity, note.
    This function sends a single review to the OpenAI LLM for categorization and returns a structured analysis of the review.
    '''
    client = utils.create_openai_connection(configs_data)
    response = client.chat.completions.create(
        model="gpt-5.4-nano-2026-03-17",
        response_format={"type": "json_object"},  # instructs the LLM to output a single JSON object
        messages=[
            # system role: provides persona and categorization instructions to the LLM
            {
                "role": "system",
                "content": prompts.ANALYZER_SYSTEM_MESSAGE
            },
            # user role: provides the actual review text to analyze
            {
                "role": "user",
                "content": review
            }
        ]
    )
    # Parse the JSON string from the LLM response into a Python object
    # -> dict (or list if the LLM misbehaves and returns multiple objects)
    analysis = json.loads(response.choices[0].message.content)
    # I expect a single dict but if the LLM misbehave and wraps into a list, I take the first element to avoid breaking the downstream code
    if isinstance(analysis, list):
        analysis = analysis[0]
    # -> dict
    return analysis
#===================================================================================================================
if __name__ == "__main__":
    # Load configuration data from config.yaml
    # -> dict
    configs = utils.load_config('config.yaml')
    analysis = analyze_review('The restaurant was amazing the pizza was the best', configs)
    print(type(analysis))  # expected: <class 'dict'>
    print(analysis)