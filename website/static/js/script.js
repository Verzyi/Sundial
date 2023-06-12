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

