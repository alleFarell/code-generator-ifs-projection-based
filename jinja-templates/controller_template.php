<?php

namespace App\Http\Controllers\{{ namespace_prefix }};

use App\Http\Controllers\BaseController;
use App\Services\{{ namespace_prefix }}\{{ class_name }}Service;
use App\Presentation\{{ namespace_prefix }}\{{ class_name }}Pres;

class {{ class_name }}Controller extends BaseController
{
    public function __construct()
    {
        $this->service = new {{ class_name }}Service();
        $this->pres = new {{ class_name }}Pres();
        $this->url = {url here};
    }
}