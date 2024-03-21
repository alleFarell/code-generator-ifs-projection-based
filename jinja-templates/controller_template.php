<?php

namespace App\Http\Controllers\{{ namespace_prefix }};

use App\Dto\BaseDto;
use App\Http\Controllers\BaseController;
use App\Dto\{{ namespace_prefix }}\{{ class_name }}Dto;
use App\Services\{{ namespace_prefix }}\{{ class_name }}Service;
use App\Presentation\{{ namespace_prefix }}\{{ class_name }}Pres;

class {{ class_name }}Controller extends BaseController
{

    public static string $route = "{{ menu_route }}";

    public function __construct()
    {
        $this->service = {{ class_name }}Service::getInstance();
        $this->pres = new {{ class_name }}Pres();
        $this->dto = new {{ class_name }}Dto();
        parent::__construct();
    }

    public static function register()
    {
        parent::registerRoutes(self::$route);
    }

    protected function transformDto(BaseDto $dto): BaseDto
    {
        if ($dto instanceof BaseDto) {
            return new {{ class_name }}Dto();
        }

        return $dto;
    }
}