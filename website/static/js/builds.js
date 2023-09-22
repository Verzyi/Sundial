function updateFormAction(event) {
    event.preventDefault();

    let selectedOption = document.getElementById("facilitySelect").value;

    if (!selectedOption) {
        return; // Don't submit the form if no facility is selected
    }

    let form = document.getElementById("facilityForm");
    let searchInput = document.getElementById("searchInput").value;

    form.action = "/builds";
    form.method = "POST";

    let facilityInput = document.createElement("input");
    facilityInput.type = "hidden";
    facilityInput.name = "Facility";
    facilityInput.value = selectedOption;
    form.appendChild(facilityInput);

    let searchInputField = document.createElement("input");
    searchInputField.type = "hidden";
    searchInputField.name = "SearchInput";
    searchInputField.value = searchInput;
    form.appendChild(searchInputField);

    localStorage.setItem("selectedFacility", selectedOption);

    form.submit();
}

function populateSearchTable(data) {
    const tableBody = document.getElementById("searchTableBody");
    tableBody.innerHTML = ""; // Clear existing table rows

    let selectedOption = document.getElementById("facilitySelect").value;

    if (!selectedOption) {
        return; // Don't populate the table if no facility is selected
    }

    // Populate the table with data based on the selected facility
    for (let item of data) {
        let row = tableBody.insertRow();
        // Create and append table cells here...
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const logoutButton = document.getElementById("logOut");
    if (logoutButton) {
        logoutButton.addEventListener("click", function () {
            logout();
            // Perform any other logout-related actions
        });
    }
});

function logout() {
    // ... your logout logic here ...
    // Clear the selected facility from local storage
    localStorage.removeItem("selectedFacility");
}


// Add an event listener to the facility select dropdown
const facilitySelect = document.getElementById("facilitySelect");
facilitySelect.addEventListener("change", updateFormAction);

