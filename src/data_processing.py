import os
import pandas as pd

# Function to read all non-baseline .stats.csv files from a directory and combine them into a single DataFrame
def read_files(workdir):
    # Generate a list of file paths for all .stats.csv files that are not baseline stats
    files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(workdir) for f in filenames if f.endswith('stats.csv') and 'baseline' not in f]
    stats_list = []

    # Read each file, add a 'prefix' column derived from the file name, and append to stats_list
    for file in files:
        dt = pd.read_csv(file)
        dt['prefix'] = os.path.basename(file).replace('.stats.csv', '')  # Extract prefix from file name
        stats_list.append(dt)

    # Combine all DataFrames in stats_list into a single DataFrame
    stats = pd.concat(stats_list, ignore_index=True)
    return stats

# Function to combine the stats DataFrame with an analysis table and include baseline stats
def combine_with_analysis_table(stats, workdir):
    # Read the analysis table, excluding its first column
    analysis_table = pd.read_csv(os.path.join(workdir, 'analysis_table.csv')).iloc[:, 1:]
    # Merge the stats DataFrame with the analysis table on the 'prefix' column
    stats = stats.merge(analysis_table, on='prefix')

    # Find all baseline stats files
    baseline_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(workdir) for f in filenames if f.endswith('baseline.stats.csv')]

    # If there are any baseline files, process them similarly to the stats files
    if baseline_files:
        baseline_stats_list = []
        for file in baseline_files:
            dt = pd.read_csv(file)
            dt['prefix'] = os.path.basename(file).replace('.baseline.stats.csv', '')  # Extract prefix from file name
            baseline_stats_list.append(dt)

        # Combine all baseline stats into a single DataFrame
        baseline_stats = pd.concat(baseline_stats_list, ignore_index=True)
        # Rename the first column to 'tool'
        baseline_stats.rename(columns={baseline_stats.columns[0]: 'tool'}, inplace=True)

        # Merge baseline stats with selected columns from the analysis table
        baseline_stats = baseline_stats.merge(analysis_table[['prefix', 'task', 'target', 'batch', 'data_types', 'features_min', 'feature_perc', 'log_transform']], on='prefix')

        # Combine the stats and baseline_stats DataFrames
        stats = pd.DataFrame(combine_dfs([stats, baseline_stats]))

    return stats

# Function to combine multiple DataFrames into one, ensuring all columns are included
def combine_dfs(df_list):
    # Create a list of all unique column names across all DataFrames
    cn = list(set().union(*(df.columns for df in df_list)))
    # Concatenate all DataFrames, reindexing columns to include all unique column names
    combined_df = pd.concat([df.reindex(columns=cn) for df in df_list])
    return combined_df