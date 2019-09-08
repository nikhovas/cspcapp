function submit_student(id) {
    $.ajax({
        url : `/students_requests/submit/`,
        type : "POST",
        data : {'csrfmiddlewaretoken': get_scrf_token(), 'id': id},
        dataType : "json",
        success : function(json) { if (json.result) delete_object_success_end('student_request', id); else alert('Ошибка: ' + json.error) },
        error : function(xhr,errmsg,err) { alert("Err: " + xhr.responseText); delete_object_failure_end('student_request', id); }
    });
}