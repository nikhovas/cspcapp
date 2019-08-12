function submit_user(id) {
    $.ajax({
        url : `/registration_requests/submit/`,
        type : "POST",
        data : {'csrfmiddlewaretoken': get_scrf_token(), 'id': id},
        dataType : "json",
        success : function(json) { delete_object_success_end('reg_form', id); },
        error : function(xhr,errmsg,err) { alert("Err: " + xhr.responseText); delete_object_failure_end('reg_form', id); }
    });
}