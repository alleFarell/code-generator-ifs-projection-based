<?php

namespace App\Services\{{ namespace_prefix }};

use App\Dto\BaseDto;
use App\Services\BaseService;
use App\Dto\{{ namespace_prefix }}\{{class_name}}Dto;

class {{ class_name }}Service extends BaseService
{
    public function __construct()
    {
        parent::__construct();
        $this->ifsProjectionAPIUrl = "{{ projection }}";
    }

    public static function getInstance()
    {
        if (!self::$instance) {
            self::$instance = new self();
        }

        return self::$instance;
    }

    protected function transformDto(BaseDto $dto): BaseDto
    {
        if ($dto instanceof BaseDto) {
            return new {{ class_name }}Dto();
        }

        return $dto;
    }
}