import re

# 1
def pascal_to_kebab(s):
    """Convert a PascalCase string to kebab-case."""
    return '-'.join(re.sub('([a-z0-9])([A-Z])', r'\1-\2', s).lower().split())

def snake_to_pascal(snake_case_str):
    """Convert a snake_case string to PascalCase."""
    words = snake_case_str.split('_')
    capitalized_words = [word.capitalize() for word in words if word]
    return ''.join(capitalized_words)

def string_to_pascal(string):
    """Convert a space separated string to PascalCase."""
    words = string.split()
    pascal_case = ''.join(word.capitalize() for word in words)
    return pascal_case

def pascal_to_string(s):
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', s)

#2
def snake_to_camel(s):
    """Converts snake case strings to camelCase."""
    parts = s.split('_')
    return parts[0].lower() + ''.join(part.title() for part in parts[1:])

def camel_to_pascal(s):
    """Converts camelCase strings to PascalCase."""
    return s[0].upper() + s[1:] if s else s

def camel_to_snake(s):
    """Converts strings to snake_case."""
    return '_'.join(re.findall('[A-Z][^A-Z]*', s)).lower()

def upper_to_lower_snake(s):
    """Converts strings from UPPER_CASE to snake_case."""
    # If the string is already in UPPER_CASE, just convert it to lower case
    return s.lower()

def format_enum_case(name):
    return name.replace(" ", "_").upper()