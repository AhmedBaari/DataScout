import pandas as pd

def clean_column(df, column_name):
    """
    Clean the column elements to make it more suitable for search prompt placeholder.
    """
    # whitespaces (leading and trailing)
    df[column_name] = df[column_name].str.strip()
    
    # special characters
    df[column_name] = df[column_name].str.replace('[^\w\s]', '')
    
    # multiple spaces to single space
    df[column_name] = df[column_name].str.replace('\s+', ' ')
    
    return df