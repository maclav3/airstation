Dygraph.onDOMready(function onDOMready() {
  var graphDefinitions = {
    temperature: {
        div: 'temperature',
        title: 'Temperature',
        ylabel: 'Temperature (C)',
        colors: ['#FF0000'],
        data: []
    },
    pressure: {
        div: 'pressure',
        title: 'Pressure',
        ylabel: 'Pressure (hPa)',
        colors: ['#0000FF'],
        data: []
    },
    humidity: {
        div: 'humidity',
        csvKey: 'relative_humidity',
        title: 'Relative Humidity',
        ylabel: 'Relative Humidity (%)',
        colors: ['#00FF00'],
        data: []
    },
    tvoc: {
        div: 'tvoc',
        title: 'TVOC',
        ylabel: 'TVOC (ppb)',
        colors: ['#FF00FF'],
        data: []
    },
    eco2: {
        div: 'eco2',
        csvKey: 'eCO2',
        title: 'eCO2',
        ylabel: 'eCO2 (ppm)',
        colors: ['#009999'],
        data: []
    },
    aqi: {
        div: 'aqi',
        title: 'AQI',
        ylabel: 'AQI',
        colors: ['#333300'],
        data: []
    }
  }

  var dataSeries = ['temperature', 'pressure', 'humidity', 'tvoc', 'eco2', 'aqi'];

  var plugins =

  renderGraphs = function() {
      var graphs = [];
      for (var i = 0; i < 6; i++) {
        var graphDefinition = graphDefinitions[dataSeries[i]];
        var div = document.getElementById(graphDefinition.div);
        graphs.push(new Dygraph(
          div,
          graphDefinition.data,
          {
            connectSeparatedPoints: false,
            gapSize: 1,
            drawGapEdgePoints: true,
            plugins: [
                new Dygraph.Plugins.Crosshair({
                  direction: "vertical"
                })
            ],
            title: graphDefinition.title,
            ylabel: graphDefinition.ylabel,
            xlabel: 'Time',
            labels: ['Time', graphDefinition.ylabel],
            colors: graphDefinition.colors,
            highlightCircleSize: 2,
            strokeWidth: 1,
            highlightSeriesOpts: {
                strokeWidth: 2,
                strokeBorderWidth: 1,
                highlightCircleSize: 3
            },
          }
        ));
      }

      Dygraph.synchronize(graphs, {
          range: false
      });
  };

  const max_time_between_points = 60 * 1000; // 60 seconds
  Papa.parse('./example-data.csv', {
    download: true,
    header: true,
    dynamicTyping: true,
    step: function(row) {
        for (var i = 0; i < 6; i++) {
            if (!row.data.timestamp) {
                continue;
            }
            var graph_def = graphDefinitions[dataSeries[i]];
            var t = new Date((row.data.timestamp + 946684800) * 1000);

            if (graph_def.data.length > 0) {
                var last_data = graph_def.data[graph_def.data.length - 1];
                var diff = t - last_data[0];
                if (diff > max_time_between_points) {
                    graph_def.data.push([new Date(t - diff), null]);
                }
            }

            var key = graph_def.csvKey || dataSeries[i];
            graph_def.data.push([t , row.data[key]]);
        }
    },
    complete: function(results) {
        renderGraphs();
    }
  });
});

