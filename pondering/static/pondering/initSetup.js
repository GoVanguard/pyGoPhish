console.log('Running initSetup.js');
let form = document.getElementById("form");
form.addEventListener("input", check);
window.onload = (event) => {check()};
services = ['SMTP', 'GRPH', 'O365']
