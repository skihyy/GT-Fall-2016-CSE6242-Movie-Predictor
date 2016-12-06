var comparisonChart;

/**
 * Drawing the radar chart.
 * @param dataset data set, refer to Chart.js for details
 */
function drawRadarChart(id, dataset) {
    var ctx = document.getElementById(id).getContext("2d");
    new Chart(ctx, {
        type: 'radar',
        data: dataset
    });
}

/**
 * Drawing the comparison chart.
 * @param numOfMoviesList number of movies in each score interval
 * @param avgDirectorScore avg score of directors in each score interval
 * @param avg_actor_score_list avg score of actors in each score interval
 * @param avg_actress_score_list avg score of actresses in each score interval
 */
function drawComparisonChart(numOfMoviesList, avgDirectorScore, avg_actor_score_list, avg_actress_score_list) {
    comparisonChart = echarts.init(document.getElementById("comparison-chart"));

    var maxNumOfMovie = getMaxOfArray(numOfMoviesList);
    var interval = Math.ceil(maxNumOfMovie / 5);

    var option = {
        title: {text: ""},
        tooltip: {trigger: 'axis'},
        toolbox: {
            feature: {
                dataView: {show: true, readOnly: false},
                magicType: {show: true, type: ['line', 'bar']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        legend: {data: ['Number of Movies', 'Average Director Score', 'Average Actor Score', 'Average Actress Score']},
        xAxis: [{type: 'category', data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']}],
        yAxis: [
            {
                type: 'value',
                name: 'Number of Movies',
                min: 0,
                max: maxNumOfMovie,
                interval: interval,
                axisLabel: {formatter: '{value}'}
            },
            {
                type: 'value',
                name: 'Points',
                min: 0,
                max: 10,
                interval: 9,
                axisLabel: {formatter: '{value} pts'}
            }
        ],
        series: [
            {
                name: 'Number of Movies',
                type: 'bar',
                data: numOfMoviesList
            },
            {
                name: 'Average Director Score',
                type: 'line',
                yAxisIndex: 1,
                data: avgDirectorScore
            },
            {
                name: 'Average Actor Score',
                type: 'line',
                yAxisIndex: 1,
                data: avg_actor_score_list
            },
            {
                name: 'Average Actress Score',
                type: 'line',
                yAxisIndex: 1,
                data: avg_actress_score_list
            }]

    };

    comparisonChart.setOption(option);
}

/**
 * Get the maximum value from a list of numbers.
 * @param numArray number array
 * @returns maximum value
 */
function getMaxOfArray(numArray) {
    var max = Math.max.apply(null, numArray) + 10;
    // making this better to fit in chart
    while (0 != max % 10) {
        max += 1;
    }
    return max;
}

window.onresize = function () {
    if (null != comparisonChart){
        comparisonChart.resize();
    }
}

function addNameToActor(idOfInput1, idOfInput2, idOfImage)
{
    var input1 = document.getElementById(idOfInput1);
    var input2 = document.getElementById(idOfInput2);

    if(0 == input1.value.length)
    {
        addName(idOfInput1, idOfImage);
    }
    else if(0 == input2.value.length)
    {
        addName(idOfInput2, idOfImage);
    }
}

function addNameToDirector(idOfInput, idOfImage)
{
    console.log("gakki!");

    var input = document.getElementById(idOfInput);

    if(0 == input.value.length)
    {
        addName(idOfInput, idOfImage);
    }
}

function addName(idOfInput, idOfImage)
{
    var input = document.getElementById(idOfInput);
    var name = document.getElementById(idOfImage).innerHTML;
    console.log(name);
    input.value = name.trim();
}
