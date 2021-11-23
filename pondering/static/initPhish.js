let form = document.getElementById("form");
form.addEventListener("input", check);
let ping = new Ping();
window.onload = (event) => {check()};
