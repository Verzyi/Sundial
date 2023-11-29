function updateFormAction(event) {
    event.preventDefault();

    let selectedOption = document.getElementById("facilitySelectInput").value;

    if (!selectedOption) {
        console.log("No facility selected");
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

    // Get the NcrIDInput from the first column (index 0) of the row
    const NCRIDInput = row.getElementsByTagName("td")[0].textContent.trim();


    // Fetch additional NCR information and display it
    fetchNCRInfo(NCRIDInput);

    NCRCheckbox.addEventListener("change", function (event) {
        // Toggle the visibility of the ncrForm based on the checkbox state
        const ncrForm = document.getElementById("NCRForm");
        ncrForm.style.display = event.target.checked ? "block" : "none";
    });
}
// Function to show NCR information
function showNCRInfo(event) {
    const row = event.currentTarget;
    const ncrId = row.dataset.ncrId; // Retrieve the NCR ID from the clicked row's data attribute

    fetchNCRInfo(ncrId); // Call the function to fetch NCR information based on the ID
    // Additional operations you want to perform after fetching the info...
}

// Function to fetch NCR information
function fetchNCRInfo(ncrId) {
    fetch(`/get_NCR_info/${ncrId}`, {
        method: 'GET',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not OK!');
        }
        return response.json();
    })
    .then(data => {
        console.log('Retrieved NCR data:', data);
        // Handle the retrieved NCR data as needed
        
        // Example: Update the UI with the retrieved data
        const NCRIDDisplay = document.getElementById('NCRIdDisplay');
        NCRIDDisplay.textContent = data.NCRID;

        const createdByInput = document.getElementById('createdByInput');
        createdByInput.textContent = data.CreatedBy;

        // ... Update other elements with the fetched data
    })
    .catch(error => {
        console.error('Error fetching NCR info:', error);
        // Handle errors, show error messages, etc.
    });
}


// Function to filter builds based on the search input
function filterNCRs() {
    const searchInput = document.getElementById("searchInput").value.toUpperCase();
    const ncrsTable = document.querySelector(".NCRsTable table");
    const ncrRows = ncrsTable.getElementsByTagName("tr");

    for (let i = 0; i < ncrRows.length; i++) {
        const ncrWorkOrder = ncrRows[i].getElementsByTagName("td")[1];
        const NcrIDInput = ncrRows[i].getElementsByTagName("td")[0];

        if (ncrWorkOrder && NcrIDInput) {
            const ncrWorkOrderText = ncrWorkOrder.textContent || ncrWorkOrder.innerText;
            const ncrIdText = NcrIDInput.textContent || NcrIDInput.innerText;

            if (
                ncrWorkOrderText.toUpperCase().indexOf(searchInput) > -1 ||
                ncrIdText.toUpperCase().indexOf(searchInput) > -1
            ) {
                ncrRows[i].style.display = "";
            } else {
                ncrRows[i].style.display = "none";
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
                        const selectedRow = event.currentTarget;
                        const ncrId = selectedRow.getElementsByTagName("td")[0].textContent;
                        const createdBy = selectedRow.getElementsByTagName("td")[1].textContent;
                        // const createdOn = selectedRow.getElementsByTagName("td")[2].textContent;
                    
                        const ncrIdDisplay = document.getElementById("NCRIdDisplay");
                        const createdByInput = document.getElementById("createdByInput");
                        // const createdOnInput = document.getElementById("createdOnInput");
                    
                        ncrIdDisplay.textContent = ncrId;
                        createdByInput.textContent = createdBy;
                        // createdOnInput.textContent = createdOn;
                    }
                    