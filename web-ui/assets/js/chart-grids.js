crudServiceBaseUrl = "http://"+window.location.host+":5000"
$(function () {
    var ctx = document.getElementById("myChart").getContext("2d");
    var json_url = crudServiceBaseUrl+"/info/?callback=?";

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
    $("#menu").hide();
    var dataSource = new kendo.data.DataSource({
            transport: {
                read: {
                    url: crudServiceBaseUrl + "/",
                    dataType: "jsonp"
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
                        twit_id: { editable: false, nullable: true },
                        // Discontinued: { type: "boolean", editable: false },
                        following: { type: "number" },
                        followers: { type: "number" },
                        will_f: { type: "number" },
                        wont_f: { type: "number" },
                    }
                },
                data: "data"
            }
        });

    $("#grid").kendoGrid({
        dataSource: dataSource,
        selectable: "multiple",
        persistSelection: true,
        columnMenu: {
            filterable: false
        },
        height: 680,
        scrollable: { virtual: true },
        // editable: "incell",
        pageable: {
            refresh:true,
            pageSizes: [10, 50, 100, 200, 500],//'all',
            numeric: false,
            // previousNext: true,
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
        dataBound: onDataBound,
        toolbar: ["search"],
        columns: [
            {
                field: "twit_id",
                title: "ID",
                width: 105
            },
            {
                field: "t_username",
                title: "Username",
                template: "<div class='product-photo'  style='background-image: url(../assets/img/pfp/#:data.t_username#.jpg), url(../assets/img/pfp/#:data.t_username#.jpeg), url(../assets/img/pfp/#:data.t_username#.png);'></div><div class='product-name'><a href='https://twitter.com/#: t_username #' target='_blank'>#: t_username #</a></div>",
                width: 300
            }, 
            // {
            //     field: "Discontinued",
            //     title: "Popular",
            //     template: "<span id='badge_#=twit_id#' class='badgeTemplate'></span>",
            //     width: 130,
            // }, 
            {
                field: "following",
                title: "Following",
                width: 105
            }, 
            {
                field: "followers",
                title: "Followers",
                width: 105
            }, 
            {
                field: "will_f",
                title: "Will follow back",
                format: "{0}%",
                template: "<span id='chart_#= twit_id#' class='sparkline-chart'></span>",
                width: 220
            }, 
            {
                field: "wont_f",
                title: "Wont follow back",
                format: "{0}%",
                template: "<span id='chart_#= twit_id#' class='sparkline-chart-red'></span>",
                width: 220
            },
            // { command: "destroy", title: "&nbsp;", width: 120 }
        ],
    });
});

function onDataBound(e) {
    var grid = this;
    grid.table.find("tr").each(function () {
        var dataItem = grid.dataItem(this);
        var themeColor = dataItem.Discontinued ? 'success' : 'error';
        var text = dataItem.Discontinued ? 'Yes' : 'Nope';

        $(this).find(".badgeTemplate").kendoBadge({
            themeColor: themeColor,
            text: text,
        });

        $(this).find(".sparkline-chart").kendoSparkline({
            legend: {
                visible: false
            },
            data: [Math.abs(dataItem.will_f)],
            type: "bar",
            chartArea: {
                margin: 0,
                width: 180,
                background: "transparent"
            },
            seriesDefaults: {
                color: "green",
                labels: {
                    visible: true,
                    format: '{0}%',
                    background: 'none'
                }
            },
            categoryAxis: {
                majorGridLines: {
                    visible: false
                },
                majorTicks: {
                    visible: false
                }
            },
            valueAxis: {
                type: "numeric",
                min: 0,
                max: 130,
                visible: false,
                labels: {
                    visible: false
                },
                minorTicks: { visible: false },
                majorGridLines: { visible: false }
            },
            tooltip: {
                visible: false
            }
        });
        $(this).find(".sparkline-chart-red").kendoSparkline({
            legend: {
                visible: false
            },
            data: [Math.abs(dataItem.wont_f)],
            type: "bar",
            chartArea: {
                margin: 0,
                width: 180,
                background: "transparent"
            },
            seriesDefaults: {
                color: "#ff0000",
                labels: {
                    visible: true,
                    format: '{0}%',
                    background: 'none'
                }
            },
            categoryAxis: {
                majorGridLines: {
                    visible: false
                },
                majorTicks: {
                    visible: false
                }
            },
            valueAxis: {
                type: "numeric",
                min: 0,
                max: 130,
                visible: false,
                labels: {
                    visible: false
                },
                minorTicks: { visible: false },
                majorGridLines: { visible: false }
            },
            tooltip: {
                visible: false
            }
        });

        kendo.bind($(this), dataItem);
    });

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
                    // Do something on select
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