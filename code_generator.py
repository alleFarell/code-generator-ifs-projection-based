import json
from jinja2 import Environment, FileSystemLoader
import re

# Define List of Ids to be Excluded
excluded_ids = ["OBJKEY", "OBJID", "OBJVERSION", "AnotherIdToExclude"]

def camel_case(s):
    """Converts strings to camelCase."""
    parts = s.split('_')
    return parts[0].lower() + ''.join(part.title() for part in parts[1:])

def pascal_case(s):
    """Converts camelCase strings to PascalCase."""
    return s[0].upper() + s[1:] if s else s

def camel_case_to_snake_case(s):
    """Converts strings to snake_case."""
    return '_'.join(re.findall('[A-Z][^A-Z]*', s)).lower()

def snake_case(s):
    """Converts strings from UPPER_CASE to snake_case."""
    # If the string is already in UPPER_CASE, just convert it to lower case
    return s.lower()

def default_value_for_type(type_name):
    """Returns default value based on type."""
    defaults = {
        "string": "null",
        "int": "0",
        "bool": "false",
    }
    return defaults.get(type_name, "null")

def map_type(json_type):
    """Maps JSON field types to PHP types, safely handling None values."""
    if json_type is None:
        # Default to string or any other type as needed
        return ""
    
    # Proceed with mapping if json_type is not None
    type_mapping = {
        "STRING": "string",
        "NUMBER": "int",
        "BOOLEAN": "bool",
        # Add more mappings as needed
    }
    return type_mapping.get(json_type.upper(), "").lower()

def map_field_type(json_type):
    type_mapping = {
        "STRING": "STRING",
        "NUMBER": "NUMBER",
        "BOOLEAN": "CHECKBOX",
        "DATE/DATE": "DATE",
        "DATE/DATETIME": "DATETIME",
    }
    # Default to STRING if not found
    return type_mapping.get(json_type, "STRING")

def generate_dto_from_json(json_data, class_name, namespace_prefix):
    """Generates a PHP DTO class from JSON data."""
    data = json_data
    properties = [{
        'name': camel_case(prop["Id"]),
        'type': map_type(prop["Type"]),
        'default': default_value_for_type(map_type(prop["Type"]))
    } for prop in data["value"] if prop["Id"] not in excluded_ids] # Skip this prop if its ID is in the list of excluded IDs

    # Set up Jinja2 environment with the templates directory
    env = Environment(loader=FileSystemLoader('jinja-templates'))
    env.filters['pascal_case'] = pascal_case  # Assuming this filter is defined elsewhere

    # Load the DTO template from the file
    template = env.get_template('dto_template.php')

    # Render the template with context data
    dto_class = template.render(
        class_name=class_name,
        namespace_prefix=namespace_prefix,
        properties=properties
    )

    return dto_class

def generate_service_from_json(class_name, namespace_prefix, projection):
    """Generates a PHP Service class."""
    # Set up Jinja2 environment with the templates directory
    env = Environment(loader=FileSystemLoader('jinja-templates'))

    # Load the SERVICE template from the file
    template = env.get_template('service_template.php')

    # Render the template with context data
    service_class = template.render(
        class_name=class_name,
        namespace_prefix=namespace_prefix,
        projection=projection
    )

    return service_class

def generate_controller_from_json(class_name, namespace_prefix, menu_route):
    """Generates a PHP Controller class."""
    # Set up Jinja2 environment with the templates directory
    env = Environment(loader=FileSystemLoader('jinja-templates'))

    # Load the SERVICE template from the file
    template = env.get_template('controller_template.php')

    # Render the template with context data
    controller_class = template.render(
        class_name=class_name,
        namespace_prefix=namespace_prefix,
        menu_route=menu_route
    )

    return controller_class

def generate_pres_from_json(json_data, class_name, namespace_prefix, presentation_title="PresentationTitleExample"):
    """Generates a PHP Pres class."""
    data = json_data
    properties = [prop["Id"] for prop in data["value"]]

    # Convert property names to lower snake case for dynamic form layout
    form_layout_properties = [snake_case(prop) for prop in properties]
    
    # Process each JSON object into the format required by initPresentationFieldContent
    presentation_fields = []
    for item in data["value"]:

        if item['Id'].upper() in excluded_ids:
          continue  # Skip this item if its ID is in the list of excluded IDs
        
        field = {
            "id": snake_case(item["Id"]),
            "label": item["Label"] if item["Label"] else item["Id"],
            "type": f"FieldTypeEnum::{map_field_type(item.get('Type', 'STRING'))}",
            "inputType": f"FieldTypeEnum::{map_field_type(item.get('Type', 'STRING'))}",
            "length": item["Length"] if item.get("Type") == "STRING" and item.get("Length") else 100,
            "primaryKey": "true" if item.get("PrimaryKey", "false") == "true" else "false",
            "mandatory": "true" if item.get("Mandatory", "false") == "true" else "false",
            "insertable": "true" if item.get("Insertable", "false") == "true" else "false",
            "updateable": "true" if item.get("Updateable", "false") == "true" else "false",
            "presentation": "true",
            "hidden": "false",
            "visible": "true",
            "detail": "true",
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
        }
        presentation_fields.append(field)

    # UnpackCheck Filter
    unpack_check_fields = [{
        "id": field["id"],
        "insertable": "true" if field.get("insertable", "false") == "true" else "false",
        "updateable": "true" if field.get("updateable", "false") == "true" else "false"
    } for field in presentation_fields if field.get("insertable", "false") == "true" or field.get("updateable", "false") == "true"]

    # Set up Jinja2 environment with the templates directory
    env = Environment(loader=FileSystemLoader('jinja-templates'), extensions=['jinja2.ext.loopcontrols'])

    # Load the SERVICE template from the file
    template = env.get_template('pres_template.php')

    # Assuming you have a logic to group properties for form layout
    form_layout_groups = [form_layout_properties[i:i+4] for i in range(0, len(form_layout_properties), 4)]

    # Render the template with context data
    pres_class = template.render(
        class_name=class_name,
        namespace_prefix=namespace_prefix,
        presentation_title=presentation_title,
        presentation_fields=presentation_fields,
        form_layout_groups=form_layout_groups,
        unpack_check_fields=unpack_check_fields
    )

    return pres_class