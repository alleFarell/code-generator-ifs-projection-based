<?php

namespace App\Dto\Warranty\Setup;

use App\Dto\BaseDto;

class ProdModelDto extends BaseDto
{
    private string $objstate;
    private string $objevents;
    private string $state;
    private string $objkey;
    private string $exportNo;
    private bool $isActive;
    
    public function __construct(
        string $objstate = null,
        string $objevents = null,
        string $state = null,
        string $objkey = null,
        string $exportNo = null,
        bool $isActive = false
        ) {
        
        $this->objstate = $objstate;
        $this->objevents = $objevents;
        $this->state = $state;
        $this->objkey = $objkey;
        $this->exportNo = $exportNo;
        $this->isActive = $isActive;
        
    }
    
    public function getObjstate(): string
    {
        return $this->objstate;
    }
    public function setObjstate(string $objstate): void
    {
        $this->objstate = $objstate;
    }
    
    public function getObjevents(): string
    {
        return $this->objevents;
    }
    public function setObjevents(string $objevents): void
    {
        $this->objevents = $objevents;
    }
    
    public function getState(): string
    {
        return $this->state;
    }
    public function setState(string $state): void
    {
        $this->state = $state;
    }
    
    public function getObjkey(): string
    {
        return $this->objkey;
    }
    public function setObjkey(string $objkey): void
    {
        $this->objkey = $objkey;
    }
    
    public function getExportNo(): string
    {
        return $this->exportNo;
    }
    public function setExportNo(string $exportNo): void
    {
        $this->exportNo = $exportNo;
    }
    
    public function getIsActive(): bool
    {
        return $this->isActive;
    }
    public function setIsActive(bool $isActive): void
    {
        $this->isActive = $isActive;
    }
    
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