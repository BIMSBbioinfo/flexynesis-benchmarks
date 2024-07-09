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
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.2.2/css/buttons.dataTables.min.css">
    <style>
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
            }
            .content {
                margin-left: 0;
            }
        }
    </style>
</head>
<body class="bg-gray-100 font-sans text-gray-800">
    <div class="sidebar fixed top-0 left-0 h-full w-64 bg-gray-800 text-white shadow-lg overflow-y-auto transition-all duration-300 ease-in-out z-50" id="sidebar">
        <nav class="p-4">
            <h2 class="text-xl font-semibold mb-4">Table of Contents</h2>
            <ul class="space-y-2">
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
        toc += f'<li><a href="#{dataset_id}" class="block py-1 px-2 hover:bg-gray-700 rounded">{dataset}</a></li>\n'
        # Start a new section for the dataset
        sections += f'<div id="{dataset_id}" class="bg-white shadow-md rounded-lg p-4 md:p-6 mb-8">\n<h2 class="text-2xl font-light mb-4">{dataset}</h2>\n<div class="space-y-6">\n'
        # Loop through each group within the dataset
        for group, df in group_dict.items():
            # Create an ID for each group
            group_id = f"{dataset_id}_{group.replace(' ', '_')}"
            # Add group to the Table of Contents under its dataset
            toc += f'  <li><a href="#{group_id}" class="block py-1 px-2 hover:bg-gray-700 rounded ml-4"> - {group}</a></li>\n'
            # Start a new section for the group
            sections += f'<div id="{group_id}" class="bg-gray-50 rounded-lg p-4">\n<h3 class="text-xl font-light mb-4">{group}</h3>\n'
            # Add a table for the group's data
            sections += '<div class="overflow-x-auto">\n'
            sections += df.to_html(index=False, classes="min-w-full divide-y divide-gray-200")
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
    <div class="content ml-0 md:ml-64 p-4 md:p-8 transition-all duration-300 ease-in-out" id="content">
        <header class="bg-white shadow-md rounded-lg p-4 md:p-6 mb-8 text-center">
            <h1 class="text-2xl md:text-3xl font-light">Collate Results Make Summary Benchmark Figures</h1>
            <p class="text-gray-600 mt-2"><em>Author: Bora Uyar</em></p>
            <p class="text-gray-600"><em>Date: {datetime.now().strftime("%Y-%m-%d")}</em></p>
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
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            const sections = document.querySelectorAll('[id]');
            const navLinks = document.querySelectorAll('nav a');

            if (navLinks.length > 0) {
                navLinks[0].classList.add('bg-gray-700');
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
                    link.classList.remove('bg-gray-700');
                    if (link.getAttribute('href') === '#' + currentSection) {
                        link.classList.add('bg-gray-700');
                    }
                });
            }

            window.addEventListener('scroll', onScroll);

            document.querySelectorAll('nav a').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                    document.querySelectorAll('nav a').forEach(a => a.classList.remove('bg-gray-700'));
                    this.classList.add('bg-gray-700');
                    if (window.innerWidth < 768) {
                        sidebar.classList.add('-translate-x-full');
                        content.classList.remove('ml-64');
                    }
                });
            });

            $('table').each(function() {
                $(this).DataTable({
                    dom: '<"flex flex-col sm:flex-row justify-between items-center mb-4"<"flex-1 mb-2 sm:mb-0"B><"flex-1"f>>rtip',
                    buttons: [
                        {
                            extend: 'csv',
                            text: 'Download CSV',
                            className: 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'
                        }
                    ],
                    order: [],
                    responsive: true,
                    language: {
                        search: "_INPUT_",
                        searchPlaceholder: "Search...",
                    },
                    initComplete: function(settings, json) {
                        // Wrap the table in a responsive container
                        $(this).wrap('<div class="overflow-x-auto"></div>');
                    }
                });
            });
        });
    </script>
</body>
</html>
"""