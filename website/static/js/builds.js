// Function to update the form action based on the selected facility
function updateFormAction(event) {
  let form = document.getElementById("facilityForm");
  let selectedOption = event.target.value;
  form.action = "/builds";
  form.method = "POST";
  let input = document.createElement("input");
  input.type = "hidden";
  input.name = "Facility";
  input.value = selectedOption;
  form.appendChild(input);
  form.submit();
}

// Function to show build info when a row in the table is clicked
function showBuildInfo(event) {
  const buildSetupForm = document.getElementById("buildSetupForm");
  const buildStartForm = document.getElementById("buildStartForm");
  const buildFinishForm = document.getElementById("buildFinishForm");
  const buildId = event.target.closest("tr").dataset.buildid;
  const buildName = event.target.closest("tr").dataset.buildname;

  // ...

  // Unhide the buttons when a row is clicked
  const controlButtons = document.getElementById("btn-group");
  controlButtons.style.display = "inline-flex"; // Change display to "inline-flex"

  // Show the appropriate form based on the selected build state
  const buildState = event.target.name;
  if (event.target.checked) {
    if (buildState === "buildState") {
      if (event.target.id === "buildSetupCheckbox") {
        buildSetupForm.style.display = "block";
        buildStartForm.style.display = "none";
        buildFinishForm.style.display = "none";
      } else if (event.target.id === "buildStartCheckbox") {
        buildSetupForm.style.display = "none";
        buildStartForm.style.display = "block";
        buildFinishForm.style.display = "none";
      } else if (event.target.id === "buildFinishCheckbox") {
        buildSetupForm.style.display = "none";
        buildStartForm.style.display = "none";
        buildFinishForm.style.display = "block";
      }
    }
  }
  
  // Show all buttons (remove the inline style attribute)
  const allButtons = document.querySelectorAll(".controlButtons button");
  allButtons.forEach(button => {
    button.style.display = "inline-flex";
  });

  // Populate forms with the selected build information
  const buildIdInput = document.getElementById("solidJobsBuildIDInput");
  const buildNameInput = document.getElementById("buildNameInput");
  const machineInput = document.getElementById("machineInput");
  const blendIDInput = document.getElementById("blendIDInput");
  const plateSerialInput = document.getElementById("plateSerialInput");
  const materialAddedInput = document.getElementById("materialAddedInput");
  const buildFinishInput = document.getElementById("buildFinishInput");

  buildIdInput.value = buildId;
  buildNameInput.value = buildName;
  // ... (populate other fields)

  // Fetch the additional build information from the server using the build ID
  fetch("/get_build_info", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ buildId: buildId }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Populate the rest of the form fields with the retrieved data
      blendIDInput.value = data.blendID;
      plateSerialInput.value = data.plateSerial;
      materialAddedInput.value = data.materialAdded;
      buildFinishInput.value = data.buildFinish;

      // Ensure the appropriate form is displayed based on the selected build state
      if (buildSetupCheckbox.checked) {
        buildSetupForm.style.display = "block";
        buildStartForm.style.display = "none";
        buildFinishForm.style.display = "none";
      } else if (buildStartCheckbox.checked) {
        buildSetupForm.style.display = "none";
        buildStartForm.style.display = "block";
        buildFinishForm.style.display = "none";
      } else if (buildFinishCheckbox.checked) {
        buildSetupForm.style.display = "none";
        buildStartForm.style.display = "none";
        buildFinishForm.style.display = "block";
      }
    });
}

// ...

// Function to filter builds based on the search input
function filterBuilds() {
  const searchInput = document.getElementById("searchInput").value.toUpperCase();
  const buildsTable = document.querySelector(".buildsTable table");
  const buildRows = buildsTable.getElementsByTagName("tr");

  for (let i = 0; i < buildRows.length; i++) {
    const buildName = buildRows[i].getElementsByTagName("td")[1];
    const buildId = buildRows[i].getElementsByTagName("td")[0];

    if (buildName && buildId) {
      const buildNameText = buildName.textContent || buildName.innerText;
      const buildIdText = buildId.textContent || buildId.innerText;

      if (
        buildNameText.toUpperCase().indexOf(searchInput) > -1 ||
        buildIdText.toUpperCase().indexOf(searchInput) > -1
      ) {
        buildRows[i].style.display = "";
        buildRows[i].classList.add("highlighted-row"); // Add a CSS class to highlight the row
      } else {
        buildRows[i].style.display = "none";
        buildRows[i].classList.remove("highlighted-row"); // Remove the CSS class to reset the row styling
      }
    }
  }
}

// Debounce function to limit the frequency of filter operations
function debounce(func, delay) {
  let timer;
  return function () {
    clearTimeout(timer);
    timer = setTimeout(func, delay);
  };
}

// Debounced filterBuilds function
const debouncedFilterBuilds = debounce(filterBuilds, 30);

// Retrieve the searchInput element
const searchInput = document.getElementById("searchInput");

// Event listener for input changes
searchInput.addEventListener("input", debouncedFilterBuilds);

// Add event listeners for the build state checkboxes to show/hide the appropriate forms
const buildSetupCheckbox = document.getElementById("buildSetupCheckbox");
buildSetupCheckbox.addEventListener("change", showBuildInfo);

const buildStartCheckbox = document.getElementById("buildStartCheckbox");
buildStartCheckbox.addEventListener("change", showBuildInfo);

const buildFinishCheckbox = document.getElementById("buildFinishCheckbox");
buildFinishCheckbox.addEventListener("change", showBuildInfo);

// Event listener for table rows
const buildRows = document.querySelectorAll(".buildsTable table tbody tr");
buildRows.forEach((row) => {
  row.addEventListener("click", function (event) {
    showBuildInfo(event);
  });
});
