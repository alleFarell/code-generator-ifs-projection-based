<?php

namespace App\Dto\{{ namespace_prefix }};

use App\Dto\BaseDto;

class {{ class_name }}Dto extends BaseDto
{
    {% for prop in properties %}private {{ prop.type }} ${{ prop.name }};
    {% endfor %}
    public function __construct(
        {% for prop in properties %}{{ prop.type }} ${{ prop.name }} = {{ prop.default }}{% if not loop.last %},{% else %}
        ) {
        {% endif %}
        {% endfor %}{% for prop in properties %}$this->{{ prop.name }} = ${{ prop.name }};
        {% endfor %}
    }
    {% for prop in properties %}
    public function get{{ prop.name|pascal_case }}(): {{ prop.type }}
    {
        return $this->{{ prop.name }};
    }
    public function set{{ prop.name|pascal_case }}({{ prop.type }} ${{ prop.name }}): void
    {
        $this->{{ prop.name }} = ${{ prop.name }};
    }
    {% endfor %}
    public function jsonSerialize()
    {
        $parentResult = parent::jsonSerialize(); // Get default properties from BaseDto

        $additionalProperties = array_combine(
            array_map(fn($key) => strtolower(preg_replace('/(?<!^)[A-Z]/', '_$0', $key)), array_keys(get_object_vars($this))),
            get_object_vars($this)
        );

        return array_merge($parentResult, $additionalProperties);
    }
}