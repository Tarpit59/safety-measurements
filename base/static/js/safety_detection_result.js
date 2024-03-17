document.addEventListener("DOMContentLoaded", function () {
  const unsafety_percentage = document.getElementById(
    "unsafety_percentage"
  ).innerHTML;
  const safety_percentage =
    document.getElementById("safety_percentage").innerHTML;

  const xValues = ["Safety Percentage", "Unsafety Percentage"];
  const yValues = [safety_percentage, unsafety_percentage];
  const barColors = ["#23a2f6", "#f09819"];

  new Chart("myChart", {
    type: "pie",
    data: {
      labels: xValues,
      datasets: [
        {
          backgroundColor: barColors,
          data: yValues,
        },
      ],
    },
  });
});
