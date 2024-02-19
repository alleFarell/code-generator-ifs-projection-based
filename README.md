# PHP Code Generator for Laravel

This PHP Code Generator automates the creation of DTO, Service, Controller, and Pres classes for Laravel applications based on metadata defined in Excel sheets and fetched dynamically from a specified API. The tool aims to streamline the development process, reduce repetitive coding tasks, and ensure consistency across different parts of the application.

## Features
- Dynamic Class Generation: Automatically generates PHP classes based on JSON metadata.
- Excel Configuration: Utilizes Excel files for easy management of class configurations.
- API Integration: Fetches metadata from a REST API with support for bearer token authentication.
- Customizable Templates: Uses Jinja2 templates for flexible code output customization.

## Prerequisites
Before you begin, ensure you have the following installed on your system:
- Python 3.6 or higher
- Pip (Python package installer)

## Installation
Install the required Python libraries using pip:
```
pip install pandas requests jinja2 openpyxl
```

## Configuration
1. API Credentials: Set up your API credentials (client ID, client secret, username, password) within the authentication function in the script.
2. Excel Template: Prepare an Excel template with columns for menu names, table names, class names, and package suffixes. Ensure this file follows the format used in the script.

## Usage
To use the code generator:
1. Set up your Excel configuration file with the necessary details for the classes you want to generate.
2. Run the authentication script to obtain an access token for the API.
3. Execute the main script, specifying the path to your Excel configuration file. The script will read configurations, fetch metadata for each table, and generate the corresponding PHP classes.
```
python main.py
```

## Contributing
Contributions to this project are welcome! If you have suggestions for improvements, bug fixes, or new features, feel free to fork the repository, make your changes, and submit a pull request. For major changes or discussions, please open an issue first to discuss what you would like to change.

## License
This project is open-sourced under the MIT License. See the LICENSE file for more details.

## Contact
For questions or support, please open an issue in the GitHub repository.
