function lookup(e) {
    e.preventDefault();
    console.log('Running lookupCompany.js');
    const userInput = e.target.value;
    const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrftoken);
    formData.append('company', userInput);
    console.log('Lookup event triggered.');
    fetch('http://localhost:8000/enumerate', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        const reader = response.body.getReader();
        console.log(reader.read());
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function publish(data) {
}
