function updateDatabase(selectedValue, inputName) {
    // Get the build ID from your HTML, you can modify this as per your HTML structure
    let buildId = document.getElementById('buildId').textContent;
    let machine = document.getElementById('machineIdInput').value;
    let material = document.getElementById('AlloyNameInput').value;

    // Prepare data to send in the AJAX request
    let data = {
        build_id: buildId,
        machine_id: machine,
        material_name: material
    };
    console.log(data);
    // Make an AJAX request to the Flask route
    fetch('/update_database', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Database updated successfully');
            // You can perform additional actions here if the update was successful
        } else {
            console.error('Error updating database:', data.message);
            // Handle error scenarios here
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle network or other errors here
    });
}