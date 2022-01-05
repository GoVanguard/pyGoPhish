console.log('Running initEnumerate.js');
let input = document.getElementById('company');
input.addEventListener('input', lookup);
let button = document.getElementById('submit');
button.addEventListener('click', enumerate);
console.log(input);
enumeration = ['LI2U', 'GRIO', 'GOVN'];
if(document.getElementById('company').value != '') {
    lookup();
}
