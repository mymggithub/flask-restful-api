var crudServiceBaseUrl = "http://"+window.location.host+":5000";
var gridSelected = [];
var is_windows = /Windows/i.test(navigator.userAgent);
var selectable = is_windows?"multiple":false;
$(function () {

    var ctx = document.getElementById("myChart").getContext("2d");
    var json_url = crudServiceBaseUrl+"/info";///?callback=?

    var myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ["Missing","Cache","Skipped"],
            datasets: [
                {
                    label: "My First dataset",
                    backgroundColor: ["#4e73df","#1cc88a","#f6c23e"],
                    data: [],
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            legend: {
                display: false,
                labels: {fontStyle:"normal"}
            },
            title: {fontStyle:"normal"}
        }
    });
    ajax_chart(myChart, json_url);

    var dataSource = new kendo.data.DataSource({
        transport: {
            read: {
                url: crudServiceBaseUrl + "/",
                dataType: "json"
            },
            parameterMap: function (options, operation) {
                if (operation !== "read" && options.models) {
                    return { models: kendo.stringify(options.models) };
                }
            }
        },
        batch: true,
        pageSize: 200,
        // autoSync: true,
        // aggregate: [{
        //     field: "TotalSales",
        //     aggregate: "sum"
        // }],
        // group: { field: "following", dir: "desc" },
        sort: { field: "following", dir: "desc" },
        schema: {
            model: {
                id: "twit_id",
                fields: {
                    twit_id: {  type: "number", editable: false, nullable: true },
                    following: { type: "number" },
                    followers: { type: "number" },
                    will_f: { type: "number" },
                    wont_f: { type: "number" },
                    cached: { type: "boolean", editable: false },
                    scanned: { type: "boolean", editable: false },
                    description: { type: "string", editable: false },
                    bday: { type: "string", editable: false },
                    location: { type: "string", editable: false },
                    link: { type: "string", editable: false },
                    blank_pfp: { type: "boolean", editable: false },
                    // skip: { type: "number", editable: false },
                }
            },
            data: "data"
        }
    });

    $("#grid").kendoGrid({
        dataSource: dataSource,
        selectable: selectable,
        persistSelection: true,
        height: 680,
        scrollable: { virtual: true },
        // editable: "incell",
        pageable: {
            refresh:true,
            pageSizes: [10, 50, 100, 200, 500, 1000],//, 'all'
            numeric: true,
            previousNext: true,
            // messages: {
            //     display: "Showing {2} data items"
            // }
        },
        sortable: {
            mode: "mixed",
            allowUnsort: true,
            showIndexes: true
        },
        navigatable: true,
        resizable: true,
        reorderable: true,
        groupable: true,
        filterable: true,
        columnMenu: {
            componentType: "modern",
            filterable: true,
        },
        dataBound: onDataBound,
        page: onPaging,
        dataBinding: onDataBinding,
        change: onChange,
        toolbar: ["search"],
        columns: [
            {
                field: "twit_id",
                title: "ID",
                hidden: !is_windows,
                locked: is_windows,
                lockable: true,
                width: 100,
            },
            {
                field: "t_username",
                title: "Username",
                locked: is_windows,
                lockable: true,
                template: function(arg) {
                    if (arg.cached) {
                        return "<div class='user-photo'  style='background-image: url(../assets/img/pfp/"+arg.t_username+".jpg);'></div><div class='username-list'><a href='https://twitter.com/"+arg.t_username+"' target='_blank'>"+arg.t_username+"</a></div>";
                    }
                    return "<div class='username-list'><a href='https://twitter.com/"+arg.t_username+"' target='_blank'>"+arg.t_username+"</a></div>";
                },
                width: 225,
                filterable: {search: true} 
            }, 
            {
                field: "following",
                title: "Following",
                format: "{0:n0}",
                width: 105
            }, 
            {
                field: "followers",
                title: "Followers",
                format: "{0:n0}",
                width: 105
            }, 
            {
                field: "will_f",
                title: "Will follow back",
                format: "{0}%",
                template: "<div><div style='display: inline-block; width: 75%;'><div class='progress'><div class='progress-bar bg-success' aria-valuenow='#= will_f#' aria-valuemin='0' aria-valuemax='100' style='width: #= will_f#%;'>&nbsp;<span class='visually-hidden'></span></div></div></div><span> &nbsp;#= will_f#%</span></div>",
                width: 220
            }, 
            {
                field: "wont_f",
                title: "Wont follow back",
                format: "{0}%",
                template: "<div><div style='display: inline-block; width: 75%;'><div class='progress'><div class='progress-bar bg-danger' aria-valuenow='#= wont_f#' aria-valuemin='0' aria-valuemax='100' style='width: #= wont_f#%;'>&nbsp;<span class='visually-hidden'></span></div></div></div><span> &nbsp;#= wont_f#%</span></div>",
                width: 220
            },
            {
                field: "cached",
                title: "Cached",
                template: function (arg) {
                    if (arg.cached) {
                        return "<span class='badge bg-success'>Saved</span>";
                    }else if (arg.skip) {
                        return "<span class='badge bg-warning text-dark'>Skipped</span>";
                    }
                    return "<span class='badge bg-danger'>Nope</span>";
                },
                width: 105,
                filterable: { multi: true }
            }, 
            {
                field: "scanned",
                title: "Scanned",
                template: function (arg) {
                    if (arg.scanned) {
                        return "<span class='badge bg-info'>Scanned</span>";
                    }
                    return "<span class='badge bg-danger'>Nope</span>";
                },
                width: 105,
                filterable: { ui: boolScannedFilterTemplate  }
            },
            {
                field: "blank_pfp",
                title: "Blank",
                template: function (arg) {
                    if (arg.blank_pfp) {
                        return "<span class='badge bg-danger'>Blank</span>";
                    }else {
                        return "<span class='badge bg-success'>Has Pic</span>";
                    }
                },
                width: 105,
                filterable: { ui: boolBlankFilterTemplate }
            }, 
            {
                field: "description",
                title: "Description",
                width: 600,
                filterable: {search: true} 
            }, 
            {
                field: "bday",
                title: "B-Day",
                width: 100,
            },
            {
                field: "location",
                title: "Location",
                width: 300,
            }, 
            {
                field: "link",
                title: "Link",
                width: 300,
            }, 
            // { command: "destroy", title: "&nbsp;", width: 120 }
        ],
        filter: onFilter,
        columnMenuInit: onFilterMenuInit
    });

    $("#appbar").kendoAppBar({
        themeColor: "inherit",
        items: [
            { template: '<a role="button" class="k-button k-button-flat-base k-button-flat k-button-md k-rounded-md k-icon-button" href="\\#"><span class="k-button-icon k-button-icon k-icon k-i-pointer"></span> Multi Select Tool</a>', type: "contentItem" },
        ]
    }).on("click", ".k-button", function (e) {
        e.preventDefault();
        var grid = $("#grid").data("kendoGrid");
        // grid.selectable.clear();
        if (grid.selectable == null) {
            grid.lockColumn("twit_id");
            grid.setOptions({selectable:"multiple"});
            $(".right-select-items").show();
        }else{
            grid.setOptions({selectable:false});
            $(".right-select-items").hide();
        }
    });
    if (is_windows) {$(".right-select-items").show();}
});

