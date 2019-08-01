function deleteItem(type, id) {
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
            if (json.result) {
                delete_object_success_end(type, id);
                console.log(json.result);
            } else {
                console.log("Произошла ошибка: " + json.error);
            }
        },
        error : function(xhr,errmsg,err) {
            alert("Произошла ошибка: " + xhr.responseText);
            delete_object_failure_end(type, id);
        }
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


