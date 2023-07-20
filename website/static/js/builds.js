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

function showBuildInfo(event) {
  // Check if the clicked element is inside a table row
  const row = event.target.closest("tr");
  if (!row) {
    return;
  }

  // Get the buildId from the first column (index 0) of the row
  const buildId = row.getElementsByTagName("td")[0].textContent.trim();
  console.log("Build ID:", buildId);

  // Fetch additional build information and display it
  fetchBuildInfo(buildId);

  // Show the appropriate form based on the selected build state
  const buildState = event.target.name;
  const buildSetupForm = document.getElementById("buildSetupForm");
  const buildStartForm = document.getElementById("buildStartForm");
  const buildFinishForm = document.getElementById("buildFinishForm");

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
    // If the checkbox is unchecked, hide the corresponding form
    if (event.target.id === "buildSetupCheckbox") {
      buildSetupForm.style.display = "none";
    } else if (event.target.id === "buildStartCheckbox") {
      buildStartForm.style.display = "none";
    } else if (event.target.id === "buildFinishCheckbox") {
      buildFinishForm.style.display = "none";
    }
  }
}

// Add event listeners for the build state checkboxes to show/hide the appropriate forms
const buildSetupCheckbox = document.getElementById("buildSetupCheckbox");
buildSetupCheckbox.addEventListener("change", function (event) {
  // Stop the event from propagating to the row click event handler
  event.stopPropagation();
  // Call the showBuildInfo function
  showBuildInfo(event);
});

const buildStartCheckbox = document.getElementById("buildStartCheckbox");
buildStartCheckbox.addEventListener("change", function (event) {
  // Stop the event from propagating to the row click event handler
  event.stopPropagation();
  // Call the showBuildInfo function
  showBuildInfo(event);
});

const buildFinishCheckbox = document.getElementById("buildFinishCheckbox");
buildFinishCheckbox.addEventListener("change", function (event) {
  // Stop the event from propagating to the row click event handler
  event.stopPropagation();
  // Call the showBuildInfo function
  showBuildInfo(event);
});

// Function to fetch and display additional build information
function fetchBuildInfo(buildId) {
  fetch(`/get_build_info/${buildId}`, {
    method: "GET",
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Retrieved build data:", data);

      // Populate the rest of the form fields with the retrieved data
      const machineInput = document.getElementById("machineInput");
      machineInput.value = data.MachineID;

      const blendIDInput = document.getElementById("blendIDInput");
      blendIDInput.value = data.BlendID;

      const plateSerialInput = document.getElementById("plateSerialInput");
      plateSerialInput.value = data.PlateSerial;

      const materialAddedInput = document.getElementById("materialAddedInput");
      materialAddedInput.value = data.MaterialAdded;

      const buildFinishInput = document.getElementById("buildFinishInput");
      buildFinishInput.value = data.BuildFinish;
    })
    .catch((error) => {
      console.error("Error fetching build info:", error);
    });
}

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
      } else {
        buildRows[i].style.display = "none";
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
      checkbox.style.alignItems = "center";
      checkbox.style.justifyContent = "center";
    });

    // Show all labels for checkboxes
    const allLabels = document.querySelectorAll(".build-state-buttons label");
    allLabels.forEach(label => {
      label.style.display = "inline-flex";
      label.style.alignItems = "center";
      label.style.justifyContent = "center";
    });

    // Show all buttons
    const allButtons = document.querySelectorAll(".controlButtons button");
    allButtons.forEach(button => {
      button.style.display = "inline-flex";
      button.style.alignItems = "center";
      button.style.justifyContent = "center";
    });

    showBuildInfo(event);
  });
});