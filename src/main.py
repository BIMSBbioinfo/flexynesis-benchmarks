import os
import sys  
from data_processing import read_files, combine_with_analysis_table
from stats_processing import split_stats, order_stats
from html_generation import generate_html

# Define the main function to generate an HTML report from stats files
def main(outdir, output_file_path):
    # Read and process the stats files from the specified directory
    stats = read_files(outdir)
    # Combine the processed stats with an analysis table
    stats = combine_with_analysis_table(stats, outdir)
    # Split the combined stats by task
    stats_by_task = split_stats(stats)
    # Order the stats within each task
    ordered_stats = order_stats(stats_by_task)
    # Generate HTML content from the ordered stats
    html_content = generate_html(ordered_stats)

    # Write the HTML content to the specified output file
    with open(output_file_path, "w") as f:
        f.write(html_content)

    # Print a message indicating the report has been generated
    print(f"HTML report generated: {output_file_path}")

# Check if the script is run directly (not imported) and execute the main function
if __name__ == "__main__":
    # Ensure the correct number of command-line arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python main.py <OUTDIR> <OUTPUT_FILE_PATH>")
        sys.exit(1)  # Exit with an error code if the arguments are incorrect
    # Call the main function with the provided arguments
    main(sys.argv[1], sys.argv[2])