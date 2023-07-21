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
      const buildId = document.getElementById("BuildID")
      buildId.value = data.BuildIt

      const build_id = document.getElementById("BuildIt")
      build_id.textContent = data.BuildIt

      // Find the dropdown element
      const machineInput = document.getElementById("machineInput");

      // Iterate over the options and find the one with a matching value
      for (let i = 0; i < machineInput.options.length; i++) {
        if (machineInput.options[i].value === data.MachineID) {
          // Set the matched option as selected
          machineInput.options[i].selected = true;
          break; // Exit the loop since we found the match
        }
}

      const blendIDInput = document.getElementById("blendIDInput");
      blendIDInput.value = data.BlendID;

      const plateSerialInput = document.getElementById("plateSerialInput");
      plateSerialInput.value = data.PlateSerial;

      const materialAddedInput = document.getElementById("materialAddedInput");
      materialAddedInput.value = data.MaterialAdded;

      const buildFinishInput = document.getElementById("buildFinishInput");
      buildFinishInput.value = data.BuildFinish;

      const createdByInput = document.getElementById("createdByInput");
      createdByInput.textContent = data.CreatedBy;

      const createdOnInput = document.getElementById("createdOnInput");
      createdOnInput.textContent = data.CreatedOn;

      // const facilityNameInput = document.getElementById("facilityNameInput");
      // facilityNameInput.value = data.FacilityName;

      // const sjBuildInput = document.getElementById("sjBuildInput");
      // sjBuildInput.value = data.SJBuild;

      const materialInput = document.getElementById("materialInput");
      materialInput.value = data.Material;

      const buildNameInput = document.getElementById("buildNameInput");
      buildNameInput.value = data.BuildName;

      const platformWeightInput = document.getElementById("platformWeightInput");
      platformWeightInput.value = data.PlatformWeight;

      const layerInput = document.getElementById("layerInput");
      layerInput.value = data.Layer;

      // const heightInput = document.getElementById("heightInput"); //this is for part pistion height
      // heightInput.value = data.Height;

      const offsetInput = document.getElementById("offsetInput");
      offsetInput.value = data.Offset;

      const scaleXInput = document.getElementById("scaleXInput");
      scaleXInput.value = data.ScaleX;

      const scaleYInput = document.getElementById("scaleYInput");
      scaleYInput.value = data.ScaleY;

      // const noteInput = document.getElementById("noteInput");
      // noteInput.value = data.Note;

      const buildStartInput = document.getElementById("buildStartInput");
      buildStartInput.value = data.BuildStart;

      const buildTimeInput = document.getElementById("buildTimeInput");
      buildTimeInput.value = data.BuildTime;

      const finishHeightInput = document.getElementById("finishHeightInput");
      finishHeightInput.value = data.FinishHeight;

      const finishPlatformWeightInput = document.getElementById("finishPlatformWeightInput");
      finishPlatformWeightInput.value = data.FinishPlatformWeight;

      // const certificationBuildInput = document.getElementById("certificationBuildInput");
      // certificationBuildInput.value = data.CertificationBuild;

      const feedPowderHeightInput = document.getElementById("feedPowderHeightInput");
      feedPowderHeightInput.value = data.FeedPowderHeight;

      const endFeedPowderHeightInput = document.getElementById("endFeedPowderHeightInput");
      endFeedPowderHeightInput.value = data.EndFeedPowderHeight;

      const potentialBuildHeightInput = document.getElementById("potentialBuildHeightInput");
      potentialBuildHeightInput.value = data.PotentialBuildHeight;

      // const locationInput = document.getElementById("locationInput");
      // locationInput.value = data.Location;

      const plateThicknessInput = document.getElementById("plateThicknessInput");
      plateThicknessInput.value = data.PlateThickness;

      const minChargeAmountInput = document.getElementById("MinChargeAmountInput");
      minChargeAmountInput.value = data.MinChargeAmount;

      const maxChargeAmountInput = document.getElementById("MaxChangeAmountInput");
      maxChargeAmountInput.value = data.MaxChargeAmountInput;

      const dosingBoostAmountInput = document.getElementById("DosingBoostAmountInput");
      dosingBoostAmountInput.value = data.DosingBoostAmount;

      const recoaterSpeedInput = document.getElementById("RecoaterSpeedInput");
      recoaterSpeedInput.value = data.RecoaterSpeed;

      const parameterRevInput = document.getElementById("ParameterRevInput");
      parameterRevInput.value = data.ParameterRev;

      // const measuredLaserPowerInput = document.getElementById("measuredLaserPowerInput");
      // measuredLaserPowerInput.value = data.MeasuredLaserPower;

      // const gasFlowInput = document.getElementById("gasFlowInput");
      // gasFlowInput.value = data.GasFlow;

      // const initialDosingFactorInput = document.getElementById("initialDosingFactorInput");
      // initialDosingFactorInput.value = data.InitialDosingFactor;

      // const maxFinishHeightInput = document.getElementById("maxFinishHeightInput");
      // maxFinishHeightInput.value = data.MaxFinishHeight;

      // const maxBuildTimeInput = document.getElementById("maxBuildTimeInput");
      // maxBuildTimeInput.value = data.MaxBuildTime;

      // const maxDateDifferenceInput = document.getElementById("maxDateDifferenceInput");
      // maxDateDifferenceInput.value = data.MaxDateDifference;

      const platformTemperatureInput = document.getElementById("platformTemperatureInput");
      platformTemperatureInput.value = data.PlatformTemperature;

      const startLaserHoursInput = document.getElementById("startLaserHoursInput");
      startLaserHoursInput.value = data.StartLaserHours;

      const finalLaserHoursInput = document.getElementById("finalLaserHoursInput");
      finalLaserHoursInput.value = data.FinalLaserHours;

      const inertTimeInput = document.getElementById("inertTimeInput");
      inertTimeInput.value = data.InertTime;

      const f9FilterSerialInput = document.getElementById("f9FilterSerialInput");
      f9FilterSerialInput.value = data.F9FilterSerial;

      const h13FilterSerialInput = document.getElementById("h13FilterSerialInput");
      h13FilterSerialInput.value = data.H13FilterSerial;

      // const filterLightInput = document.getElementById("filterLightInput");
      // filterLightInput.value = data.FilterLight;

      const endPartPistonHeightInput = document.getElementById("endPartPistonHeightInput");
      endPartPistonHeightInput.value = data.EndPartPistonHeight;

      const breakoutInput = document.getElementById("breakoutInput");
      breakoutInput.value = data.Breakout;

      // const completedWithoutStoppageInput = document.getElementById("completedWithoutStoppageInput");
      // completedWithoutStoppageInput.value = data.CompletedWithoutStoppage;


      const buildInterruptsInput = document.getElementById("buildInterruptsInput");
      buildInterruptsInput.value = data.BuildInterrupts;

      const recoaterTypeInput = document.getElementById("recoaterTypeInput");
      recoaterTypeInput.value = data.RecoaterType;


      //here is all the velo items 
      /*
      const veloFlowSoftwareRevInput = document.getElementById("veloFlowSoftwareRevInput");
      veloFlowSoftwareRevInput.value = data.VeloFlowSoftwareRev;

      const veloFlowSoftwareBaseInput = document.getElementById("veloFlowSoftwareBaseInput");
      veloFlowSoftwareBaseInput.value = data.VeloFlowSoftwareBase;

      const veloFlowBuildTimeEstimationInput = document.getElementById("veloFlowBuildTimeEstimationInput");
      veloFlowBuildTimeEstimationInput.value = data.VeloFlowBuildTimeEstimation;

      const veloFlowActualBuildTimeInput = document.getElementById("veloFlowActualBuildTimeInput");
      veloFlowActualBuildTimeInput.value = data.VeloFlowActualBuildTime;

      const veloFlowDrainedPowderWeightInput = document.getElementById("veloFlowDrainedPowderWeightInput");
      veloFlowDrainedPowderWeightInput.value = data.VeloFlowDrainedPowderWeight;

      const veloFlowRealisedYieldInput = document.getElementById("veloFlowRealisedYieldInput");
      veloFlowRealisedYieldInput.value = data.VeloFlowRealisedYield;

      const veloFlowActualScanSpeedInput = document.getElementById("veloFlowActualScanSpeedInput");
      veloFlowActualScanSpeedInput.value = data.VeloFlowActualScanSpeed;

      const veloFlowActualHatchDistanceInput = document.getElementById("veloFlowActualHatchDistanceInput");
      veloFlowActualHatchDistanceInput.value = data.VeloFlowActualHatchDistance;

      const veloFlowActualAvgHatchDensityInput = document.getElementById("veloFlowActualAvgHatchDensityInput");
      veloFlowActualAvgHatchDensityInput.value = data.VeloFlowActualAvgHatchDensity;

      const veloFlowEstimatedScanSpeedInput = document.getElementById("veloFlowEstimatedScanSpeedInput");
      veloFlowEstimatedScanSpeedInput.value = data.VeloFlowEstimatedScanSpeed;

      const veloFlowEstimatedHatchDistanceInput = document.getElementById("veloFlowEstimatedHatchDistanceInput");
      veloFlowEstimatedHatchDistanceInput.value = data.VeloFlowEstimatedHatchDistance;

      const veloFlowEstimatedAvgHatchDensityInput = document.getElementById("veloFlowEstimatedAvgHatchDensityInput");
      veloFlowEstimatedAvgHatchDensityInput.value = data.VeloFlowEstimatedAvgHatchDensity;

      // Add code to populate any other fields not mentioned above
      */
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