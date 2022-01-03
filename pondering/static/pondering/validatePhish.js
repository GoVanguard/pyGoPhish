function check() {
    const userPrompt = document.getElementById("userPrompt");
    const phishingWebsite = document.getElementById("phishingwebsite").value;
    const phishingWebsiteLag = document.getElementById("lagpw")
    const targetWebsite = document.getElementById("targetwebsite").value;
    const targetWebsiteLag = document.getElementById("lagtw")
    const targets = document.getElementById("targets").value;
    const dateTimeField = document.getElementById("datetimefield");
    const uDateTime = document.getElementById("datetime");
    const uPrompt = document.getElementById("prompt");
    const urgent = document.getElementById("urgent").checked
    validSyntaxPhishingWebsite = validateDomain(phishingWebsite, phishingWebsiteLag);
    validSyntaxTargetWebsite = validateDomain(targetWebsite, targetWebsiteLag);
    pingDomain(phishingWebsite, phishingWebsiteLag);
    pingDomain(targetWebsite, targetWebsiteLag);
    if(urgent) {
        dateTimeField.hidden = true;
        uPrompt.value = "Next";
        if(!targetWebsite && !targets) {
            userPrompt.innerHTML = "Immediately? Please enter a domain.";
            uPrompt.disabled = true;
        }
        else {
            uPrompt.value = "Next";
            if(validSyntaxTargetWebsite) {
                userPrompt.innerHTML = "Immediately? The boat awaits!";
                uPrompt.disabled = false;
            }
            else {
                userPrompt.innerHTML = "That is not a valid domain.";
                uPrompt.disabled = true;
            }
        }
    }
    else {
        uPrompt.value = "Schedule";
        dateTimeField.hidden = false;
        if(targetWebsite || targets) {
            if(validSyntaxTargetWebsite) { 
                if(validateSchedule(uDateTime.value)) {
                    userPrompt.innerHTML = "Let's schedule the trip."
                    uPrompt.disabled = false;
                    targets.required = false;
                }
                else {
                    userPrompt.innerHTML = "Please choose a valid date and time for phishing."
                    uPrompt.disabled = true;
                }
            }
            else {
                userPrompt.innerHTML = "This is not a valid domain.";
                uPrompt.disabled = true;
    	    }
        }
        else {
            userPrompt.innerHTML = "Where would you like to go phishing?";
            uPrompt.disabled = true;
        }
    }
}

function validateDomain(domain) {
    validate = /^[a-z0-9]+([-.][a-z0-9]+)*\.[a-z]{2,}$/i.test(domain);
    return validate;
}

function pingDomain(domain, update) {
    if(validateDomain(domain)) {
        result = ping.ping("http://www." + domain)
        result.then(data => {
            update.innerHTML = data + " ms";
        });
        result.catch(data => {
            console.error("Ping failed: " + data);
            update.innerHTML = "Unlisted";
        });
    }
}

function validateSchedule(uDateTime) {
    quasiValid = /([2-9][0-9][2-9][0-9][-])(([0][1-9])|([1][0-2]))([-](([0][1-9])|([1-2][0-9])|([3][0-1]))[T])((([0-1][0-9])|([2][0-3]))[:]([0-5][0-9]))|([2-9][1-9][0-9][0-9][-])(([0][1-9])|([1][0-2]))([-](([0][1-9])|([1-2][0-9])|    ([3][0-1]))[T])((([0-1][0-9])|([2][0-3]))[:]([0-5][0-9]))|([3-9][0-9][0-9][0-9][-])(([0][1-9])|([1][0-2]))([-](([0][1-9])|([1-2][0-9])|([3][0-1]))[T])((([0-1][0-9])|([2][0-3]))[:]([0-5][0-9]))|([0-9]{5,}[-])(([0][1-9])|([1][0-2]))([-    ](([0][1-9])|([1-2][0-9])|([3][0-1]))[T])((([0-1][0-9])|([2][0-3]))[:]([0-5][0-9]))/g.test(uDateTime);
    if(quasiValid) {
        leapYear = leapYearCheck(uDateTime);
            if(uDateTime.slice(5,7) == "02" && uDateTime.slice(8,10) > 28 && !leapYear) {
                return false;
            }
            else if(uDateTime.slice(5,7) == "02" && uDateTime.slice(8,10) > 29 && leapYear) {
                return false;
            }
            else if((uDateTime.slice(5,7) == "04" || uDateTime.slice(5,7) == "06" || uDateTime.slice(5,7) == "09" ||
                   uDateTime.slice(5,7) == "11") && uDateTime.slice(8.10) > 30) {
                return false;
            }
            else if(uDateTime.slice(8,10) > 31) {
                return false;
            }
            else {
                return true;
            }
      }
      else {
          return false;
      }
}


