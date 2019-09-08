String.prototype.replaceAll = function(search, replacement) {
    return this.split(search).join(replacement);
};


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function get_scrf_token() {
    return getCookie('csrftoken');
}


function scrfTokenInput() {
    return `<input type="hidden" name="csrfmiddlewaretoken" value="${get_scrf_token()}">`;
}


function serializeObject(object) {
    let result = "";
    object.find("input,select").each(function(item) {
        if (this.type === 'checkbox') {
            if ($(this).is(':checked')) {
                result += `${this.name}=True&`;
            } else {
                result += `${this.name}=False&`;
            }
        } else {
            result += `${this.name}=${this.value}&`;
        }

    });
    console.log(result);
    return result;
}


function htmlInputToObject(object) {
    let result = {};
    object.find("input,select").each(function(item) {
        if (this.type === 'checkbox') {
            result[this.name] = $(this).is(':checked');
        } else {
            result[this.name] = this.value;
        }

    });
    console.log(result);
    return result;
}


function jsonFromObject(object) {
    let arr = [];
    object.find("input,select").each(function(item) {
        if (this.type === 'checkbox') {
            if ($(this).is(':checked')) {
                arr.push({'name': this.name, 'value': 'True'});
            } else {
                arr.push({'name': this.name, 'value': 'False'});
            }
        } else {
            arr.push({'name': this.name, 'value': this.value});
        }
    });
    return pair_array_to_map(arr);
}


function pair_array_to_map(array) {
    var dict = {};
    for (const i in array) {
        if (!(array[i].name in dict)) {
            dict[array[i].name] = [];
        }
        dict[array[i].name].push(array[i].value);
    }
    for (const i in dict) {
        if (dict[i].length === 1) {
            dict[i] = dict[i][0];
        }
    }
    return dict;
}


function aaa() {
    $("#dialog").dialog();
}

// window.onload = function () {
//     if (!sessionStorage.getItem('is_session_data_loaded')) {
//         $.ajax({
//             url : `/session_data/`,
//             dataType : "json",
//             success : function(json) {
//                 for (let key in json) {
//                     sessionStorage.setItem(key, JSON.stringify(json[key]));
//                     console.log(json[key]);
//                 }
//             }
//         });
//     }
// };