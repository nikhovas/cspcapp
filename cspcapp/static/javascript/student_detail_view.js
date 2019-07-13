//Django basic setup for accepting ajax requests.
// Cookie obtainer Django

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
// Setup ajax connections safetly

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function demo() {
    alert('gsdagadsf')
}

class DocumentEditFunctions {
    static enableEditDocumentMode(document_id) {
        document.getElementById("document_data_form_" + document_id.toString()).childNodes.forEach(function(item) {
            // Console.log(111);
            item.readOnly = false;
        });
        document.getElementById("document_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-floppy-disk";
        document.getElementById("document_data_button_" + document_id.toString()).onclick = function() {DocumentEditFunctions.disableEditDocumentMode(document_id); };
    }

    //TODO make it work

    static disableEditDocumentMode(document_id) {
        let form_name = "#document_data_form_" + document_id.toString();

        $.ajax({
            url : "/api/document_data_edit/",
            type : "POST",
            data : $(form_name).serialize(),
            dataType : "json",
            success : function(json) {

                // alert(typeof(json));
                // json_obj = JSON.json
                // JSON.parse(json)['success']
                // alert(json.response);
                // if (JSON.parse(json)['success'] === true) {
                //     alert('Success!');
                // } else {
                //     alert('Some Error!');
                // }

                if (json.is_valid) {
                    console.log(json.response);
                } else {
                    console.log("You didn't message : I want an AJAX response");
                }
            },
            error : function(xhr,errmsg,err) {
                alert(xhr.responseText);
            }
        });

        document.getElementById("document_data_form_" + document_id.toString()).childNodes.forEach(function(item) {
            item.readOnly = true;
        });
        document.getElementById("document_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-pencil";
        document.getElementById("document_data_button_" + document_id.toString()).onclick = function() { DocumentEditFunctions.enableEditDocumentMode(document_id); };
    }
}

