import os
import time
import pandas as pd
import re
import logging
from consumable_api import authenticate_and_get_token, get_meta_data
from code_generator import generate_dto_from_json, generate_controller_from_json, generate_service_from_json, generate_pres_from_json

# Setup logging
logging.basicConfig(filename='code_generation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def pascal_to_kebab(s):
    """Convert a PascalCase string to kebab-case."""
    return '-'.join(re.sub('([a-z0-9])([A-Z])', r'\1-\2', s).lower().split())

def ensure_directory_exists(directory_path):
    """Ensure the directory exists. If not, create it."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging.info(f"Created directory: {directory_path}")

def generate_code_for_configuration(excel_path):
    # Authenticate and get token
    access_token = authenticate_and_get_token()
    if not access_token:
        logging.error("Failed to authenticate")
        return

    logging.info("Successfully authenticated")

    # Read the Excel file for configurations
    df = pd.read_excel(excel_path)
    
    # For each configuration, consume the API, generate code, and save to files
    for index, row in df.iterrows():
        presentation_title = row['MENU NAME']
        table_name = row['TABLE NAME']
        class_name = row['CLASS NAME']
        package_suffix = row['PACKAGE SUFFIX']
        projection = row['IFS PROJECTION']

        # Prepare the route builder
        route_builder_package = package_suffix.lower().replace("\\", "/").strip()
        route_builder_class = pascal_to_kebab(class_name.strip())

        # Form the Menu Route pattern based on package_suffix and class_name
        menu_route = f"/{route_builder_package}/{route_builder_class}"

        json_data = get_meta_data(access_token, table_name)
        if json_data is None:
            logging.error(f"Failed to get data for table: {table_name}")
            continue

        logging.info(f"Retrieved metadata for {table_name}")

        # Generate code for DTO, Pres, Service, and Controller based on JSON data
        dto_class_content = generate_dto_from_json(json_data, class_name, package_suffix)
        service_class_content = generate_service_from_json(class_name, package_suffix, projection)
        controller_class_content = generate_controller_from_json(class_name, package_suffix, menu_route)
        pres_class_content = generate_pres_from_json(json_data, class_name, package_suffix, presentation_title)

        # Define the base directory to save the files
        base_dir = "../generated_code"

        # Ensure the directory exists before saving files
        ensure_directory_exists(base_dir)
        ensure_directory_exists(f"{base_dir}/dto")
        ensure_directory_exists(f"{base_dir}/service")
        ensure_directory_exists(f"{base_dir}/controller")
        ensure_directory_exists(f"{base_dir}/pres")

        # Save the generated code to files
        with open(f"{base_dir}/dto/{class_name}Dto.php", "w") as file:
            file.write(dto_class_content)
        with open(f"{base_dir}/service/{class_name}Service.php", "w") as file:
            file.write(service_class_content)
        with open(f"{base_dir}/controller/{class_name}Controller.php", "w") as file:
            file.write(controller_class_content)
        with open(f"{base_dir}/pres/{class_name}Pres.php", "w") as file:
            file.write(pres_class_content)

        logging.info(f"Code generated for {class_name}")

# Specify the path to your Excel file
excel_path = 'Template Mapping Menu AAL.xlsx'

# Start timing counter
start_time = time.time()

# Run The Code Generator
generate_code_for_configuration(excel_path)

# End timing and log the execution time
end_time = time.time()
execution_time = end_time - start_time
logging.info(f"Code generation completed in {execution_time} seconds.")
print(f"Code generation completed in {execution_time} seconds.")

