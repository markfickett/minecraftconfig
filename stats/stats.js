/**
 * Renders time-series data for Minecraft user logins and for server machine
 * temperatures, using Dygraph; and renders day/time heatmaps of when users
 * are most often (or recently) logged in, using D3.
 */

// Constants for layout, colors, labels.
var margin = { top: 50, right: 0, bottom: 100, left: 30 },
    width = 960 - margin.left - margin.right,
    height = 430 - margin.top - margin.bottom,
    gridSize = Math.floor(width / 24),
    legendElementWidth = gridSize*2,
    buckets = 9,
    // alternatively colorbrewer.YlGnBu[9]
    colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4",
              "#1d91c0","#225ea8","#253494","#081d58"],
    days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    times = [
        "1a", "2a", "3a", "4a", "5a", "6a",
        "7a", "8a", "9a", "10a", "11a", "12a",
        "1p", "2p", "3p", "4p", "5p", "6p",
        "7p", "8p", "9p", "10p", "11p", "12p"];

function filterData(d) {
  return {
    day: +d.day,
    // convert UTC => EDT, +(24-4) mods easier than -4
    hour: (+d.hour + 20) % 24,
    probability: +d.probability * 100,
    population: +d.population
  };
}

function onDataLoaded(parentElementId, error, data) {
  var colorScale = d3.scale.quantile()
      .domain([0, buckets - 1, d3.max(
          data, function (d) { return d.probability; })])
      .range(colors);

  var svg = d3.select(parentElementId).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

  var dayLabels = svg.selectAll(".dayLabel")
      .data(days)
      .enter().append("text")
        .text(function (d) { return d; })
        .attr("x", 0)
        .attr("y", function (d, i) { return i * gridSize; })
        .style("text-anchor", "end")
        .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
        .attr("class", function (d, i) {
            return ((i >= 0 && i <= 4) ?
                "dayLabel mono axis axis-workweek" :
                "dayLabel mono axis"); });

  var timeLabels = svg.selectAll(".timeLabel")
      .data(times)
      .enter().append("text")
        .text(function(d) { return d; })
        .attr("x", function(d, i) { return i * gridSize; })
        .attr("y", 0)
        .style("text-anchor", "middle")
        .attr("transform", "translate(" + gridSize / 2 + ", -6)")
        .attr("class", function(d, i) {
            return ((i >= 7 && i <= 16) ?
                "timeLabel mono axis axis-worktime" :
                "timeLabel mono axis"); });

  var heatMap = svg.selectAll(".hour")
      .data(data)
      .enter().append("circle")
      .attr("cx", function(d) { return (d.hour + 0.5) * gridSize; })
      .attr("cy", function(d) { return (d.day + 0.5) * gridSize; })
      .attr("class", "hour bordered" )
      .attr("r", function(d) {
          return gridSize * (d.population) / 4.0; })
      .style("fill", colors[0]);

  heatMap.transition().duration(1000)
      .style("fill", function(d) { return colorScale(d.probability); });

  heatMap.append("title").text(function(d) { return d.value; });

  var legend = svg.selectAll(".legend")
      .data([0].concat(
          colorScale.quantiles()), function(d) { return d; })
      .enter().append("g")
      .attr("class", "legend");

  legend.append("rect")
    .attr("x", function(d, i) { return legendElementWidth * i; })
    .attr("y", height)
    .attr("width", legendElementWidth)
    .attr("height", gridSize / 2)
    .style("fill", function(d, i) { return colors[i]; });

  legend.append("text")
    .attr("class", "mono")
    .text(function(d) { return "" + Math.round(d); })
    .attr("x", function(d, i) { return legendElementWidth * i; })
    .attr("y", height + gridSize);
}

function loadHourDayChart(csvFile, parentElementId) {
  d3.csv(
      csvFile,
      filterData,
      onDataLoaded.bind(undefined, parentElementId));
}

/* Dygraph rendering for time-series temperature / login history. */

var graphs = [];
function renderDygraphs() {
  graphs.push(new Dygraph(
    document.getElementById("temperatures"),
    "temperatures.csv",
    {
      'height': 400,
      'width': 1000,
      'ylabel': 'Internal Temperatures (C)',
      'colors': [
        '#0A0', '#3A0', '#0A3', '#3A3', '#5A0', /* CPU cores */
        '#389', /* PCI */
        '#F94', '#E74', '#E36', /* drives */
      ],
    }));
  graphs.push(new Dygraph(
    document.getElementById("crafters"),
    "crafters-simplified.csv",
    {
      'height': 200,
      'width': 1000,
      'ylabel': 'Logged-In Players: Naib'
    }));
  graphs.push(new Dygraph(
    document.getElementById("upcrafters"),
    "upcrafters-simplified.csv",
    {
      'height': 200,
      'width': 1000,
      'ylabel': 'Logged-In Players: UP'
    }));
  var sync = Dygraph.synchronize(graphs, {'range': false});
}
