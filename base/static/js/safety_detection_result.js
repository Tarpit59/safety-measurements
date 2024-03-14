document.addEventListener("DOMContentLoaded", function () {
  const unsafety_percentage = document.getElementById(
    "unsafety_percentage"
  ).innerHTML;
  const safety_percentage =
    document.getElementById("safety_percentage").innerHTML;

  google.charts.load("current", { packages: ["corechart"] });
  google.charts.setOnLoadCallback(drawChart);

  function drawChart() {
    const data = google.visualization.arrayToDataTable([
      ["Result", "Percentage"],
      ["Safety", parseFloat(safety_percentage)],
      ["Unsafety", parseFloat(unsafety_percentage)],
    ]);

    const options = {
      backgroundColor: "transparent",
      fontColor: "#fff",
      width: 550, 
      height: 300,
      legend: {
        textStyle: {
          color: "#fff",
          fontSize: 18
        },
      },
      pieSliceTextStyle: {
        color: "#fff",
        fontSize: 16
      },
    };

    const chart = new google.visualization.PieChart(
      document.getElementById("myChart")
    );
    chart.draw(data, options);
  }
});