function leapYearCheck(uDateTime) {
    if(uDateTime%4 == 0) {
        if(uDateTime%100 == 0) {
            if(uDateTime%400 == 0) {
                return true;
            }
            else {
                return false;
            }
        }
        else {
            return true;
        }
    }
    else {
        return false;
    }
}


function convertDateTime(cDate) {
    time = cDate.getFullYear() + '-' + ((parseInt(cDate.getMonth()) + 1)<10?'0':'') + (parseInt(cDate.getMonth()) + 1) + '-' + (cDate.getDate()<10?'0':'') + cDate.getDate() + 'T' + (cDate.getHours()<10?'0':'') + cDate.getHours() + ':' + (cDate.getMinutes()<10?'0':'') + cDate.getMinutes();
    return time
}

/**
 * Creates a Ping instance.
 * @returns {Ping}
 * @constructor
 */

function Ping(opt) {
    this.opt = opt || {};
    this.favicon = this.opt.favicon || "/favicon.ico";
    this.timeout = this.opt.timeout || 0;
    this.logError = this.opt.logError || false;
};

/**
 * Pings source and triggers a callback when completed.
 * @param {string} source Source of the website or server, including protocol and port.
 * @param {Function} callback Callback function to trigger when completed. Returns error and ping value.
 * @returns {Promise|undefined} A promise that both resolves and rejects to the ping value.
 * Or undefined if the browser does not support Promise.
 */

Ping.prototype.ping = function(source, callback) {
    var promise, resolve, reject;
    if (typeof Promise !== "undefined") {
        promise = new Promise(function(_resolve, _reject) {
            resolve = _resolve;
            reject = _reject;
        });
    }

    var self = this;
    self.wasSuccess = false;
    self.img = new Image();
    self.img.onload = onload;
    self.img.onerror = onerror;

    var timer;
    var start = new Date();

    function onload(e) {
        self.wasSuccess = true;
        pingCheck.call(self, e);
    }

    function onerror(e) {
        self.wasSuccess = false;
        pingCheck.call(self, e);
    }

    if (self.timeout) {
        timer = setTimeout(function() {
            pingCheck.call(self, undefined);
    }, self.timeout); }


    /**
     * Times ping and triggers callback.
     */
    function pingCheck() {
        if (timer) { clearTimeout(timer); }
        var pong = new Date() - start;

        if (!callback) {
            if (promise) {
                return this.wasSuccess ? resolve(pong) : reject(pong);
            } else {
                throw new Error("Promise is not supported by your browser. Use callback instead.");
            }
        } else if (typeof callback === "function") {
            // When operating in timeout mode, the timeout callback doesn't pass [event] as e.
            // Notice [this] instead of [self], since .call() was used with context
            if (!this.wasSuccess) {
                if (self.logError) { console.error("error loading resource"); }
                if (promise) { reject(pong); }
                return callback("error", pong);
            }
            if (promise) { resolve(pong); }
            return callback(null, pong);
        } else {
            throw new Error("Callback is not a function.");
        }
    }

    self.img.src = source + self.favicon + "?" + (+new Date()); // Trigger image load with cache buster
    return promise;
};

if (typeof exports !== "undefined") {
    if (typeof module !== "undefined" && module.exports) {
        module.exports = Ping;
    }
} else {
    window.Ping = Ping;
}
