document.addEventListener("DOMContentLoaded", () => {
  viewDetectionDelete();
  viewPopup();
});

function viewDetectionDelete() {
  let viewDetectionDelete = document.getElementsByClassName(
    "viewDetectionDelete"
  );

  for (let element of viewDetectionDelete) {
    element.addEventListener("click", async () => {
      if (confirm("Are you sure?")) {
        let detection_id = element.getAttribute("data");
        let isLoaded = false;
        if (!isLoaded) {
          document.getElementById("preloader").style.display = "block";
        }
        await fetch(`view-detection?detection_id=${detection_id}`, {
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
      }
    });
  }
}

function viewPopup() {
  let view = document.getElementsByClassName("view");

  for (let element of view) {
    element.addEventListener("click", async () => {
      let detection_stats = JSON.parse(element.getAttribute("data"));

      let popupData = document.getElementById("popup-data");
      let popupContainer = document.getElementById("popup-container");

      document.getElementById(
        "popup-heading"
      ).innerHTML = `${detection_stats.type.toUpperCase()} Statstics`;
      popupContainer.style.display = "flex";
      popupContainer.style.alignItems = "center";
      popupContainer.style.justifyContent = "center";
    });
  }
}

function closePopup() {
  document.getElementById("popup-container").style.display = "none";
}
