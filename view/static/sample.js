function drawChart(dataset)
{
    var ctx = document.getElementById("myChart").getContext("2d");
    var chart = new Chart(ctx, {
        type: 'radar',
        data: dataset
    });
}