function deleteItem(type, id) {
    if (type in config) {
        let deleteMsg = config[type].delete_caution;
        if (deleteMsg && !confirm('Внимание!\n' + deleteMsg)) return;
    }
    changeLockStatus($(`#${type}_row_${id}`), false);
    // changeLockStatus(document.getElementById(`${type}_data_form_${id}`), false);
    $(`#${type}_data_button_span_${id}`).className = "glyphicon glyphicon-hourglass";
    $(`#${type}_data_button_${id}`).onclick = function() {};
    $.ajax({
        url : `/api/delete/${type}/`,
        type : "POST",
        data : {'csrfmiddlewaretoken': get_scrf_token(), 'id': id},
        dataType : "json",
        success : function(json) {
            if (json.success) delete_object_success_end(type, id);
            else alert(json.error_msg); delete_object_failure_end(type, id);
            },
        error : function(xhr,errmsg,err) { console.log(xhr); console.log(errmsg); console.log(err); alert("Err: " + "1)" + xhr.responseText + "\n\n\n2) " + errmsg + "\n\n\n3) " + err); delete_object_failure_end(type, id); }
    });
}


function delete_object_success_end(type, id) {
    $(`#${type}_row_${id}`).remove();
    $(`#${type}_row_more_info_${id}`).remove();
    delete_object_common_end(type, id);
}


function delete_object_failure_end(type, id) {
    changeLockStatus(document.getElementById(`${type}_row_${id}`), true);
    document.getElementById(`delete_${type}_data_button_span_${id}`).className = "glyphicon glyphicon-remove";
    document.getElementById(`delete_${type}_data_button_${id}`).onclick = function() { deleteItem(type, id) };
    delete_object_common_end(type, id);
}

function delete_object_common_end(type, id) { }


