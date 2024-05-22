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

    def generate_pres_from_json(self, json_data, class_name, namespace_prefix, presentation_title="PresentationTitleExample", is_real_class=True):
        properties = [prop["Id"] for prop in json_data["value"] if prop["Id"] not in self.excluded_ids]
        form_layout_properties = [util.upper_to_lower_snake(prop) for prop in properties]
        
        presentation_fields = []
        lov_iid_dict = {"lov": [], "iid": []}
        for item in json_data["value"]:
            if item['Id'].upper() in self.excluded_ids:
                continue
            
            # Define LOV reference (only if LOV exist)
            lov_class_name = f"{self.generate_class_name(item.get('ReferenceTable', "null"), None)}Lov" if item.get("Lov", "false") == 'true' else "null"
            ref_controller = f"{lov_class_name}Controller::class" if (item.get("Lov", "false") == 'true') and (is_real_class) else "null"
            ref_service = f"{lov_class_name}Service::class" if (item.get("Lov", "false") == 'true') and (is_real_class) else "null"
            ref_pres = f"{lov_class_name}Pres::class" if (item.get("Lov", "false") == 'true') and (is_real_class) else "null"

            # Define IID reference (only if IID exist)
            iid_class_name = self.generate_class_name(item.get("Id", "null"), None) if (item.get("Iid", "false") == 'true') and (is_real_class) else "null"
            static_iid_enum = f"{iid_class_name}Enum::class" if (item.get("Iid", "false") == 'true') and (is_real_class) else "null"
            
            # Put LOV and IID list for Importing classes
            if lov_class_name != "null" and (item.get("Lov", "false") == 'true') and (is_real_class):
                lov_iid_dict["lov"].append(lov_class_name)
            if iid_class_name != "null" and (item.get("Iid", "false") == 'true') and (is_real_class):
                lov_iid_dict["iid"].append(iid_class_name)

            # Input Type Override for IID Dropdown
            field_input_type = f"FieldTypeEnum::{self.map_field_type(item.get('Type', 'STRING'))}"
            if (item.get("Iid", "false") == 'true') and (is_real_class):
                field_input_type = f"FieldTypeEnum::DROPDOWN"

            field = {
                "id": util.upper_to_lower_snake(item["Id"]),
                "label": item["Label"] if item["Label"] else item["Id"],
                "type": f"FieldTypeEnum::{self.map_field_type(item.get('Type', 'STRING'))}",
                "inputType": field_input_type,
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
                "lov": "true" if (item.get("Lov", "false") == 'true') and (is_real_class) else "false",
                "lovDetail": f'"{util.upper_to_lower_snake(item["Id"])}"' if (item.get("Lov", "false") == 'true') and (is_real_class) else "null",
                "referenceController": ref_controller,
                "referenceService": ref_service,
                "referencePres": ref_pres,
                "iid": "true" if (item.get("Iid", "false") == "true") and (is_real_class) else "false",
                "staticIidEnum": static_iid_enum,
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
            unpack_check_fields = unpack_check_fields,
            lov_iid_dict=lov_iid_dict
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

    def fetch_lov_iid(self, lov_info, iid_info, json_data):
        for item in json_data["value"]:
            if item["Lov"] == "true":
                lov_info.append({
                    "parentTable": item['TableName'],
                    "field": item["Id"],
                    "fieldLabel": item["Label"],
                    "referenceApiUrl": item.get("ReferenceApiUrl"),
                    "referenceFilter": item.get("ReferenceFilter"),
                    "referenceTable": item.get("ReferenceTable")
                })
            if item["Iid"] == "true":
                iid_info.append({
                    "parentTable": item['TableName'],
                    "field": item["Id"],
                    "fieldLabel": item["Label"],
                    "iidObjectClient": item.get("IidObjectClient"),
                    "iidObjectDb": item.get("IidObjectDb"),
                })
        return lov_info, iid_info
    
    def split_ifs_enum(self, ifs_enum_values):
        result_list = ifs_enum_values.rstrip('^').split('^')
        return result_list

    def generate_lov_classes(self, access_token, lov_info, base_dir):

        ensure_directory_exists(f"{base_dir}/lov/dto")
        ensure_directory_exists(f"{base_dir}/lov/service")
        ensure_directory_exists(f"{base_dir}/lov/controller")
        ensure_directory_exists(f"{base_dir}/lov/pres")
        lov_class_set = set()

        for lov in lov_info:
            parent_table = lov["parentTable"]
            package_suffix = "Lov"
            ref_table = lov["referenceTable"]
            ref_url = lov["referenceApiUrl"]
            class_name = f"{self.generate_class_name(ref_table, "")}Lov"
            # class_name = f"Lov{class_name}"
            lov_projection = ref_url.replace(f"{self.config["base_url"]}/", "")
            lov_pres_title = f"{util.pascal_to_string(self.generate_class_name(ref_table, ""))}"

            # Prepare the route builder
            route_lov_package = util.pascal_to_kebab(package_suffix).lower().strip()
            route_lov_class = util.pascal_to_kebab(class_name.strip())

            # Form the Menu Route pattern based on package_suffix and class_name
            menu_route = f"/{route_lov_package}/{route_lov_class}"

            # Placeholder for actual data fetching logic if needed
            try:
                # Getting metadata from projections
                response = get_meta_data(access_token, ref_table)
                json_data = response.json()
                if json_data is None:
                    logging.error(f"Failed to get data for LOV table: {ref_table} IN {parent_table}")
                    continue
                elif json_data['value'] == []:
                    logging.error(f"Empty data for LOV table: {ref_table} IN {parent_table}")
                    continue

                logging.info(f"Retrieved metadata for LOV table: {ref_table} IN {parent_table}")

            except Exception as e:
                logging.error(f"An error occurred while getting metadata for LOV table {ref_table} IN {parent_table}: {str(e)}")
                # Optionally, you may want to handle the error further, such as retrying the operation or logging additional information.
                continue

            # Generate DTO, Service, Controller, Presentation for LOV
            dto_content = self.generate_dto_from_json(json_data, class_name, package_suffix)
            service_content = self.generate_service_from_json(class_name, package_suffix, lov_projection)
            controller_content = self.generate_controller_from_json(class_name, package_suffix, menu_route)
            pres_content = self.generate_pres_from_json(json_data, class_name, package_suffix, lov_pres_title, is_real_class=False)

            # Write DTO, Service, Controller, Presentation Files for LOV
            with open(f"{base_dir}/lov/dto/{class_name}Dto.php", 'w') as file:
                file.write(dto_content)
            with open(f"{base_dir}/lov/service/{class_name}Service.php", 'w') as file:
                file.write(service_content)
            with open(f"{base_dir}/lov/controller/{class_name}Controller.php", 'w') as file:
                file.write(controller_content)            
            with open(f"{base_dir}/lov/pres/{class_name}Pres.php", 'w') as file:
                file.write(pres_content)
            # Log success
            logging.info(f"LOV class generated for {class_name}")

            # Append lov class name to a list
            lov_class_set.add(class_name)

            # END OF LOOP #
        
        # Register the LOV class route Separately
        for lov_name in lov_class_set:
            print("Unique class name:", lov_name)
            with open(f"{base_dir}/register_calls_lov.txt", 'a') as f:
                f.write(f"{lov_name}Controller::register();\n")
            # logging.info(f"Generated route registration for LOV class {lov_name}")

    def generate_iid_enum(self, iid_info, base_dir):

        ensure_directory_exists(f"{base_dir}/iid")

        for iid_item in iid_info:
            if iid_item:
                iid_class_name = self.generate_class_name(iid_item["field"], None)
                iid_db_value = [util.format_enum_case(item) for item in self.split_ifs_enum(iid_item["iidObjectDb"])]
                iid_client_value = self.split_ifs_enum(iid_item["iidObjectClient"])
                
                # Pairing DB and client values
                iid_pairs = list(zip(iid_db_value, iid_client_value))

                # Setup Jinja2 Enum Template
                template = self.env.get_template('enum_template.php')

                # Render the template with data
                enum_content = template.render(iid_class_name=iid_class_name, pairs=iid_pairs)

                # Write Enum Files for IID
                with open(f"{base_dir}/iid/{iid_class_name}Enum.php", 'w') as file:
                    file.write(enum_content)
                
                # Log success
                logging.info(f"IID Enum generated for {iid_class_name}")

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

        base_dir = self.config['base_dir']
        # Ensure the directory exists before saving files
        ensure_directory_exists(base_dir)
        ensure_directory_exists(f"{base_dir}/dto")
        ensure_directory_exists(f"{base_dir}/service")
        ensure_directory_exists(f"{base_dir}/controller")
        ensure_directory_exists(f"{base_dir}/pres")

        # Contain All Lov info
        lov_info_all = []
        iid_info_all = []

        # Check For Distinct table_name in Core/Main class  
        # (Only generate LOV class based on distinct table_name main class)
        dist_table_name = ()

        # For each configuration, consume the API, generate code, and save to files
        for index, row in df.iterrows():
            presentation_title = row['MENU NAME']
            table_name = row['TABLE NAME']
            addl_info = row['ADDL INFO']
            class_name = self.generate_class_name(table_name, addl_info) # Generate class name based on table name
            module_name = row['MODULE']
            submodule_name = row['SUBMODULE']
            package_suffix = f"{module_name}\\{submodule_name}"

            try:
                projection = row['SPECIFIC URL']
                if pd.isnull(projection):
                    projection = self.generate_ifs_projection(table_name)
            except KeyError:
                projection = self.generate_ifs_projection(table_name)
            

            # Prepare the route builder
            route_builder_package = util.pascal_to_kebab(package_suffix).lower().replace("\\", "/").strip()
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
                self.api_log_results(table_name, response, summary, api_results_list)
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

            # Register the class route
            with open(f"{base_dir}/register_calls.txt", 'a') as f:
                f.write(f"{class_name}Controller::register();\n")
            logging.info(f"Generated route registration for {class_name}")

            # Inside the loop after generating code for each class
            with open(f"{base_dir}/navigator_registration.txt", 'a') as f:
                f.write(f"$ExampleNavigatorDto->addSubMenu(\n")
                f.write(f"\t$this->addNavigator(\"{route_builder_class}\", \"{presentation_title}\", $ExampleNavigatorDto->getRoute() . \"/{route_builder_class}\", null)\n")
                f.write(f");\n")
            logging.info(f"Generated Navigator for {class_name}")

            # Generated LOV Separately
            lov_info = []
            iid_info = []
            lov_info, iid_info = self.fetch_lov_iid(lov_info, iid_info, json_data)

            # Store LOV and IID if exist
            if lov_info:
                lov_info_all.extend(lov_info)
            if iid_info:
                iid_info_all.extend(iid_info)
                
            # END OF LOOP #

        # Generate LOV and IID separately if exist
        if lov_info_all:
            self.generate_lov_classes(access_token, lov_info_all, base_dir)
        if iid_info_all:
            self.generate_iid_enum(iid_info_all, base_dir)
        
        # Code Generator Reporting
        results_df = pd.DataFrame(api_results_list)  # Convert the list of dictionaries to a DataFrame

        # Adding summary at the end of DataFrame
        summary_df = pd.DataFrame([{"Table Name": "Summary", "Status": f"Passed: {summary['Passed']}, Failed: {summary['Failed']}"}])
        results_df = pd.concat([results_df, summary_df], ignore_index=True)
        
        # Writing results to an Excel file
        results_df.to_excel(f"{base_dir}/generator_report.xlsx", index=False)

        
