import os
import pandas as pd
import re
from consumable_api import authenticate_and_get_token, get_meta_data
from code_generator import generate_dto_from_json, generate_controller_from_json, generate_service_from_json, generate_pres_from_json

# Assuming authenticate_and_get_token and get_data functions are defined as previously provided

def pascal_to_kebab(s):
    """Convert a PascalCase string to kebab-case."""
    return '-'.join(re.sub('([a-z0-9])([A-Z])', r'\1-\2', s).lower().split())

def ensure_directory_exists(directory_path):
    """Ensure the directory exists. If not, create it."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def generate_code_for_configuration(excel_path):
    # Authenticate and get token
    access_token = authenticate_and_get_token()
    if not access_token:
        print("Failed to authenticate")
        return

    # Read the Excel file for configurations
    df = pd.read_excel(excel_path)
    
    # For each configuration, consume the API, generate code, and save to files
    for index, row in df.iterrows():
        presentation_title = row['MENU NAME']
        table_name = row['TABLE NAME']
        class_name = row['CLASS NAME']
        package_suffix = row['PACKAGE SUFFIX']
        # presentation_title = f"{class_name} Presentation"  # Example presentation title

        # Consume API to get JSON data
        json_data = get_meta_data(access_token, table_name)
        if json_data is None:
            print(f"Failed to get data for table: {table_name}")
            continue

        # Generate code for DTO, Pres, Service, and Controller based on JSON data
        # Assume generate_dto_from_json, generate_service_from_json, generate_controller_from_json, generate_pres_from_json functions are defined
        dto_class_content = generate_dto_from_json(json_data, class_name, package_suffix)
        service_class_content = generate_service_from_json(class_name, package_suffix)
        controller_class_content = generate_controller_from_json(class_name, package_suffix)
        pres_class_content = generate_pres_from_json(json_data, class_name, package_suffix, presentation_title)

        # Define the base directory to save the files (adjust as needed)
        base_dir = "/generated_code"

        # Ensure the directory exists before saving files
        ensure_directory_exists(base_dir)

        # Save the generated code to files
        with open(f"{base_dir}/{class_name}Dto.php", "w") as file:
            file.write(dto_class_content)
        with open(f"{base_dir}/{class_name}Service.php", "w") as file:
            file.write(service_class_content)
        with open(f"{base_dir}/{class_name}Controller.php", "w") as file:
            file.write(controller_class_content)
        with open(f"{base_dir}/{class_name}Pres.php", "w") as file:
            file.write(pres_class_content)

        print(f"Code generated for {class_name}")

# Specify the path to your Excel file
excel_path = 'Template Mapping Menu AAL.xlsx'

generate_code_for_configuration(excel_path)
