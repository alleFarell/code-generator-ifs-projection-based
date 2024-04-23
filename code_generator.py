import json
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import utilities as util
import logging
from consume_api import authenticate_and_get_token, get_meta_data
from file_operations import ensure_directory_exists

class CodeGenerator:
    def __init__(self, config):
        self.config = config
        self.excluded_ids = ["OBJKEY", "OBJID", "OBJVERSION", "AnotherIdToExclude"]
        # Initialize the Jinja2 environment with loop controls extension
        self.env = Environment(loader=FileSystemLoader('jinja-templates'), extensions=['jinja2.ext.loopcontrols'])
        # If you have custom filters like camel_to_pascal, make sure they are added here
        self.env.filters['pascal_case'] = util.camel_to_pascal

    def default_value_for_type(self, type_name):
        """Returns default value based on type."""
        defaults = {
            "string": "null",
            "int": "0",
            "bool": "false",
        }
        return defaults.get(type_name, "null")

    def map_type(self, json_type):
        """Maps JSON field types to PHP types, safely handling None values."""
        if json_type is None:
            return ""
        type_mapping = {
            "STRING": "string",
            "NUMBER": "int",
            "BOOLEAN": "bool",
        }
        return type_mapping.get(json_type.upper(), "").lower()

    def map_field_type(self, json_type):
        type_mapping = {
            "STRING": "STRING",
            "NUMBER": "NUMBER",
            "BOOLEAN": "CHECKBOX",
            "DATE/DATE": "DATE",
            "DATE/DATETIME": "DATETIME",
        }
        return type_mapping.get(json_type, "STRING")

    def generate_dto_from_json(self, json_data, class_name, namespace_prefix):
        properties = [{
            'name': util.snake_to_camel(prop["Id"]),
            'type': self.map_type(prop["Type"]),
            'default': self.default_value_for_type(self.map_type(prop["Type"]))
        } for prop in json_data["value"] if prop["Id"] not in self.excluded_ids]

        template = self.env.get_template('dto_template.php')
        dto_class = template.render(
            class_name=class_name,
            namespace_prefix=namespace_prefix,
            properties=properties
        )
        return dto_class

    def generate_service_from_json(self, class_name, namespace_prefix, projection):
        template = self.env.get_template('service_template.php')
        service_class = template.render(
            class_name=class_name,
            namespace_prefix=namespace_prefix,
            projection=projection
        )
        return service_class

    def generate_controller_from_json(self, class_name, namespace_prefix, menu_route):
        template = self.env.get_template('controller_template.php')
        controller_class = template.render(
            class_name=class_name,
            namespace_prefix=namespace_prefix,
            menu_route=menu_route
        )
        return controller_class

    def generate_pres_from_json(self, json_data, class_name, namespace_prefix, presentation_title="PresentationTitleExample"):
        properties = [prop["Id"] for prop in json_data["value"] if prop["Id"] not in self.excluded_ids]
        form_layout_properties = [util.upper_to_lower_snake(prop) for prop in properties]
        
        presentation_fields = []
        for item in json_data["value"]:
            if item['Id'].upper() in self.excluded_ids:
                continue
            field = {
                "id": util.upper_to_lower_snake(item["Id"]),
                "label": item["Label"] if item["Label"] else item["Id"],
                "type": f"FieldTypeEnum::{self.map_field_type(item.get('Type', 'STRING'))}",
                "inputType": f"FieldTypeEnum::{self.map_field_type(item.get('Type', 'STRING'))}",
                "length": item["Length"] if item.get("Type") == "STRING" and item.get("Length") else 100,
                "primaryKey": "true" if item.get("PrimaryKey", "false") == "true" else "false",
                "mandatory": "true" if item.get("Mandatory", "false") == "true" else "false",
                "insertable": "true" if item.get("Insertable", "false") == "true" else "false",
                "updateable": "true" if item.get("Updateable", "false") == "true" else "false",
                "presentation": "true",
                "hidden": "false",
                "visible": "true",
                "detail": "true" if item.get("PrimaryKey", "false") == "true" else "false",
                "onchange": "false",
                "onchangeLookup": "null",
                "lov": "false",
                "lovDetail": "null",
                "referenceController": "null",
                "referenceService": "null",
                "referencePres": "null",
                "iid": "false",
                "staticIidEnum": "null",
                "uploader": "false",
                "downloader": "false",
                "thousandSeparator": "false",
                "decimalPrecision": 2,
                "internalZoomContent": "null",
                "externalZoomContent": "null",
            }  # The field dictionary setup goes here.
            presentation_fields.append(field)

        # UnpackCheck Filter
        unpack_check_fields = [{
            "id": field["id"],
            "insertable": "true" if field.get("insertable", "false") == "true" else "false",
            "updateable": "true" if field.get("updateable", "false") == "true" else "false"
        } for field in presentation_fields if field.get("insertable", "false") == "true" or field.get("updateable", "false") == "true"]

        template = self.env.get_template('pres_template.php')
        pres_class = template.render(
            class_name=class_name,
            namespace_prefix=namespace_prefix,
            presentation_title=presentation_title,
            presentation_fields=presentation_fields,
            form_layout_groups=[form_layout_properties[i:i+4] for i in range(0, len(form_layout_properties), 4)],
            unpack_check_fields = unpack_check_fields
        )
        return pres_class
    
    def generate_class_name(self, value, addl_info):
        # Remove prefix "CTM_" if present
        if value.startswith("CTM_"):
            value = value[len("CTM_"):]

        # Split the string by underscores and capitalize each word
        words = value.split('_')
        capitalized_words = [word.capitalize() for word in words]

        # Join the words together without underscores
        pascal_class_name = ''.join(capitalized_words)

        if not(pd.isna(addl_info)):
            pascal_addl_info = util.string_to_pascal(addl_info)
            pascal_class_name = f"{pascal_class_name}{pascal_addl_info}"

        # return class name in pascal
        return pascal_class_name

    def generate_ifs_projection(self, table_name_str):
        """Generate an IFS Projection from table_name."""
        pascal_str = util.snake_to_pascal(table_name_str)
        return f"{pascal_str}Handling.svc/{pascal_str}Set"
    
    def api_log_results(self, table_name, response, summary, results_list):
        try:
            if response.status_code == 200: 
                data = response.json()
                if data["value"]:
                    results_list.append({"Table Name": table_name, "Status": "Passed"})
                    summary["Passed"] += 1
                else:
                    results_list.append({"Table Name": table_name, "Status": "Failed - EMPTY RESPONSE"})
                    summary["Failed"] += 1
            else:
                results_list.append({"Table Name": table_name, "Status": f"Failed - Status Code: {response.status_code}"})
                summary["Failed"] += 1
        except Exception as e:
            results_list.append({"Table Name": table_name, "Status": "Failed - PROJECTION ERROR"})
            summary["Failed"] += 1
    
    def generate(self):
        # Authenticate and get token
        access_token = authenticate_and_get_token()
        if not access_token:
            logging.error("Failed to authenticate")
            return

        logging.info("Successfully authenticated")

        df = pd.read_excel(self.config['excel_path'])
        classes_name = []
        api_results_list = []
        summary = {"Passed": 0, "Failed": 0}

        # For each configuration, consume the API, generate code, and save to files
        for index, row in df.iterrows():
            presentation_title = row['MENU NAME']
            table_name = row['TABLE NAME']
            addl_info = row['ADDL INFO']
            class_name = self.generate_class_name(table_name, addl_info) # Generate class name based on table name
            module_name = row['MODULE']
            submodule_name = row['SUBMODULE']
            package_suffix = f"{module_name}\\{submodule_name}"
            projection = self.generate_ifs_projection(table_name)
            

            # Prepare the route builder
            route_builder_package = package_suffix.lower().replace("\\", "/").strip()
            route_builder_class = util.pascal_to_kebab(class_name.strip())

            # Form the Menu Route pattern based on package_suffix and class_name
            menu_route = f"/{route_builder_package}/{route_builder_class}"
            
            try:
                # Getting metadata from projections
                response = get_meta_data(access_token, table_name)
                json_data = response.json()
                self.api_log_results(table_name, response, summary, api_results_list)
                if json_data is None:
                    logging.error(f"Failed to get data for table: {table_name}")
                    continue
                elif json_data['value'] == []:
                    logging.error(f"Empty data for table: {table_name}")
                    continue

                logging.info(f"Retrieved metadata for {table_name}")

            except Exception as e:
                logging.error(f"An error occurred while getting metadata for table {table_name}: {str(e)}")
                # Optionally, you may want to handle the error further, such as retrying the operation or logging additional information.
                # Depending on the situation, you might also want to continue the loop or raise the exception.
                continue
            
            # Append classes name that are not empty
            classes_name.append(class_name)

            # Generate code for DTO, Pres, Service, and Controller based on JSON data
            dto_class_content = self.generate_dto_from_json(json_data, class_name, package_suffix)
            service_class_content = self.generate_service_from_json(class_name, package_suffix, projection)
            controller_class_content = self.generate_controller_from_json(class_name, package_suffix, menu_route)
            pres_class_content = self.generate_pres_from_json(json_data, class_name, package_suffix, presentation_title)

            base_dir = self.config['base_dir']
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

            # Register the class immediately
            with open(f"{base_dir}/register_calls.txt", 'a') as f:
                f.write(f"{class_name}Controller::register();\n")


            # Inside the loop after generating code for each class
            with open(f"{base_dir}/navigator_registration.txt", 'a') as f:
                f.write(f"$ExampleNavigatorDto->addSubMenu(\n")
                f.write(f"\t$this->addNavigator(\"{route_builder_class}\", \"{presentation_title}\", $ExampleNavigatorDto->getRoute() . \"/{route_builder_class}\", null)\n")
                f.write(f");\n")


            # END OF LOOP #
        
        # Code Generator Reporting
        results_df = pd.DataFrame(api_results_list)  # Convert the list of dictionaries to a DataFrame

        # Adding summary at the end of DataFrame
        summary_df = pd.DataFrame([{"Table Name": "Summary", "Status": f"Passed: {summary['Passed']}, Failed: {summary['Failed']}"}])
        results_df = pd.concat([results_df, summary_df], ignore_index=True)
        
        # Writing results to an Excel file
        results_df.to_excel(f"{base_dir}/generator_report.xlsx", index=False)

        # # Separately Generate Route Registration
        # with open(f"{base_dir}/register_calls.txt", 'w') as f:
        #     for class_name in classes_name:
        #         f.write(f"{class_name}Controller::register();\n")

        # logging.info(f"Code generated for route registration")
        