// On page load, set the selected option in the facility dropdown from local storage (if available)
window.addEventListener("load", function () {
    const selectedFacility = localStorage.getItem("selectedFacility");
    if (selectedFacility) {
        facilitySelect.value = selectedFacility;
    }
});


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
    // Add event listeners for the build state checkboxes to show/hide the appropriate forms
    // const buildSetupCheckbox = document.getElementById("buildSetupCheckbox");
    buildSetupCheckbox.addEventListener("change", function (event) {
        // Toggle the visibility of the buildSetupForm based on the checkbox state
        const buildSetupForm = document.getElementById("buildSetupForm");
        buildSetupForm.style.display = event.target.checked ? "block" : "none";
    });

    // const buildStartCheckbox = document.getElementById("buildStartCheckbox");
    buildStartCheckbox.addEventListener("change", function (event) {
        // Toggle the visibility of the buildStartForm based on the checkbox state
        const buildStartForm = document.getElementById("buildStartForm");
        buildStartForm.style.display = event.target.checked ? "block" : "none";
    });

    // const buildFinishCheckbox = document.getElementById("buildFinishCheckbox");
    buildFinishCheckbox.addEventListener("change", function (event) {
        // Toggle the visibility of the buildformFinshed based on the checkbox state
        const buildformFinshed = document.getElementById("buildformFinshed");
        buildformFinshed.style.display = event.target.checked ? "block" : "none";
    });
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
    fetch(`get_build_info/${buildId}`, {
        method: "GET",
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not OK!");
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


            const blendIDInput = document.getElementById("BlendIDInput");
            blendIDInput.value = data.BlendID;

            const plateSerialInput = document.getElementById("PlateSerialInput");
            plateSerialInput.value = data.PlateSerial;

            const buildFinishInput = document.getElementById("buildFinishInput");
            buildFinishInput.value = data.BuildFinish;

            const createdByInput = document.getElementById("createdByInput");
            createdByInput.textContent = data.CreatedBy;

            const createdOnInput = document.getElementById("createdOnInput");
            const datetimeString = data.CreatedOn;
            // Parse the datetime string into a Date object
            const datetime = new Date(datetimeString);

            // Format the date as "M D Y"
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            const formattedDate = datetime.toLocaleDateString('en-US', options);

            createdOnInput.textContent = formattedDate;

            const materialInput = document.getElementById("materialInput");
            materialInput.value = data.AlloyName;

            const machineInput = document.getElementById("machineInput");
            machineInput.value = data.MachineID;


            const machineTableCell = document.getElementById("machineTableCell");

            if (data.MachineID == "Velo") {
                // Do something specific for "Velo"
                console.log("Selected machine is Velo");
                // Get all elements with the class 'EOS'
                const eosElements = document.querySelectorAll('.EOS');
                // Loop through each element and hide it
                eosElements.forEach(element => {
                    element.style.display = 'none';
                });

                // Get all elements with the class 'Velo'
                const veloElements = document.querySelectorAll('.Velo');
                // Loop through each element and hide it
                veloElements.forEach(element => {
                    element.style.display = 'block';
                });


            } else {
                // Get all elements with the class 'EOS'
                const eosElements = document.querySelectorAll('.EOS');

                // Loop through each element and hide it
                eosElements.forEach(element => {
                    element.style.display = 'block';
                });
                // Get all elements with the class 'Velo'
                const veloElements = document.querySelectorAll('.Velo');
                // Loop through each element and hide it
                veloElements.forEach(element => {
                    element.style.display = 'none';
                });
            }

            console.log(data.MachineID); // Check if this is not null


            machineInput.addEventListener("change", function () {

                if (machineInput.value === "Velo") {
                    // Do something specific for "Velo"
                    console.log("Selected machine is Velo");
                    // Get all elements with the class 'EOS'
                    const eosElements = document.querySelectorAll('.EOS');
                    // Loop through each element and hide it
                    eosElements.forEach(element => {
                        element.style.display = 'none';
                    });

                    // Get all elements with the class 'Velo'
                    const veloElements = document.querySelectorAll('.Velo');
                    // Loop through each element and hide it
                    veloElements.forEach(element => {
                        element.style.display = 'block';
                    });


                } else {
                    // Get all elements with the class 'EOS'
                    const eosElements = document.querySelectorAll('.EOS');

                    // Loop through each element and hide it
                    eosElements.forEach(element => {
                        element.style.display = 'block';
                    });
                    // Get all elements with the class 'Velo'
                    const veloElements = document.querySelectorAll('.Velo');
                    // Loop through each element and hide it
                    veloElements.forEach(element => {
                        element.style.display = 'block';
                    });
                }
            });

            const buildNameInput = document.getElementById("buildNameInput");
            buildNameInput.value = data.BuildName;

            const plateWeightInput = document.getElementById("PlateWeightInput");
            plateWeightInput.value = data.PlateWeight;

            const layerInput = document.getElementById("LayerInput");
            layerInput.value = data.Layer;

            // const heightInput = document.getElementById("heightInput"); //this is for part pistion height
            // heightInput.value = data.Height;

            const offsetInput = document.getElementById("OffsetInput");
            offsetInput.value = data.Offset;

            const scaleXInput = document.getElementById("ScaleXInput");
            scaleXInput.value = data.ScaleX;

            const scaleYInput = document.getElementById("ScaleYInput");
            scaleYInput.value = data.ScaleY;

            // const noteInput = document.getElementById("noteInput");
            // noteInput.value = data.Note;

            const buildStartInput = document.getElementById("BuildStartInput");
            buildStartInput.value = data.BuildStart;

            const buildTimeInput = document.getElementById("BuildTimeInput");
            buildTimeInput.value = data.BuildTime;

            const finishHeightInput = document.getElementById("FinishHeightInput");
            finishHeightInput.value = data.FinishHeight;

            const finishPlateWeightInput = document.getElementById("FinishPlateWeightInput");
            finishPlateWeightInput.value = data.FinishPlateWeight;

            // const certificationBuildInput = document.getElementById("certificationBuildInput");
            // certificationBuildInput.value = data.CertificationBuild;

            const feedPowderHeightInput = document.getElementById("FeedPowderHeightInput");
            feedPowderHeightInput.value = data.FeedPowderHeight;

            const endFeedPowderHeightInput = document.getElementById("EndFeedPowderHeightInput");
            endFeedPowderHeightInput.value = data.EndFeedPowderHeight;

            const potentialBuildHeightInput = document.getElementById("PotentialBuildHeightInput");
            potentialBuildHeightInput.value = data.PotentialBuildHeight;

            const plateThicknessInput = document.getElementById("PlateThicknessInput");
            plateThicknessInput.value = data.PlateThickness;

            const minChargeAmountInput = document.getElementById("MinChargeAmountInput");
            minChargeAmountInput.value = data.MinChargeAmount;

            const maxChargeAmountInput = document.getElementById("MaxChargeAmountInput");
            maxChargeAmountInput.value = data.MaxChargeAmount;

            const dosingBoostAmountInput = document.getElementById("DosingBoostAmountInput");
            dosingBoostAmountInput.value = data.DosingBoostAmount;

            const recoaterSpeedInput = document.getElementById("RecoaterSpeedInput");
            recoaterSpeedInput.value = data.RecoaterSpeed;

            // const parameterRevInput = document.getElementById("ParameterRevInput");
            // parameterRevInput.value = data.ParameterRev;

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

            const plateTemperatureInput = document.getElementById("PlateTemperatureInput");
            plateTemperatureInput.value = data.PlateTemperature;

            const startLaserHoursInput = document.getElementById("StartLaserHoursInput");
            startLaserHoursInput.value = data.StartLaserHours;

            const finalLaserHoursInput = document.getElementById("FinalLaserHoursInput");
            finalLaserHoursInput.value = data.FinalLaserHours;

            const inertTimeInput = document.getElementById("InertTimeInput");
            inertTimeInput.value = data.InertTime;

            const f9FilterSerialInput = document.getElementById("F9FilterSerialInput");
            f9FilterSerialInput.value = data.F9FilterSerial;

            const h13FilterSerialInput = document.getElementById("H13FilterSerialInput");
            h13FilterSerialInput.value = data.H13FilterSerial;

            // const filterLightInput = document.getElementById("filterLightInput");
            // filterLightInput.value = data.FilterLight;

            const endPartPistonHeightInput = document.getElementById("EndPartPistonHeightInput");
            endPartPistonHeightInput.value = data.EndPartPistonHeight;

            const breakoutTimeInput = document.getElementById("BreakoutTimeInput");
            breakoutTimeInput.value = data.BreakoutTime;

            // const completedWithoutStoppageInput = document.getElementById("completedWithoutStoppageInput");
            // completedWithoutStoppageInput.value = data.CompletedWithoutStoppage;

            const materialAddedInput = document.getElementById("MaterialAddedInput");
            materialAddedInput.value = data.MaterialAdded;

            const buildInterruptsInput = document.getElementById("BuildInterruptsInput");
            buildInterruptsInput.value = data.BuildInterrupts;

            const recoaterTypeInput = document.getElementById("RecoaterTypeInput");
            recoaterTypeInput.value = data.RecoaterType;

            // Here is all the velo items 
            const inSpec = document.getElementById("InSpec");

            if (
                data.BeamStabilityTestPerformed == true &&
                data.LaserAlignmentTestPerformed == true &&
                data.ThermalSensorTest == true &&
                data.LaserFocus == true
                ) {
                inSpec.value = true; // Assign the boolean value true
            } else {
                inSpec.value = false; // Assign the boolean value false
            }

            const powderLevel = document.getElementById("PowderLevelInput");
            powderLevel.value = data.PowderLevel;

            const sieveLife = document.getElementById("SieveLifeInput");
            sieveLife.value = data.SieveLife;

            const filterPressure = document.getElementById("FilterPressureInput");
            filterPressure.value = data.FilterPressureDrop;

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

function formatPlateSerial(input) {
    // Remove all non-numeric characters
    let rawInput = input.value.replace(/[^0-9]/g, '');

    // Insert hyphens at appropriate positions
    let formattedInput = '';
    for (let i = 0; i < rawInput.length; i++) {
        if (i === 2 || i === 4) {
            formattedInput += '-';
        }
        formattedInput += rawInput.charAt(i);
    }

    input.value = formattedInput;
}
