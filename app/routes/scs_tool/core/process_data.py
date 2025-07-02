import pandas as pd
import json
import os

def process_data(json_path, container_name, df):
    """
    Processes a standard report, checks accuracy, and provides the correct value on error.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        mask = df['ContainerName'] == container_name
        df.loc[mask, 'Accuracy'] = f'ERROR: {container_name} JSON not found or invalid'
        return df

    container_data = json_data.get(container_name, {})
    
    # Create an inverted map for very fast lookups of the correct value.
    # Maps each component to its one correct container value.
    component_to_value_map = {
        component: value
        for value, components in container_data.items()
        for component in components
    }

    # Create a boolean mask for the rows that match the current container
    mask = df['ContainerName'] == container_name
    # Get a copy of the relevant subset to avoid SettingWithCopyWarning
    relevant_df = df[mask].copy()

    def check_accuracy_and_get_correct_value(row):
        """
        Checks a single row and returns a tuple of (status, correct_value).
        """
        component = row['Component']
        current_value = row['ContainerValue']
        
        # Find the correct value for the component from our map.
        correct_value = component_to_value_map.get(component)
        
        if correct_value is not None:
            # A correct value exists for this component. Check if it matches.
            if current_value == correct_value:
                return (f'SCS {container_name} OK', '') # Status OK, no correct value needed.
            else:
                return (f'ERROR: {container_name}', correct_value) # Status ERROR, provide the correct value.
        else:
            # This component was not found anywhere in the JSON for this container.
            return (f'ERROR: {container_name}', 'Component Not Found in JSON')

    # Only apply the check if there are relevant rows to process
    if not relevant_df.empty:
        # The result of .apply() will be a Series of tuples.
        results = relevant_df.apply(check_accuracy_and_get_correct_value, axis=1)
        # Efficiently assign the tuples to the two target columns.
        relevant_df[['Accuracy', 'Correct Value']] = pd.DataFrame(results.tolist(), index=relevant_df.index)
        # Update the original DataFrame with the results from the processed subset.
        df.update(relevant_df)
    
    return df


def process_data_granular(json_path, container_name, df_g):
    """
    Processes a granular report, checks accuracy, and provides the correct value on error.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        mask = df_g['Granular Container Tag'] == container_name
        df_g.loc[mask, 'Accuracy'] = f'ERROR: {container_name} JSON not found or invalid'
        return df_g

    container_data = json_data.get(container_name, {})
    
    # Create the inverted map for fast lookups.
    component_to_value_map = {
        component: value
        for value, components in container_data.items()
        for component in components
    }
    
    mask = df_g['Granular Container Tag'] == container_name
    relevant_df = df_g[mask].copy()

    def check_granular_accuracy_and_get_correct_value(row):
        """
        Checks a single granular row and returns a tuple of (status, correct_value).
        """
        component = row['Component']
        current_granular_value = row['Granular Container Value']
        
        correct_value = component_to_value_map.get(component)
        
        if correct_value is not None:
            if current_granular_value == correct_value:
                return (f'SCS {container_name} OK', '')
            else:
                return (f'ERROR: {container_name}', correct_value)
        else:
            return (f'ERROR: {container_name}', 'Component Not Found in JSON')

    if not relevant_df.empty:
        results = relevant_df.apply(check_granular_accuracy_and_get_correct_value, axis=1)
        relevant_df[['Accuracy', 'Correct Value']] = pd.DataFrame(results.tolist(), index=relevant_df.index)
        df_g.update(relevant_df)
    
    return df_g
