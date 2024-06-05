import pandas as pd
import json

def process_data(json_path, container_name, container_df, df):
    

    # Open the JSON file and load the data into a dictionary.
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    # Convert the list of containers into a DataFrame.
    container_data = pd.DataFrame(json_data[container_name])

    # Create an empty dictionary
    container_accuracy_dict = {}

    # Iterate over each container in the JSON data.
    for container in container_data.itertuples(index=False):
        # Create a mask using exact string matching.
        maskContainer = (container_df['PhwebDescription'] == container.PhwebDescription) & \
                        (container_df['ContainerValue'] == container.ContainerValue)
        # Update the 'container_accuracy_dict' dictionary using boolean indexing.
        container_accuracy_dict.update(container_df[maskContainer].index.to_series().map(lambda idx: (idx, f'SCS {container_name} OK')))
    # Update the 'Accuracy' column of the 'container_df' DataFrame using boolean indexing.
    container_df.loc[container_accuracy_dict.keys(), 'Accuracy'] = [value for _, value in container_accuracy_dict.values()]
    # Update the 'Accuracy' column of the 'df' DataFrame using boolean indexing.
    df.loc[container_df.index, 'Accuracy'] = container_df['Accuracy']

    # Find the unmatched containers and set error messages
    unmatched_containers = container_df[~container_df.index.isin(container_accuracy_dict.keys())]
    unmatched_error_messages = [f'ERROR: {container_name}' for _ in range(len(unmatched_containers))]
    unmatched_containers['Accuracy'] = unmatched_error_messages
    # Update the 'Accuracy' column of the 'df' DataFrame for unmatched containers.
    df.loc[unmatched_containers.index, 'Accuracy'] = unmatched_containers['Accuracy']

    unmatched_container_values = []
    for container in unmatched_containers.itertuples(index=False):
        matching_containers = container_data[container_data['PhwebDescription'] == container.PhwebDescription]
        if len(matching_containers) > 0:
            correct_value = matching_containers.iloc[0]['ContainerValue']
            unmatched_container_values.append(correct_value)
        else:
            unmatched_container_values.append('N/A')
    # Add 'Correct Value' column to the df DataFrame for unmatched containers
    df.loc[unmatched_containers.index, 'Correct Value'] = unmatched_container_values

    return df