def split_stats(stats):
    """
    Splits the stats DataFrame into a nested dictionary grouped first by 'task' and then by 'var'.
    
    Parameters:
    - stats: DataFrame containing the statistics data.
    
    Returns:
    - A dictionary with tasks as keys, each containing a dictionary of variables as keys and their corresponding DataFrames as values.
    """
    # Group the stats DataFrame by 'task' and create a dictionary
    stats_by_task = {task: df for task, df in stats.groupby('task')}
    
    # For each task, further group the DataFrame by 'var' and update the dictionary
    for task in stats_by_task:
        stats_by_task[task] = {var: df for var, df in stats_by_task[task].groupby('var')}
    
    return stats_by_task

def order_stats(stats_by_task):
    """
    Orders the statistics within each task and variable based on specific metrics.
    
    Parameters:
    - stats_by_task: A dictionary with tasks as keys, each containing a dictionary of variables as keys and their corresponding DataFrames as values.
    
    Returns:
    - A dictionary structured like stats_by_task but with DataFrames ordered by specific metrics.
    """
    ordered_stats = {}
    # Iterate through each task and its variables
    for task, var_dict in stats_by_task.items():
        ordered_stats[task] = {}
        for var, df in var_dict.items():
            # Order the DataFrame based on the presence of specific metrics
            if 'pearson_corr' in df['metric'].values:
                ordered_stats[task][var] = dcast_and_order(df, 'pearson_corr')
            elif 'kappa' in df['metric'].values:
                ordered_stats[task][var] = dcast_and_order(df, 'kappa')
            elif 'cindex' in df['metric'].values:
                ordered_stats[task][var] = dcast_and_order(df, 'cindex')
    return ordered_stats

def dcast_and_order(df, metric):
    """
    Pivots and orders a DataFrame based on a specified metric.
    
    Parameters:
    - df: DataFrame to be pivoted and ordered.
    - metric: The metric name to sort the DataFrame by.
    
    Returns:
    - A pivoted and ordered DataFrame.
    """
    # Pivot the DataFrame to have metrics as columns
    df_pivot = df.pivot(index=['prefix', 'target', 'batch', 'event', 'time', 'tool', 'gnn_conv', 'fusion', 'data_types', 'finetuning_samples'], columns='metric', values='value').reset_index()
    
    # If the specified metric is present, sort the DataFrame by it
    if metric in df_pivot.columns:
        df_pivot = df_pivot.sort_values(by=metric, ascending=False)
    
    # Remove the column name hierarchy
    df_pivot.columns.name = None
    
    return df_pivot