document.addEventListener("DOMContentLoaded", () => {
  viewDetectionDelete();
});

function viewDetectionDelete() {
  let viewDetectionDelete = document.getElementsByClassName(
    "viewDetectionDelete"
  );

  for (let element of viewDetectionDelete) {
    element.addEventListener("click", async () => {
      let detection_id = element.getAttribute("data");
      let isLoaded = false;
      if (!isLoaded) {
        document.getElementById("preloader").style.display = "block";
      }
      const res = await fetch(`view-detection?detection_id=${detection_id}`, {
        method: "GET",
      })
        .then((data) => {
          isLoaded = true;
          return data.text();
        })
        .then((html) => {
          document.open();
          document.write(html);
          document.close();
        })
        .catch(() => {
          isLoaded = true;
        });

      if (isLoaded) {
        document.getElementById("preloader").style.display = "none";
      }
    });
  }
}