function boolScannedFilterTemplate(input) {
    input.kendoDropDownList({
        dataSource: {
            data: [
                { text: "Scanned", value: true },
                { text: "Un-scanned", value: false }
            ]
        },
        dataTextField: "text",
        dataValueField: "value",
        valuePrimitive: true,
        optionLabel: "All"
    });
}

function boolBlankFilterTemplate(input) {
    input.kendoDropDownList({
        dataSource: {
            data: [
                { text: "Blank", value: true },
                { text: "Has Pic", value: false }
            ]
        },
        dataTextField: "text",
        dataValueField: "value",
        valuePrimitive: true,
        optionLabel: "All"
    });
}

function onFilter(e){
    if (e.field === "scanned" || e.field === "blank_pfp") {
        var filter = e.filter;
        if (filter && filter.filters && filter.filters.length > 0) {
            var filters = filter.filters;
            filters[0].value = (filters[0].value === "true");
        }
    }
}

function onFilterMenuInit(e){
    if (e.field === "scanned" || e.field === "blank_pfp") {
        e.container.find(".k-filter-help-text").text("Show items with value:");
    }
}
function onChange(arg) {
    gridSelected = $.map(this.select(), function(item) {
        return $(item).find(".username-list a").text();//grid.getSelectedData()
    });
}
function onPaging(arg) {
    console.log("Paging to page index:" + arg.page);
}
function onDataBinding(arg) {
    console.log("Grid data binding");
}
function onDataBound(e) {
    var grid = this;
    // grid.table.find("tr").each(function () {
    //     var dataItem = grid.dataItem(this);
    //     var themeColor = dataItem.cached ? 'success' : 'error';
    //     var text = dataItem.cached ? 'Yes' : 'Nope';

        // $(this).find(".badgeTemplate").kendoBadge({
        //     themeColor: themeColor,
        //     text: text,
        // });

        // $(this).find(".sparkline-chart").kendoSparkline({
        //     legend: {
        //         visible: false
        //     },
        //     data: [Math.abs(dataItem.will_f)],
        //     type: "bar",
        //     chartArea: {
        //         margin: 0,
        //         width: 180,
        //         background: "transparent"
        //     },
        //     seriesDefaults: {
        //         color: "green",
        //         labels: {
        //             visible: true,
        //             format: '{0}%',
        //             background: 'none'
        //         }
        //     },
        //     categoryAxis: {
        //         majorGridLines: {
        //             visible: false
        //         },
        //         majorTicks: {
        //             visible: false
        //         }
        //     },
        //     valueAxis: {
        //         type: "numeric",
        //         min: 0,
        //         max: 130,
        //         visible: false,
        //         labels: {
        //             visible: false
        //         },
        //         minorTicks: { visible: false },
        //         majorGridLines: { visible: false }
        //     },
        //     tooltip: {
        //         visible: false
        //     }
        // });

        // kendo.bind($(this), dataItem);
    // });

    setTimeout(function () {
        var menu = $("#menu"),
            original = menu.clone(true);

        original.find(".k-active").removeClass("k-active");

        $("#apply").click(function (e) {
            e.preventDefault();
            var clone = original.clone(true);

            menu.getKendoContextMenu().destroy();
            clone.appendTo("#grid");

            initMenu();
        });

        var initMenu = function () {
            menu = $("#menu").kendoContextMenu({
                target: "#grid",
                // filter: ".product",
                animation: {
                    open: { effects: "fadeIn" },
                    duration: 500
                },
                select: function(e) {
                    clicked_item_classes = $(e.item).attr("class").split(/\s+/);
                    action_index = clicked_item_classes.findIndex(element => element.includes("right-action"))
                    if (action_index > -1) {
                        action_name = clicked_item_classes[action_index].replace("right-action-", "");
                    }else{ return false; }
                    console.log(action_name);
                    var grid = $("#grid").data("kendoGrid");
                    switch(action_name) {
                        case "update-fb":
                            $.getJSON(crudServiceBaseUrl+"/updateWillWont/").done(function(response) {
                                console.log(response);
                                grid.dataSource.read();// $("#grid .k-pager-refresh").click()
                            });
                            break;
                        case "delete-user":
                            $.ajax({
                                type: "POST",
                                contentType: "application/json",
                                url: crudServiceBaseUrl+"/del_users/",
                                data: JSON.stringify({ t_usernames:gridSelected }),
                                success: function(data) {
                                    grid.dataSource.read();
                                },
                                dataType: "json"
                            });
                            break;
                        case "re-download":
                            $.ajax({
                                type: "POST",
                                contentType: "application/json",
                                url: crudServiceBaseUrl+"/redownload/",
                                data: JSON.stringify({ t_usernames:gridSelected }),
                                success: function(data) {
                                    grid.dataSource.read();
                                },
                                dataType: "json"
                            });
                            break;
                        case "re-scan":
                            $.ajax({
                                type: "POST",
                                contentType: "application/json",
                                url: crudServiceBaseUrl+"/rescan/",
                                data: JSON.stringify({ t_usernames:gridSelected }),
                                success: function(data) {
                                    grid.dataSource.read();
                                },
                                dataType: "json"
                            });
                            break;
                        case "re-scan-all":
                            $.getJSON(crudServiceBaseUrl+"/rescanall/").done(function(response) {
                                console.log(response);
                                grid.dataSource.read();// $("#grid .k-pager-refresh").click()
                            });
                            break;
                        default:
                    }
                    return true;
                }
            });
        };

        initMenu();        
    }, 0);
}
function ajax_chart(chart, url, data) {
    var data = data || {};
    $.getJSON(url, data).done(function(response) {
        $("#total_users").text(response.data["total"].toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        $("#cache").text(response.data["num_cached"].toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        $("#skipped").text(response.data["num_skipped"].toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","));
        chart.data.datasets[0].data = [response.data["missing"], response.data["num_cached"], response.data["num_skipped"]]; // or you can iterate for multiple datasets
        chart.update();
        chart.resize()
    });
}