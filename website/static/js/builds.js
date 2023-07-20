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
  // Check if event.target is null or if it's not a checkbox
  if (!event.target || event.target.type !== "checkbox") {
    return;
  }

  // Get the closest ancestor tr element
  const trElement = event.target.closest("tr");

  // Check if the trElement exists and has the dataset attribute
  if (!trElement || !trElement.dataset) {
    return;
  }

  const buildSetupForm = document.getElementById("buildSetupForm");
  const buildStartForm = document.getElementById("buildStartForm");
  const buildFinishForm = document.getElementById("buildFinishForm");

  // Get the buildId and buildName from the dataset
  const buildId = trElement.dataset.buildid;
  const buildName = trElement.dataset.buildname;



  // Unhide the buttons when a row is clicked
  const controlButtons = document.getElementById("btn-group");
  controlButtons.style.display = "flex"; // Change display to "flex"
  controlButtons.style.alignItems = "center"; // Vertically center the content inside the buttons

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
  } else {
    // If none of the checkboxes are selected, hide all forms
    buildSetupForm.style.display = "none";
    buildStartForm.style.display = "none";
    buildFinishForm.style.display = "none";
  }

  // Populate forms with the selected build information
  const buildIdInput = document.getElementById("solidJobsBuildIDInput");
  const buildNameInput = document.getElementById("buildNameInput");

  buildIdInput.value = buildId;
  buildNameInput.value = buildName;

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
      // Update the input element IDs and properties based on your form structure
      // For example:
      const machineInput = document.getElementById("machineInput");
      machineInput.value = data.machine;

      const blendIDInput = document.getElementById("blendIDInput");
      blendIDInput.value = data.blendID;

      const plateSerialInput = document.getElementById("plateSerialInput");
      plateSerialInput.value = data.plateSerial;

      const materialAddedInput = document.getElementById("materialAddedInput");
      materialAddedInput.value = data.materialAdded;

      const buildFinishInput = document.getElementById("buildFinishInput");
      buildFinishInput.value = data.buildFinish;
    });
}


// Function to filter builds based on the search input and sort in descending order
function filterBuilds() {
  const searchInput = document.getElementById("searchInput").value.toUpperCase();
  const buildsTable = document.querySelector(".buildsTable table");
  const buildRows = buildsTable.getElementsByTagName("tr");

  // Convert buildRows to an array for easier sorting
  const buildRowsArray = Array.from(buildRows);

  // Sort the rows in descending order
  buildRowsArray.sort((a, b) => {
    const buildNameA = a.getElementsByTagName("td")[1].textContent.toUpperCase();
    const buildNameB = b.getElementsByTagName("td")[1].textContent.toUpperCase();
    return buildNameB.localeCompare(buildNameA); // For descending order
  });

  // Append sorted rows back to the table
  buildRowsArray.forEach(row => {
    buildsTable.appendChild(row);
  });

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

// Retrieve the searchInput element
const searchInput = document.getElementById("searchInput");

// Event listener for input changes
const debouncedFilterBuilds = debounce(filterBuilds, 300);
searchInput.addEventListener("input", debouncedFilterBuilds);

// Add event listeners for the build state checkboxes to show/hide the appropriate forms
const buildSetupCheckbox = document.getElementById("buildSetupCheckbox");
buildSetupCheckbox.addEventListener("change", showBuildInfo);

const buildStartCheckbox = document.getElementById("buildStartCheckbox");
buildStartCheckbox.addEventListener("change", showBuildInfo);

const buildFinishCheckbox = document.getElementById("buildFinishCheckbox");
buildFinishCheckbox.addEventListener("change", showBuildInfo);


// Hide all checkboxes initially
const allChecks = document.querySelectorAll(".build-state-buttons input[type='checkbox']");
allChecks.forEach(checkbox => {
  checkbox.style.display = "none";
});

// Show checkboxes and labels when a build is selected
const buildRows = document.querySelectorAll(".buildsTable table tbody tr");
buildRows.forEach((row) => {
  row.addEventListener("click", function (event) {
    // Show all checkboxes
    allChecks.forEach(checkbox => {
      checkbox.style.display = "inline-block";
    });

// Show all labels for checkboxes
const allLabels = document.querySelectorAll(".build-state-buttons label");
allLabels.forEach(label => {
  label.style.display = "inline-flex";
  label.style.alignItems = "center"; // Center align the content vertically
  label.style.justifyContent = "center"; // Center align the content horizontally
});

// Show all buttons
const allButtons = document.querySelectorAll(".controlButtons button");
allButtons.forEach(button => {
  button.style.display = "inline-flex";
  button.style.alignItems = "center"; // Center align the content vertically
  button.style.justifyContent = "center"; // Center align the content horizontally
});


    showBuildInfo(event);
  });
});
