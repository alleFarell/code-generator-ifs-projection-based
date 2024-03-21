<?php

namespace App\Presentation\{{ namespace_prefix }};

use App\Dto\FieldTypeEnum;
use App\Presentation\BasePres;

class {{ class_name }}Pres extends BasePres
{
    public function __construct()
    {
        $this->initPresentationContent();
        $this->initFormLayoutContent();
        $this->initPresentationFieldContent();
        $this->initUnpackCheck();
    }

    public function initPresentationContent(): void
    {
        $this->presentationContent = [
            "id" => "{{ class_name }}", "title" => "{{ presentation_title }}", "table" => true, "form" => true, "tab" => false,
            "readonly" => false, "autoPopulate" => true, "findByPrimaryKey" => false,
            "tabContent" => null,
            "toolbarButtonContent" => ["refresh" => true, "operation" => false, "create" => true, "edit" => true, "delete" => true],
            "scannerButtonContent" => ["qrcode" => false, "barcode" => false]
        ];
    }

    public function initFormLayoutContent(): void
    {
        $this->formLayout = [
            {% for group in form_layout_groups %}[{% for field in group %}"{{ field }}"{% if not loop.last %}, {% endif %}{% endfor %}]{% if not loop.last %},{% endif %}
            {% endfor %}
        ];
    }

    public function initPresentationFieldContent(): void
    {
        $this->presentationFields = [
            {% for field in presentation_fields %}
            [
                "id" => "{{ field.id }}", "label" => "{{ field.label }}",
                "type" => {{ field.type }}, "inputType" => {{ field.inputType }}, "length" => {{ field.length }},
                "primaryKey" => {{ field.primaryKey|lower }}, "presentation" => {{ field.presentation|lower }}, "hidden" => {{ field.hidden|lower }}, "visible" => {{ field.visible|lower }},
                "detail" => {{ field.detail|lower }}, "mandatory" => {{ field.mandatory|lower }}, "insertable" => {{ field.insertable|lower }}, "updateable" => {{ field.updateable|lower }},
                "onchange" => {{ field.onchange|lower }}, "onchangeLookup" => {{ field.onchangeLookup }}, "lov" => {{ field.lov|lower }}, "lovDetail" => {{ field.lovDetail }},
                "referenceController" => {{ field.referenceController }}, "referenceService" => {{ field.referenceService }}, "referencePres" => {{ field.referencePres }},
                "iid" => {{ field.iid|lower }}, "staticIidEnum" => {{ field.staticIidEnum }}, "uploader" => {{ field.uploader|lower }}, "downloader" => {{ field.downloader|lower }},
                "thousandSeparator" => {{ field.thousandSeparator|lower }}, "decimalPrecision" => {{ field.decimalPrecision }},
                "internalZoomContent" => {{ field.internalZoomContent }},
                "externalZoomContent" => {{ field.externalZoomContent }}
            ],
            {% endfor %}
        ];
    }

    public function initUnpackCheck(): void
    {
        $this->unpackCheck = [
            {% for field in unpack_check_fields %}["id" => "{{ field.id }}", "insert" => "{{ field.insertable }}", "update" => "{{ field.updateable }}"]{% if not loop.last %},{% endif %}
            {% endfor %} 
        ];
    }
}