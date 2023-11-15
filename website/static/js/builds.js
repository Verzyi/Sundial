function updateFormAction(event) {
    event.preventDefault();

    let selectedOption = document.getElementById("facilitySelectInput").value;

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

    let selectedOption = document.getElementById("facilitySelectInput").value;

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
const facilitySelectInput = document.getElementById("facilitySelectInput");
facilitySelectInput.addEventListener("change", updateFormAction);

// On page load, set the selected option in the facility dropdown from local storage (if available)
window.addEventListener("load", function () {
    const selectedFacility = localStorage.getItem("selectedFacility");
    if (selectedFacility) {
        facilitySelectInput.value = selectedFacility;
    }
});


function showBuildInfo(event) {
    // Check if the clicked element is inside a table row
    const row = event.target.closest("tr");
    if (!row) {
        return;
    }

    // Get the BuildIDInput from the first column (index 0) of the row
    const BuildIDInput = row.getElementsByTagName("td")[0].textContent.trim();
    // console.log("BuildID:", BuildIDInput);

    // Fetch additional build information and display it
    fetchBuildInfo(BuildIDInput);

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
// // Add event listeners for the build state checkboxes to show/hide the appropriate forms
// const buildSetupCheckbox = document.getElementById("buildSetupCheckbox");
// buildSetupCheckbox.addEventListener("change", function (event) {
//     // Stop the event from propagating to the row click event handler
//     event.stopPropagation();
//     // Call the showBuildInfo function
//     showBuildInfo(event);
// });

// const buildStartCheckbox = document.getElementById("buildStartCheckbox");
// buildStartCheckbox.addEventListener("change", function (event) {
//     // Stop the event from propagating to the row click event handler
//     event.stopPropagation();
//     // Call the showBuildInfo function
//     showBuildInfo(event);
// });

// const buildFinishCheckbox = document.getElementById("buildFinishCheckbox");
// buildFinishCheckbox.addEventListener("change", function (event) {
//     // Stop the event from propagating to the row click event handler
//     event.stopPropagation();
//     // Call the showBuildInfo function
//     showBuildInfo(event);
// });

function fetchBuildInfo(BuildIDInput) {
    fetch(`get_build_info/${BuildIDInput}`, {
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

            // Current Build Info
            const BuildIDDisplay = document.getElementById("BuildIDDisplay")
            BuildIDDisplay.textContent = data.BuildID

            // const BuildNameDisplay = document.getElementById("BuildNameDisplay")
            // BuildNameDisplay.textContent = data.BuildName

            const CreatedByInput = document.getElementById("CreatedByInput");
            CreatedByInput.textContent = data.CreatedBy;

            const CreatedOnInput = document.getElementById("CreatedOnInput");
            const datetimeString = data.CreatedOn;
            // Parse the datetime string into a Date object
            const datetime = new Date(datetimeString);
            // Format the date as "M D Y"
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            const formattedDate = datetime.toLocaleDateString('en-US', options);
            CreatedOnInput.textContent = formattedDate;

            // Build Setup Form
            const BuildIDInput = document.getElementById("BuildIDInput")
            BuildIDInput.value = data.BuildID

            const BuildNameInput = document.getElementById("BuildNameInput");
            BuildNameInput.value = data.BuildName;

            const MachineIDInput = document.getElementById("MachineIDInput");
            MachineIDInput.value = data.MachineID;

            const machineTableCell = document.getElementById("machineTableCell");

            if (data.Platform == "Velo 3D Sapphire") {
                // Do something specific for "Velo"
                console.log("Selected machine is Velo");
                // Get all elements with the class 'Velo'
                const veloElements = document.querySelectorAll('.Velo');
                // Loop through each element and show it
                veloElements.forEach(element => {
                    element.style.display = 'block';
                });
                // Get all elements with the class 'EOS'
                const eosElements = document.querySelectorAll('.EOS');
                // Loop through each element and hide it
                eosElements.forEach(element => {
                    element.style.display = 'none';
                });
            } else {
                // Get all elements with the class 'EOS'
                const eosElements = document.querySelectorAll('.EOS');

                // Loop through each element and show it
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
            // console.log(data.Platform); // Check if this is not null

            MachineIDInput.addEventListener("change", function () {
                if (MachineIDInput.value === "GA3") {
                    // Do something specific for "Velo"
                    console.log("Selected machine is Velo");
                    // Get all elements with the class 'Velo'
                    const veloElements = document.querySelectorAll('.Velo');
                    // Loop through each element and show it
                    veloElements.forEach(element => {
                        element.style.display = 'block';
                    });
                    // Get all elements with the class 'EOS'
                    const eosElements = document.querySelectorAll('.EOS');
                    // Loop through each element and hide it
                    eosElements.forEach(element => {
                        element.style.display = 'none';
                    });
                } else {
                    // Get all elements with the class 'EOS'
                    const eosElements = document.querySelectorAll('.EOS');
                    // Loop through each element and show it
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

            const AlloyNameInput = document.getElementById("AlloyNameInput");
            AlloyNameInput.value = data.AlloyName;

            const ScaleXInput = document.getElementById("ScaleXInput");
            ScaleXInput.value = data.ScaleX;

            const ScaleYInput = document.getElementById("ScaleYInput");
            ScaleYInput.value = data.ScaleY;

            const OffsetInput = document.getElementById("OffsetInput");
            OffsetInput.value = data.Offset;

            const LayerInput = document.getElementById("LayerInput");
            LayerInput.value = data.Layer;

            const PlateTemperatureInput = document.getElementById("PlateTemperatureInput");
            PlateTemperatureInput.value = data.PlateTemperature;

            const PotentialBuildHeightInput = document.getElementById("PotentialBuildHeightInput");
            PotentialBuildHeightInput.value = data.PotentialBuildHeight;

            const MinChargeAmountInput = document.getElementById("MinChargeAmountInput");
            MinChargeAmountInput.value = data.MinChargeAmount;

            const MaxChargeAmountInput = document.getElementById("MaxChargeAmountInput");
            MaxChargeAmountInput.value = data.MaxChargeAmount;

            const DosingBoostAmountInput = document.getElementById("DosingBoostAmountInput");
            DosingBoostAmountInput.value = data.DosingBoostAmount;

            const RecoaterSpeedInput = document.getElementById("RecoaterSpeedInput");
            RecoaterSpeedInput.value = data.RecoaterSpeed;

            const RecoaterTypeInput = document.getElementById("RecoaterTypeInput");
            RecoaterTypeInput.value = data.RecoaterType;

            const ParameterRevInput = document.getElementById("ParameterRevInput");
            // ParameterRevInput.textContent = data.ParameterRev;

            const ParameterRevDisplay = document.getElementById("ParameterRevDisplay")
            ParameterRevDisplay.value = data.ParameterRev

            // Build Start Form
            const BlendIDInput = document.getElementById("BlendIDInput");
            BlendIDInput.value = data.BlendID;

            const PlateSerialInput = document.getElementById("PlateSerialInput");
            PlateSerialInput.value = data.PlateSerial;

            const PlateThicknessInput = document.getElementById("PlateThicknessInput");
            PlateThicknessInput.value = data.PlateThickness;

            const PlateWeightInput = document.getElementById("PlateWeightInput");
            PlateWeightInput.value = data.PlateWeight;

            const FeedPowderHeightInput = document.getElementById("FeedPowderHeightInput");
            FeedPowderHeightInput.value = data.FeedPowderHeight;

            const InertTimeInput = document.getElementById("InertTimeInput");
            InertTimeInput.value = data.InertTime;

            const F9FilterSerialInput = document.getElementById("F9FilterSerialInput");
            F9FilterSerialInput.value = data.F9FilterSerial;

            const H13FilterSerialInput = document.getElementById("H13FilterSerialInput");
            H13FilterSerialInput.value = data.H13FilterSerial;

            const StartLaserHoursInput = document.getElementById("StartLaserHoursInput");
            StartLaserHoursInput.value = data.StartLaserHours;

            const BuildStartTimeInput = document.getElementById("BuildStartTimeInput");
            BuildStartTimeInput.value = data.BuildStartTime;
            
            // Build Finish Form
            const MaterialAddedInput = document.getElementById("MaterialAddedInput");
            MaterialAddedInput.value = data.MaterialAdded ? "True" : "False";

            const BuildFinishTimeInput = document.getElementById("BuildFinishTimeInput");
            BuildFinishTimeInput.value = data.BuildFinishTime;

            const BuildTimeInput = document.getElementById("BuildTimeInput");
            BuildTimeInput.value = data.BuildTime;

            const FinalLaserHoursInput = document.getElementById("FinalLaserHoursInput");
            FinalLaserHoursInput.value = data.FinalLaserHours;

            const FinishHeightInput = document.getElementById("FinishHeightInput");
            FinishHeightInput.value = data.FinishHeight;

            const EndPartPistonHeightInput = document.getElementById("EndPartPistonHeightInput");
            EndPartPistonHeightInput.value = data.EndPartPistonHeight;

            const EndFeedPowderHeightInput = document.getElementById("EndFeedPowderHeightInput");
            EndFeedPowderHeightInput.value = data.EndFeedPowderHeight;

            const BreakoutTimeInput = document.getElementById("BreakoutTimeInput");
            BreakoutTimeInput.value = data.BreakoutTime;

            const FinishPlateWeightInput = document.getElementById("FinishPlateWeightInput");
            FinishPlateWeightInput.value = data.FinishPlateWeight;

            const BuildInterruptsInput = document.getElementById("BuildInterruptsInput");
            BuildInterruptsInput.value = data.BuildInterrupts ? "True" : "False";

            // const measuredLaserPowerInput = document.getElementById("measuredLaserPowerInput");
            // measuredLaserPowerInput.value = data.MeasuredLaserPower;

            // const certificationBuildInput = document.getElementById("certificationBuildInput");
            // certificationBuildInput.value = data.CertificationBuild;

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

            // const buildHeightInput = document.getElementById("buildHeightInput"); 
            // buildHeightInput.value = data.BuildHeight;

            // const notesInput = document.getElementById("notesInput");
            // notesInput.value = data.Notes;

            // const filterLightInput = document.getElementById("filterLightInput");
            // filterLightInput.value = data.FilterLight;

            // const completedWithoutStoppageInput = document.getElementById("completedWithoutStoppageInput");
            // completedWithoutStoppageInput.value = data.CompletedWithoutStoppage;

            // Velo items 
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

            const PowderLevelInput = document.getElementById("PowderLevelInput");
            PowderLevelInput.value = data.PowderLevel;

            const SieveLifeInput = document.getElementById("SieveLifeInput");
            SieveLifeInput.value = data.SieveLife;

            const FilterPressureDrop = document.getElementById("FilterPressureDropInput");
            FilterPressureDrop.value = data.FilterPressureDrop;

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
        const BuildIDInput = buildRows[i].getElementsByTagName("td")[0];

        if (buildName && BuildIDInput) {
            const buildNameText = buildName.textContent || buildName.innerText;
            const buildIdText = BuildIDInput.textContent || BuildIDInput.innerText;

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

// function formatPlateSerial(input) {
//     // Remove all non-numeric characters
//     let rawInput = input.value.replace(/[^0-9]/g, '');

//     // Insert hyphens at appropriate positions
//     let formattedInput = '';
//     for (let i = 0; i < rawInput.length; i++) {
//         if (i === 2 || i === 4) {
//             formattedInput += '-';
//         }
//         formattedInput += rawInput.charAt(i);
//     }

//     input.value = formattedInput;
// }

function formatPlateSerial(input) {
    // Remove all non-numeric characters
    let rawInput = input.value.replace(/[^0-9]/g, '');

    // Ensure the raw input is not empty
    if (rawInput.length === 0) {
        input.value = '';
        return;
    }

    // Ensure raw input is at most 9 characters long
    rawInput = rawInput.substring(0, 9);

    // Insert hyphens at appropriate positions
    let formattedInput = rawInput.substring(0, 2) + '-' + rawInput.substring(2, 4) + '-' + rawInput.substring(4);
    
    input.value = formattedInput;
}
