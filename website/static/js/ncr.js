function updateFormAction(event) {
    event.preventDefault();

    let selectedOption = document.getElementById("facilitySelectInput").value;

    if (!selectedOption) {
        return; // Don't submit the form if no facility is selected
    }

    let form = document.getElementById("facilityForm");
    let searchInput = document.getElementById("searchInput").value;

    form.action = "/NCRS";
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


function showNCRInfo(event) {
    // Check if the clicked element is inside a table row
    const row = event.target.closest("tr");
    if (!row) {
        return;
    }

    // Get the BuildIDInput from the first column (index 0) of the row
    const NCRInput = row.getElementsByTagName("td")[0].textContent.trim();


    // Fetch additional NCR information and display it
    fetchBuildInfo(NCRIDInput);

    // Show the appropriate form based on the selected build state
    const NCRState = event.target.name;
    // Add event listeners for the build state checkboxes to show/hide the appropriate forms
    // const buildSetupCheckbox = document.getElementById("buildSetupCheckbox");
    NCRCheckbox.addEventListener("change", function (event) {
        // Toggle the visibility of the buildSetupForm based on the checkbox state
        const buildSetupForm = document.getElementById("NCRSetupForm");
        buildSetupForm.style.display = event.target.checked ? "block" : "none";
    });
}
// Function to filter builds based on the search input
function filterNCRs() {
    const searchInput = document.getElementById("searchInput").value.toUpperCase();
    const ncrsTable = document.querySelector(".ncrsTable table");
    const ncrRows = ncrsTable.getElementsByTagName("tr");

    for (let i = 0; i < buildRows.length; i++) {
        const LocationInput = ncrRows[i].getElementsByTagName("td")[1];
        const NcrIDInput = ncrRows[i].getElementsByTagName("td")[0];

        if (LocationInput && NcrIDInput) {
            const LocationText = LocationText.textContent || LocationText.innerText;
            const NcrIdText = NcrIDInput.textContent || NcrIDInput.innerText;

            if (
                LocationText.toUpperCase().indexOf(searchInput) > -1 ||
                NcrIdText.toUpperCase().indexOf(searchInput) > -1
            ) {
                NcrRows[i].style.display = "";
            } else {
                NcrRows[i].style.display = "none";
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
                    const debouncedFilterNCRs = debounce(filterNCRs, 300);
                    searchInput.addEventListener("input", debouncedFilterNCRs);

                    // Function to show NCR information
                    function showNCRInfo(event) {
                        // Get the selected NCR row
                        const selectedRow = event.currentTarget;

                        // Get the NCR ID, created by, and created on
                        const ncrId = selectedRow.getElementsByTagName("td")[0].textContent;
                        const createdBy = selectedRow.getElementsByTagName("td")[1].textContent;
                        const createdOn = selectedRow.getElementsByTagName("td")[2].textContent;

                        // Update the NCR form fields with the selected NCR information
                        const ncrIdDisplay = document.getElementById("NCRIdDisplay");
                        const createdByInput = document.getElementById("createdByInput");
                        const createdOnInput = document.getElementById("createdOnInput");

                        ncrIdDisplay.textContent = ncrId;
                        createdByInput.textContent = createdBy;
                        createdOnInput.textContent = createdOn;
                    }

          