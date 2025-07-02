import pandas as pd
import json

def check_missing_fields(df, json_rules_path):
    """
    Checks for entirely missing fields for each component based on granular rules.

    This function is designed to run after the main QA process. It identifies
    which required 'Granular Container Tag's are completely missing for a component.
    It considers '[BLANK]' as a valid, present value.

    Args:
        df (pd.DataFrame): The main DataFrame after the initial QA process.
        json_rules_path (str): The file path for the component_groups_granular.json.

    Returns:
        pd.DataFrame: The DataFrame with an added 'Missing Fields' column.
    """
    print("Performing extra check for missing fields...")

    # Load the component group rules from your JSON file
    try:
        with open(json_rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
    except FileNotFoundError:
        print(f"Error: Rules file not found at {json_rules_path}")
        df['Missing Fields'] = 'Rules file not found'
        return df
        
    component_rules = {group['ComponentGroup']: group['ContainerName'] for group in rules['Groups']}

    # Add the new column for the check results, default to 'OK'
    df['Missing Fields'] = 'OK'

    # Group the DataFrame by 'Component' and 'SCSGroup' to check each one
    grouped = df.groupby(['Component', 'SCSGroup'])

    for (component, scs_group), group_df in grouped:
        if scs_group not in component_rules:
            # Skip components whose group is not defined in the rules file
            continue

        required_tags = set(component_rules[scs_group])
        present_tags = set(group_df['Granular Container Tag'])

        # Find the tags that are required but are not present for this component
        missing_tags = required_tags - present_tags

        # If there are any missing tags, record them in the new column for all rows of that component
        if missing_tags:
            missing_tags_str = ', '.join(missing_tags)
            df.loc[group_df.index, 'Missing Fields'] = missing_tags_str

    print("Missing fields check complete.")
    return df