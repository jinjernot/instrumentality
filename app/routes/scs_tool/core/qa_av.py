def av_check(df):
    # Check for duplicate combinations
    duplicate_mask = df.duplicated(subset=['SKU', 'ComponentGroup', 'ContainerName'], keep=False)
    
    # Update 'Additional Information'
    df.loc[(duplicate_mask) & (~df['ComponentGroup'].isin(['Environment', 'Optical Drive'])), 'Additional Information'] = 'Duplicated AV'
    return df