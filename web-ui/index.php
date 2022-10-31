<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
        <title>Dashboard - Bot</title>
        <link rel="stylesheet" href="assets/bootstrap/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.0/css/all.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        <link rel="stylesheet" href="//kendo.cdn.telerik.com/2022.1.412/styles/kendo.default-ocean-blue.min.css" />
        <link rel="stylesheet" href="assets/fonts/fontawesome5-overrides.min.css">
        <style type="text/css">
            .customer-photo {
                display: inline-block;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background-size: 32px 35px;
                background-position: center center;
                vertical-align: middle;
                line-height: 32px;
                box-shadow: inset 0 0 1px #999, inset 0 0 10px rgba(0,0,0,.2);
                margin-left: 5px;
            }

            .customer-name {
                display: inline-block;
                vertical-align: middle;
                line-height: 32px;
                padding-left: 3px;
            }

            .k-grid tr .checkbox-align {
                text-align: center;
                vertical-align: middle;
            }

            .product-photo {
                display: inline-block;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background-size: 32px 35px;
                background-position: center center;
                vertical-align: middle;
                line-height: 32px;
                box-shadow: inset 0 0 1px #999, inset 0 0 10px rgba(0,0,0,.2);
                margin-right: 5px;
            }

            .product-name {
                display: inline-block;
                vertical-align: middle;
                line-height: 32px;
                padding-left: 3px;
            }

            .k-rating-container .k-rating-item {
                padding: 4px 0;
            }

            .k-rating-container .k-rating-item .k-icon {
                font-size: 16px;
            }

            .dropdown-country-wrap {
                display: flex;
                flex-wrap: nowrap;
                align-items: center;
                white-space: nowrap;
            }

            .dropdown-country-wrap img {
                margin-right: 10px;
            }

            #grid .k-grid-edit-row > td > .k-rating {
                margin-left: 0;
                width: 100%;
            }
        </style>
    </head>

    <body id="page-top">
        <div id="wrapper">
            <nav class="navbar navbar-dark align-items-start sidebar sidebar-dark accordion bg-gradient-primary p-0 toggled">
                <div class="container-fluid d-flex flex-column p-0">
                    <hr class="sidebar-divider my-0">
                    <ul class="navbar-nav text-light" id="accordionSidebar">
                        <li class="nav-item"><a class="nav-link" href="http://<?php echo $_SERVER['SERVER_NAME'] ?>:9002" target="_blank"><i class="fas fa-tachometer-alt"></i><span>Portainer</span></a></li>
                        <li class="nav-item"><a class="nav-link" href="http://<?php echo $_SERVER['SERVER_NAME'] ?>:9001" target="_blank"><i class="fas fa-table"></i><span>MySQL</span></a></li>
                    </ul>
                    <div class="text-center d-none d-md-inline"><button class="btn rounded-circle border-0" id="sidebarToggle" type="button"></button></div>
                </div>
            </nav>
            <div class="d-flex flex-column" id="content-wrapper">
                <div id="content">
                    <nav class="navbar navbar-light navbar-expand bg-white shadow mb-4 topbar static-top">
                        <div class="container-fluid"><button class="btn btn-link d-md-none rounded-circle me-3" id="sidebarToggleTop" type="button"><i class="fas fa-bars"></i></button>
                            <ul class="navbar-nav flex-nowrap ms-auto">
                                <div class="d-none d-sm-block topbar-divider"></div>
                                <li class="nav-item dropdown no-arrow">
                                    <div class="nav-item dropdown no-arrow"><a class="dropdown-toggle nav-link" aria-expanded="false" data-bs-toggle="dropdown" href="#"><span class="d-none d-lg-inline me-2 text-gray-600 small">Project 1</span></a>
                                        <div class="dropdown-menu shadow dropdown-menu-end animated--grow-in">
                                            <!-- <a class="dropdown-item" href="#"><i class="fas fa-user fa-sm fa-fw me-2 text-gray-400"></i>&nbsp;Profile</a> -->
                                            <!-- <a class="dropdown-item" href="#"><i class="fas fa-cogs fa-sm fa-fw me-2 text-gray-400"></i>&nbsp;Settings</a> -->
                                            <!-- <div class="dropdown-divider"></div> -->
                                        </div>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </nav>
                    <div class="container-fluid">
                        <div class="d-sm-flex justify-content-between align-items-center mb-4">
                            <h3 class="text-dark mb-0">Dashboard</h3><!-- <a class="btn btn-primary btn-sm d-none d-sm-inline-block" role="button" href="#"><i class="fas fa-download fa-sm text-white-50"></i>&nbsp;Generate Report</a> -->
                        </div>
                        <div class="row">
                            <div class="col-md-6 col-xl-3 mb-4">
                                <div class="card shadow border-start-primary py-2">
                                    <div class="card-body">
                                        <div class="row align-items-center no-gutters">
                                            <div class="col me-2">
                                                <div class="text-uppercase text-primary fw-bold text-xs mb-1"><span>Usernames (stored)</span></div>
                                                <div class="text-dark fw-bold h5 mb-0"><span id="total_users">0</span></div>
                                            </div>
                                            <div class="col-auto"><i class="fas fa-duotone fa-users fa-2x text-gray-300"></i></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 col-xl-3 mb-4">
                                <div class="card shadow border-start-success py-2">
                                    <div class="card-body">
                                        <div class="row align-items-center no-gutters">
                                            <div class="col me-2">
                                                <div class="text-uppercase text-success fw-bold text-xs mb-1"><span>User cache (downloaded)</span></div>
                                                <div class="text-dark fw-bold h5 mb-0"><span id="cache">0</span></div>
                                            </div>
                                            <div class="col-auto"><i class="fas fa-solid fa-server fa-2x text-gray-300"></i></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 col-xl-3 mb-4">
                                <div class="card shadow border-start-warning py-2">
                                    <div class="card-body">
                                        <div class="row align-items-center no-gutters">
                                            <div class="col me-2">
                                                <div class="text-uppercase text-warning fw-bold text-xs mb-1"><span>Skipped</span></div><!-- Pending TASKS -->
                                                <div class="text-dark fw-bold h5 mb-0"><span id="skipped">0</span></div>
                                            </div>
                                            <div class="col-auto"><i class="fas fa-forward fa-2x text-gray-300"></i></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 col-xl-3 mb-4">
                                <div class="card shadow border-start-info py-2">
                                    <div class="card-body">
                                        <div class="row align-items-center no-gutters">
                                            <div class="col me-2">
                                                <div class="text-uppercase text-danger fw-bold text-xs mb-1"><span>Errors</span></div>
                                                <div class="row g-0 align-items-center">
                                                    <div class="col-auto">
                                                        <div class="text-dark fw-bold h5 mb-0 me-3"><span>0</span></div>
                                                    </div>
                                                    <div class="col">
                                                        <!-- <div class="progress progress-sm">
                                                            <div class="progress-bar bg-info" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" style="width: 50%;"><span class="visually-hidden">50%</span></div>
                                                        </div> -->
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="col-auto"><i class="fas fa-exclamation-triangle fa-2x text-gray-300"></i></div><!-- fa-clipboard-list -->
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </div>
                        <div class="row">
                            <div class="col-lg-6">
                                <div class="card shadow mb-4">
                                    <div class="card-header py-3">
                                        <h6 class="text-primary fw-bold m-0">Results</h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="chart-area"><canvas id="myChart"></canvas></div>
                                        <div class="text-center small mt-4">
                                            <span class="me-2"><i class="fas fa-circle text-primary"></i>&nbsp;Missing</span>
                                            <span class="me-2"><i class="fas fa-circle text-success"></i>&nbsp;Cache</span>
                                            <span class="me-2"><i class="fas fa-circle text-warning"></i>&nbsp;Skipped</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="card shadow mb-4">
                                    <div class="card-header d-flex justify-content-between align-items-center">
                                        <h6 class="text-primary fw-bold m-0">Jobs List</h6>
                                        <div class="dropdown no-arrow"><button class="btn btn-link btn-sm dropdown-toggle" aria-expanded="false" data-bs-toggle="dropdown" type="button"><i class="fas fa-ellipsis-v text-gray-400"></i></button>
                                            <div class="dropdown-menu shadow dropdown-menu-end animated--fade-in">
                                                <p class="text-center dropdown-header">dropdown header:</p><a class="dropdown-item" href="#">&nbsp;Action</a><a class="dropdown-item" href="#">&nbsp;Another action</a>
                                                <div class="dropdown-divider"></div><a class="dropdown-item" href="#">&nbsp;Something else here</a>
                                            </div>
                                        </div>
                                    </div>
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item">
                                            <div class="row align-items-center no-gutters">
                                                <div class="col me-2">
                                                    <h6 class="mb-0"><strong>Cache Users</strong></h6><span class="text-xs">10:30 AM</span>
                                                </div>
                                                <div class="col-auto">
                                                    <div class="form-check"><input class="form-check-input" type="checkbox" id="formCheck-1"><label class="form-check-label" for="formCheck-1"></label></div>
                                                </div>
                                            </div>
                                            <div class="progress mb-2">
                                                <div class="progress-bar bg-primary" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style="width: 60%;"><span class="visually-hidden">60%</span></div>
                                            </div>
                                        </li>
                                        <li class="list-group-item">
                                            <div class="row align-items-center no-gutters">
                                                <div class="col me-2">
                                                    <h6 class="mb-0"><strong>Watch</strong></h6><span class="text-xs">11:30 AM</span>
                                                </div>
                                                <div class="col-auto">
                                                    <div class="form-check"><input class="form-check-input" type="checkbox" id="formCheck-2"><label class="form-check-label" for="formCheck-2"></label></div>
                                                </div>
                                            </div>
                                            <div class="progress mb-2">
                                                <div class="progress-bar bg-success" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%;"><span class="visually-hidden">100%</span></div>
                                            </div>
                                        </li>
                                        <li class="list-group-item">
                                            <div class="row align-items-center no-gutters">
                                                <div class="col me-2">
                                                    <h6 class="mb-0"><strong>Follow/Unfollow</strong></h6><span class="text-xs">12:30 AM</span>
                                                </div>
                                                <div class="col-auto">
                                                    <div class="form-check"><input class="form-check-input" type="checkbox" id="formCheck-3"><label class="form-check-label" for="formCheck-3"></label></div>
                                                </div>
                                            </div>
                                            <div class="progress mb-2">
                                                <div class="progress-bar bg-danger" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 20%;"><span class="visually-hidden">20%</span></div>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-lg-12">
                        <div class="card shadow">
                            <div class="card-header py-3">
                                <p class="text-primary m-0 fw-bold">Users Info</p>
                            </div>
                            <div class="card-body">
                                <div id="grid"></div>
                            </div>
                        </div> 
                            </div>
                        </div>
                    </div>
                </div>
                <footer class="bg-white sticky-footer">
                    <div class="container my-auto">
                    </div>
                </footer>
            </div>
            <a class="border rounded d-inline scroll-to-top" href="#page-top"><i class="fas fa-angle-up"></i></a>

        </div>

        <ul id="menu">
            <li>
                <span class="k-icon k-i-pointer"></span> Selected Actions
                <ul>
                    <li><span class="k-icon k-i-eye"></span> Watch</li>
                    <li><span class="k-icon k-i-heart"></span> Follow</li>
                    <li><span class="k-icon k-i-heart-outline"></span> Unfollow</li>
                    <li><span class="k-icon k-i-cancel"></span> Block</li>
                    <li><span class="k-icon k-i-data-web"></span> Re-download</li>
                </ul>
            </li>
            <li class="k-separator"></li>
            <li>
               <span class="k-icon k-i-filter-add-group"></span> Scan All Cache
            </li>
            <li class="k-separator"></li>
            <li>
               <span class="k-icon k-i-gears"></span> Xpath Settings
            </li>
        </ul>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
        <script src="//kendo.cdn.telerik.com/2022.1.412/js/kendo.all.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/jszip/2.4.0/jszip.min.js"></script>
        <script src="assets/js/bs-init.js"></script>
        <script src="assets/js/theme.js"></script>
        <script src="assets/js/chart-grids.js"></script>
    </body>
</html>