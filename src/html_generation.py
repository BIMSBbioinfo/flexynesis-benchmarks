from datetime import datetime

def generate_html(ordered_stats):
    # Generate the HTML header
    html_content = generate_html_header()
    # Generate the Table of Contents and the sections based on the ordered stats
    toc, sections = generate_toc_and_sections(ordered_stats)
    # Append the Table of Contents to the HTML content
    html_content += toc
    # Append the body of the HTML document, which includes the sections
    html_content += generate_html_body(sections)
    # Append the HTML footer, including scripts for functionality
    html_content += generate_html_footer()
    return html_content

def generate_html_header():
    # Returns the HTML header, including the DOCTYPE declaration, meta tags, title, and links to external CSS
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Collate Results Make Summary Benchmark Figures</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/flatly/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.2.2/css/buttons.dataTables.min.css">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            scroll-behavior: smooth;
        }
        header {
            text-align: center;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }
        header p {
            margin: 5px 0;
            color: #6c757d;
        }
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100%;
            width: 250px;
            background-color: #343a40;
            color: #fff;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            padding-top: 20px;
            overflow-x: auto;
        }
        .sidebar .toc {
            padding: 20px;
        }
        .sidebar .toc h2 {
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: #fff;
        }
        .sidebar .toc ul {
            list-style-type: none;
            padding: 0;
        }
        .sidebar .toc li {
            margin: 5px 0;
            padding: 5px 0;
        }
        .sidebar .toc a {
            text-decoration: none;
            color: #adb5bd;
            padding: 5px;
            display: block;
            border-radius: 4px;
        }
        .sidebar .toc a:hover {
            text-decoration: none;
            background-color: #495057;
            color: #fff;
        }
        .sidebar .toc a.active {
            background-color: #495057;
            color: #fff;
        }
        .content {
            margin-left: 270px;
            padding: 20px;
        }
        .section {
            margin-top: 40px;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            font-size: 2rem;
            margin-top: 20px;
            font-weight: 300;
        }
        .section h3 {
            font-size: 1.75rem;
            margin-top: 20px;
            font-weight: 300;
        }
        table {
            width: 100%;
            margin-bottom: 20px;
        }
        table th, table td {
            text-align: center;
        }
        .table-responsive {
            overflow-x: auto;
        }
        table.dataTable {
            width: 100%;
            margin-bottom: 20px;
            border-collapse: collapse;
        }
        table.dataTable th, table.dataTable td {
            text-align: center;
            vertical-align: middle;
        }
        .dataTables_wrapper .dataTables_filter input {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px 10px;
            margin-left: 5px;
        }
        .dt-buttons .btn {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            margin: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .dt-buttons .btn:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        .dt-buttons .btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .dt-buttons .btn:focus {
            outline: none;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        .dt-button-collection {
            border-radius: 4px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .dt-button-collection .dt-button {
            display: block;
            width: 100%;
            padding: 8px 12px;
            text-align: left;
            border: none;
            background-color: #ffffff;
            color: #333;
            transition: background-color 0.3s ease;
        }
        .dt-button-collection .dt-button:hover {
            background-color: #f8f9fa;
        }
        .dt-button-collection .dt-button.active {
            background-color: #e9ecef;
            font-weight: bold;
        }
        .my-custom-padding {
            padding: 0 15px;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <nav class="toc">
            <h2>Table of Contents</h2>
            <ul>
"""

def generate_toc_and_sections(ordered_stats):
    # Initialize Table of Contents and sections strings
    toc = ""
    sections = ""
    # Loop through each dataset in the ordered stats
    for dataset, group_dict in ordered_stats.items():
        # Create an ID for each dataset to use in the HTML anchor
        dataset_id = dataset.replace(" ", "_")
        # Add dataset to the Table of Contents
        toc += f'<li><a href="#{dataset_id}">{dataset}</a></li>\n'
        # Start a new section for the dataset
        sections += f'<div id="{dataset_id}" class="section">\n<h2>{dataset}</h2>\n<div class="tabset">\n'
        # Loop through each group within the dataset
        for group, df in group_dict.items():
            # Create an ID for each group
            group_id = f"{dataset_id}_{group.replace(' ', '_')}"
            # Add group to the Table of Contents under its dataset
            toc += f'  <li><a href="#{group_id}"> - {group}</a></li>\n'
            # Start a new section for the group
            sections += f'<div id="{group_id}" class="section">\n<h3>{group}</h3>\n'
            # Add a table for the group's data
            sections += '<div class="table-responsive">\n'
            sections += df.to_html(index=False, classes="table table-striped table-bordered")
            sections += '</div>\n'
            sections += '</div>\n'
        sections += '</div>\n</div>\n'
    return toc, sections

def generate_html_body(sections):
    # Returns the main content of the HTML document, including the header and the main sections
    return f"""
            </ul>
        </nav>
    </div>
    <div class="content">
        <header>
            <h1>Collate Results Make Summary Benchmark Figures</h1>
            <p><em>Author: Bora Uyar</em></p>
            <p><em>Date: {datetime.now().strftime("%Y-%m-%d")}</em></p>
        </header>
        <main>
{sections}
        </main>
    </div>
"""

def generate_html_footer():
    # Returns the footer of the HTML document, including external JavaScript libraries and custom scripts
    return """
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.2.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.2.2/js/buttons.html5.min.js"></script>
    <script src="https://cdn.datatables.net/colvis/1.1.2/js/dataTables.colVis.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const sections = document.querySelectorAll('.section');
            const navLinks = document.querySelectorAll('.toc a');

            if (navLinks.length > 0) {
                navLinks[0].classList.add('active');
            }

            function onScroll() {
                let currentSection = '';

                sections.forEach((section) => {
                    const sectionTop = section.offsetTop;
                    const sectionHeight = section.clientHeight;
                    if (pageYOffset >= (sectionTop - 50)) {
                        currentSection = section.getAttribute('id');
                    }
                });

                navLinks.forEach((link) => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + currentSection) {
                        link.classList.add('active');
                    }
                });
            }

            window.addEventListener('scroll', onScroll);

            document.querySelectorAll('.toc a').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                    document.querySelectorAll('.toc a').forEach(a => a.classList.remove('active'));
                    this.classList.add('active');
                });
            });

            // Initialize DataTables with export buttons
            $('table').each(function() {
                $(this).DataTable({
                     dom: '<"row"<"col-sm-12 col-md-6"B><"col-sm-12 col-md-6"f>>rtip',
                   buttons: [
                        {
                            extend: 'csv',
                            className: 'dt-buttons'
                        }
                    ],  
                });
            });
        });
    </script>
</body>
</html>
"""