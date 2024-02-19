<?php

namespace App\Presentation\Warranty\Setup;

use App\Dto\FieldTypeEnum;
use App\Presentation\BasePres;

class ProdModelPres extends BasePres
{
    public function __construct()
    {
        $this->initPresentationContent();
        $this->initFormLayoutContent();
        $this->initPresentationFieldContent();
    }

    public function initPresentationContent(): void
    {
        $this->presentationContent = [
            "id" => "ProdModel", "title" => "Product Model", "table" => true, "form" => true, "tab" => false,
            "readonly" => false, "autoPopulate" => true, "findByPrimaryKey" => false,
            "tabContent" => null,
            "toolbarButtonContent" => ["refresh" => true, "operation" => false, "create" => true, "edit" => true, "delete" => true],
            "scannerButtonContent" => ["qrcode" => false, "barcode" => false]
        ];
    }

    public function initFormLayoutContent(): void
    {
        $this->formLayout = [
            ["objstate", "objevents", "state", "objkey"],
            ["export_no", "is_active"],
            
        ];
    }

    public function initPresentationFieldContent(): void
    {
        $this->presentationFields = [
            
            [
                "id" => "objstate", "label" => "OBJSTATE",
                "type" => FieldTypeEnum::STRING, "inputType" => FieldTypeEnum::STRING, "length" => 100,
                "primaryKey" => false, "presentation" => true, "hidden" => false, "visible" => true,
                "detail" => true, "mandatory" => false, "insertable" => false, "updateable" => false,
                "onchange" => false, "onchangeLookup" => null, "lov" => false, "lovDetail" => null,
                "referenceController" => null, "referenceService" => null, "referencePres" => null,
                "iid" => false, "staticIidEnum" => null, "uploader" => false, "downloader" => false,
                "thousandSeparator" => false, "decimalPrecision" => 2,
                "internalZoomContent" => null,
                "externalZoomContent" => null
            ],
            
            [
                "id" => "objevents", "label" => "OBJEVENTS",
                "type" => FieldTypeEnum::STRING, "inputType" => FieldTypeEnum::STRING, "length" => 10,
                "primaryKey" => false, "presentation" => true, "hidden" => false, "visible" => true,
                "detail" => true, "mandatory" => false, "insertable" => false, "updateable" => false,
                "onchange" => false, "onchangeLookup" => null, "lov" => false, "lovDetail" => null,
                "referenceController" => null, "referenceService" => null, "referencePres" => null,
                "iid" => false, "staticIidEnum" => null, "uploader" => false, "downloader" => false,
                "thousandSeparator" => false, "decimalPrecision" => 2,
                "internalZoomContent" => null,
                "externalZoomContent" => null
            ],
            
            [
                "id" => "state", "label" => "State",
                "type" => FieldTypeEnum::STRING, "inputType" => FieldTypeEnum::STRING, "length" => 20,
                "primaryKey" => false, "presentation" => true, "hidden" => false, "visible" => true,
                "detail" => true, "mandatory" => false, "insertable" => false, "updateable" => false,
                "onchange" => false, "onchangeLookup" => null, "lov" => false, "lovDetail" => null,
                "referenceController" => null, "referenceService" => null, "referencePres" => null,
                "iid" => false, "staticIidEnum" => null, "uploader" => false, "downloader" => false,
                "thousandSeparator" => false, "decimalPrecision" => 2,
                "internalZoomContent" => null,
                "externalZoomContent" => null
            ],
            
            [
                "id" => "objkey", "label" => "OBJKEY",
                "type" => FieldTypeEnum::STRING, "inputType" => FieldTypeEnum::STRING, "length" => 100,
                "primaryKey" => false, "presentation" => true, "hidden" => false, "visible" => true,
                "detail" => true, "mandatory" => false, "insertable" => false, "updateable" => false,
                "onchange" => false, "onchangeLookup" => null, "lov" => false, "lovDetail" => null,
                "referenceController" => null, "referenceService" => null, "referencePres" => null,
                "iid" => false, "staticIidEnum" => null, "uploader" => false, "downloader" => false,
                "thousandSeparator" => false, "decimalPrecision" => 2,
                "internalZoomContent" => null,
                "externalZoomContent" => null
            ],
            
            [
                "id" => "export_no", "label" => "Export Serial No",
                "type" => FieldTypeEnum::STRING, "inputType" => FieldTypeEnum::STRING, "length" => 50,
                "primaryKey" => false, "presentation" => true, "hidden" => false, "visible" => true,
                "detail" => true, "mandatory" => false, "insertable" => false, "updateable" => false,
                "onchange" => false, "onchangeLookup" => null, "lov" => false, "lovDetail" => null,
                "referenceController" => null, "referenceService" => null, "referencePres" => null,
                "iid" => false, "staticIidEnum" => null, "uploader" => false, "downloader" => false,
                "thousandSeparator" => false, "decimalPrecision" => 2,
                "internalZoomContent" => null,
                "externalZoomContent" => null
            ],
            
            [
                "id" => "is_active", "label" => "Generator Activation",
                "type" => FieldTypeEnum::BOOLEAN, "inputType" => FieldTypeEnum::BOOLEAN, "length" => 100,
                "primaryKey" => true, "presentation" => true, "hidden" => false, "visible" => true,
                "detail" => true, "mandatory" => false, "insertable" => true, "updateable" => false,
                "onchange" => false, "onchangeLookup" => null, "lov" => false, "lovDetail" => null,
                "referenceController" => null, "referenceService" => null, "referencePres" => null,
                "iid" => false, "staticIidEnum" => null, "uploader" => false, "downloader" => false,
                "thousandSeparator" => false, "decimalPrecision" => 2,
                "internalZoomContent" => null,
                "externalZoomContent" => null
            ],
            
        ];
    }
}