// Function to fetch tasks from the Flask API
async function fetchTasks() {
    try {
        const response = await fetch('/tasks'); // Assuming your Flask API is hosted on the same domain
        if (response.ok) {
            const tasks = await response.json();
            return tasks; // Return the fetched tasks data
        } else {
            console.error('Failed to fetch tasks:', response.status);
            return []; // Return an empty array in case of error
        }
    } catch (error) {
        console.error('Error fetching tasks:', error);
        return []; // Return an empty array in case of error
    }
}


document.addEventListener('DOMContentLoaded', async function() {
    const allTasks = await fetchTasks(); // Wait for tasks to be fetched before proceeding

    console.log('Fetched tasks:', allTasks); // Log the fetched tasks to the console

    if (!Array.isArray(allTasks)) {
        console.error('Invalid tasks data:', allTasks);
        return;
    }
    

    class Task {
        constructor(buildID, alloyName, machineID, buildStart, buildTime) {
            this.buildID = buildID;
            this.alloyName = alloyName;
            this.machineID = machineID;
            this.buildStart = buildStart;
            this.buildTime = buildTime;
        }

        static sortTasks(tasks) {
            // Sort tasks by MachineID, BuildStart, BuildTime, and BuildID
            tasks.sort((a, b) => {
                if (a.machineID !== b.machineID) {
                    return a.machineID - b.machineID;
                }
                if (a.buildStart !== b.buildStart) {
                    return a.buildStart - b.buildStart;
                }
                if (a.buildTime !== b.buildTime) {
                    return a.buildTime - b.buildTime;
                }
                return a.buildID - b.buildID;
            });
            return tasks;
        }
    }

    // Create instances of the Task class
    const tasks = allTasks.map(task =>
        new Task(task.BuildID, task.AlloyName, task.MachineID, task.BuildStart, task.BuildTime)
    );

    // Sort tasks
    const sortedTasks = Task.sortTasks(tasks);

    // Group tasks by machine ID
    const tasksByMachine = {};
    sortedTasks.forEach(task => {
        if (!(task.machineID in tasksByMachine)) {
            tasksByMachine[task.machineID] = [];
        }
        tasksByMachine[task.machineID].push(task);
    });

    

  // Print tasks separated by machines to console.log
  console.log(tasksByMachine);

  const container = document.getElementById('tasks-container');

    for (const machineID in tasksByMachine) {
        const machineTasks = tasksByMachine[machineID];

        const machineDiv = document.createElement('div');
        machineDiv.classList.add('machine-row');

        // Display machine number
        const machineNumber = document.createElement('div');
        machineNumber.classList.add('machine-number');
        machineNumber.textContent = `${machineID}`;
        machineDiv.appendChild(machineNumber);

        // Display tasks for this machine
        machineTasks.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.classList.add('task');
            taskDiv.textContent = `Task: ${task.buildID}, Time: ${task.buildTime || 'null'}`;
            machineDiv.appendChild(taskDiv);
        });

        container.appendChild(machineDiv);
    }
});


function updateDatabase(selectedValue, inputName) {
    // Get the build ID from your HTML, you can modify this as per your HTML structure
    let buildId = document.getElementById('buildId').textContent;
    let machine = document.getElementById('machineIdInput').value;
    let material = document.getElementById('AlloyNameInput').value;
    let buildTime = document.getElementById('buildTime').value;

    // Prepare data to send in the AJAX request
    let data = {
        build_id: buildId,
        machine_id: machine,
        material_name: material,
        build_time: buildTime
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



