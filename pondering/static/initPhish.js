let form = document.getElementById("form");
form.addEventListener("input", check);
window.onload = (event) => {check()};
let ping = new Ping();
let lag
