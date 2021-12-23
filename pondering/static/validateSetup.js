function check() {
    const service = document.getElementById('service').value;
    const domainField = document.getElementById('optional-domain');
    const from = document.getElementById('efrom');
    const preview = document.getElementById('to');
    const subject = document.getElementById('subject');
    const keyword = document.getElementById('keyword');
    const body = document.getElementById('body');
    validService = validateService(service);
    if (validService && service == 'SMTP') {
        domainField.hidden = false;
    }
    else {
        domainField.hidden = true;
    }
}

function validateService(service) {
    return services.includes(service)
}
