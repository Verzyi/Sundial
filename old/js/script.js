const hideMe = function hideMe(){
    
    let x=["search","creatBlend","addBlend","trace"];
    for (let i = 0; i < x.length; i++) {
        console.log(x[i]);
        document.getElementById(x[i]).style.display = "none"; 
        // document.getElementById(x).style.visibility = "hidden";
    } 
    // document.getElementById("trace").style.display = "none";
}


const showMe = function showMe(test){
    let x =test.id;
    console.log(x);

    document.getElementById(x).style.display = "block"; 
    document.getElementById(x).style.visibility = "visible"; 
}

const menu = function menu(x,y){
hideMe(x)
showMe(y)
}