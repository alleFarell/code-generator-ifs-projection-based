<?php

namespace App\Http\Controllers\Warranty\Setup;

use App\Http\Controllers\BaseController;
use App\Services\Warranty\Setup\ProdModelService;
use App\Presentation\Warranty\Setup\ProdModelPres;

class ProdModelController extends BaseController
{
    public function __construct()
    {
        $this->service = new ProdModelService();
        $this->pres = new ProdModelPres();
        $this->url = {url here};
    }
}