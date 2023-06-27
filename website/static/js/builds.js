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
  
        if (buildNameText.toUpperCase().indexOf(searchInput) > -1 || buildIdText.toUpperCase().indexOf(searchInput) > -1) {
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
  
  // Debounced filterBuilds function
  const debouncedFilterBuilds = debounce(filterBuilds, 30);
  
  // Event listener for input changes
  searchInput.addEventListener('input', debouncedFilterBuilds);
  