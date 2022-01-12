console.log('Running setupEnumerate.js');
const url = 'http://localhost:8000/enumerate'
function lookup() {
    console.log('Lookup event triggered.');
    csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let userInput = document.getElementById('company').value;
    let instance = document.getElementById('instance').value;
    let formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrftoken);
    formData.append('instance', instance);
    formData.append('company', userInput);
    fetch(url, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        const reader = response.body.getReader();
        const data = reader.read();
        data.then(result => {
            update = Utf8ArrayToStr(result.value);
            const view = document.getElementById('result').innerHTML = update;
            updateCompanyQuery();
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function enumerate() {
    console.log('Enumerate event triggered.');
    let userInput = document.getElementById('company').value;
    let instance = document.getElementById('instance').value;
    let submit = document.getElementById('submit');
    let formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrftoken);
    formData.append('instance', instance); 
    formData.append('company', userInput);
    formData.append('accept', true);
    fetch(url, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        const reader = response.body.getReader();
        const data = reader.read();
        data.then(result => {
            update = Utf8ArrayToStr(result.value);
            const view = document.getElementById('result').innerHTML = update;
            submit.innerHTML = 'Save';
            submit.className = 'btn btn-primary float-right';
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function deleteName(button) {
    console.log('Delete name event triggered.');
    button.className = 'btn btn-danger m-1';
}

function retainName(button) {
    console.log('Delete name event refused.');
    button.className = 'btn btn-success m-1';
}

function excludeName(button) {
    console.log('Exclude name event triggered.');
    let formData = new FormData();
    let instance = document.getElementById('instance').value;
    formData.append('csrfmiddlewaretoken', csrftoken);
    formData.append('instance', instance)
    formData.append('exclude', button.innerHTML);
    fetch(url, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        const reader = response.body.getReader();
        const data = reader.read();
        data.then(result => {
            update = Utf8ArrayToStr(result.value);
            const view = document.getElementById('result').innerHTML = update;
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function Utf8ArrayToStr(array) {
    var out, i, len, c;
    var char2, char3;

    out = '';
    len = array.length;
    i = 0;
    while(i < len) {
        c = array[i++];
        switch(c >> 4) { 
            case 0: case 1: case 2: case 3: case 4: case 5: case 6: case 7:
                // 0xxxxxxx
                out += String.fromCharCode(c);
                break;
            case 12: case 13:
                // 110x xxxx   10xx xxxx
                char2 = array[i++];
                out += String.fromCharCode(((c & 0x1F) << 6) | (char2 & 0x3F));
                break;
            case 14:
                // 1110 xxxx  10xx xxxx  10xx xxxx
                char2 = array[i++];
                char3 = array[i++];
                out += String.fromCharCode(((c & 0x0F) << 12) | ((char2 & 0x3F) << 6) | ((char3 & 0x3F) << 0));
                break;
        }
    }
    return out;
}

async function updateCompanyQuery() {
    submit = document.getElementById('submit');
    while(!document.getElementById('name')) {
        submit.disabled = true;
        await new Promise(r => setTimeout(r, 1000));
    }
    submit.disabled = false;
}
