function hiddenForm() {
    var p = document.createElement("p")
    var text = document.createTextNode("Training...");

    p.appendChild(text);
    p.setAttribute("id", "msgTraining");

    document.querySelector("main").appendChild(p);

    document.getElementById("config").style.display = "none";
};