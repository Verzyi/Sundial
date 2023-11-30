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
        console.log("selectedFacility: ", selectedFacility);
        // Manually trigger the change event after setting the value
        // facilitySelectInput.dispatchEvent(new Event('change'));
        // populateSearchTable(); // Call the function to populate the table
    }
});

function showNCRInfo(event) {
    const row = event.target.closest("tr");
    const NcrIDInput = row.getElementsByTagName("td")[0].textContent.trim();
    fetchNcrInfo(NcrIDInput);
}


function fetchNcrInfo(NcrIDInput) {
    fetch(`get_NCR_info/${NcrIDInput}`, {
        method: "GET",
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not OK!");
                const NCRForm = document.getElementById("NCRForm");
                NCRForm.classList.add("hidden");
            }
            return response.json();
        })
        .then((data) => {
            console.log("Retrieved build data:", data);
            // Populate the rest of the form fields with the retrieved data

            // Show the NCRForm
            const NCRForm = document.getElementById("NCRForm");
            NCRForm.classList.remove("hidden");

            // Current Build Info
            const NCRIDDisplay = document.getElementById("NCRIdDisplay")
            NCRIDDisplay.textContent = data.NCRID

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

            const categoryInput = document.getElementById('CategoryInput');
            categoryInput.value = data.Category; // Assuming Category is retrieved from backend

            const descriptionInput = document.getElementById("DescriptionInput");
            descriptionInput.value = data.Description;

            const QuantityInput = document.getElementById("QuantityInput");
            QuantityInput.value = data.Quantity;

            // const attachmentInput = document.getElementById("AttachmentInput");
            // attachmentInput.value = data.Attachment;
        })
        .catch((error) => {
            console.error("Error fetching NCR info:", error);
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
const debouncedfilterNCRs = debounce(filterNCRs, 300);
searchInput.addEventListener("input", debouncedfilterNCRs);

