<?php

namespace App\Dto\Iid;

enum {{ iid_class_name }}Enum: string
{
    {%- for db_value, client_value in pairs %}
    case {{ db_value|upper }} = "{{ client_value }}";
    {%- endfor %}
}
