const hideMe = function() {
    let x = ["search", "createBlend", "trace"];
    for (let i = 0; i < x.length; i++) {
        let element = document.getElementById(x[i]);
        if (element) {
            element.style.display = "none";
        }
    }
}

const showMe = function(test) {
    let x = test.id;
    let element = document.getElementById(x);
    if (element) {
        element.style.display = "block";
        element.style.visibility = "visible";
    }
}

const menu = function(x, y) {
    hideMe(x);
    showMe(y);
}


// function addBlendField() {
//     const blendFields = document.getElementById("blendFields");
//     const newBlendField = document.createElement("div");
//     newBlendField.classList.add("blendField");

//     const blendNumberInput = document.createElement("input");
//     blendNumberInput.type = "number";
//     blendNumberInput.classList.add("blendNumber");
//     blendNumberInput.name = "BlendNumber[]";
//     blendNumberInput.placeholder = "0";

//     const weightInput = document.createElement("input");
//     weightInput.type = "number";
//     weightInput.classList.add("weight");
//     weightInput.name = "weight[]";
//     weightInput.placeholder = "0";

//     newBlendField.appendChild(blendNumberInput);
//     newBlendField.appendChild(weightInput);
//     blendFields.appendChild(newBlendField);
// }

// function submitBlendForm() {
//     const blendNumbers = document.getElementsByClassName("blendNumber");
//     const weights = document.getElementsByClassName("weight");

//     let totalWeight = 0;
//     const numbers = [];
//     const weightValues = [];

//     for (let i = 0; i < blendNumbers.length; i++) {
//         const blendNumber = blendNumbers[i].value.trim();
//         const weight = weights[i].value.trim();

//         if (blendNumber && weight) {
//             numbers.push(blendNumber);
//             weightValues.push(weight);
//             totalWeight += parseFloat(weight);
//         }
//     }

//     document.getElementById("weightTotal").textContent = totalWeight;
//     document.getElementById("createButton").disabled = true;

//     // You can add code here to send the blend data to the server using AJAX or submit the form
//     // with the updated values. Make sure to handle the data on the server-side accordingly.
//     // For example:
//     // 1. Send an AJAX request to the server to save the blend data.
//     // 2. Submit the form programmatically with JavaScript to a specific route.

//     // Example AJAX request:
//     // const formData = new FormData();
//     // formData.append("blendNumbers", numbers);
//     // formData.append("weights", weightValues);
//     // ... (add other form data if needed)

//     // fetch("/save_blend", {
//     //     method: "POST",
//     //     body: formData
//     // })
//     // .then(response => response.json())
//     // .then(data => {
//     //     // Handle the response from the server
//     //     // ...
//     // })
//     // .catch(error => {
//     //     // Handle any errors
//     //     // ...
//     // });
// }
