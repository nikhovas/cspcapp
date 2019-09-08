function addNewCourseClass(id) {
    document.getElementById(`course_detail_add_button_span_${id}`).className = "glyphicon glyphicon-hourglass";
    document.getElementById(`course_detail_add_button_${id}`).onclick = function() { };
    changeLockStatus($( `#course_detail_add_row_${id}` ), true);
    $.ajax({
        url : `/api/add_course_class/`,
        type : "POST",
        data : serializeObject( $(`#course_detail_add_row_${id}`) ),
        dataType : "json",
        success : function(json) {
            if (json.result) {
                $(`#course_detail_table_body_${id}`).append(json.html);
                console.log(json.html);
                $(`#course_detail_add_row_${id}`).trigger("reset");
            } else {
                alert('Ошибка: ' + json.error)
            }

            document.getElementById(`course_detail_add_button_span_${id}`).className = "glyphicon glyphicon-plus";
            document.getElementById(`course_detail_add_button_${id}`).onclick = function() { addNewCourseClass(id); };
            changeLockStatus($(`#course_detail_add_row_${id}`), false);
            },
        error : function(xhr,errmsg,err) {
            alert("Err: " + xhr.responseText);
            document.getElementById(`course_detail_add_button_span_${id}`).className = "glyphicon glyphicon-plus";
            document.getElementById(`course_detail_add_button_${id}`).onclick = function() { addNewCourseClass(id); };
            changeLockStatus($(`#course_detail_add_row_${id}`), false);
            },
    });
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


//


function changeLockStatus(element, state) {
    element.find("input").attr('readonly', state);
    element.find("select").attr('disabled', state);
}


function enableEditCourseClassMode(id) {
    if (in_editing_mode) {
        alert('Закончите редактирование другого элемента, перед редактированием нового');
    } else {
        in_editing_mode = true;
        changeLockStatus($(`#course_detail_row_${id}`), false);
        document.getElementById(`course_detail_data_button_span_${id}`).className = "glyphicon glyphicon-floppy-disk";
        document.getElementById(`course_detail_data_button_${id}`).onclick =
            function() {disableEditCourseClassMode(id); };
    }
}


function disableEditCourseClassMode(id) {
    changeLockStatus($(`course_detail_row_${id}`), true);
    document.getElementById(`course_detail_data_button_span_${id}`).className = "glyphicon glyphicon-hourglass";
    document.getElementById(`course_detail_data_button_${id}`).onclick = function() { };

    $.ajax({
        url : `/api/edit_course_class/`,
        type : "POST",
        data : serializeObject($(`#course_detail_row_${id}`)),
        dataType : "json",
        success : function(json) { if(json.result) finishEditCourseClassMode(id); else {alert('Ошибка: ' + json.error); finishEditCourseClassMode(id); } },
        error : function(xhr,errmsg,err) { alert("Err: " + xhr.responseText); finishEditCourseClassMode(id); }
    });
}


function finishEditCourseClassMode(id) {
    in_editing_mode = false;
    changeLockStatus($(`#course_detail_row_${id}`), true);
    document.getElementById(`course_detail_data_button_span_${id}`).className = "glyphicon glyphicon-pencil";
    document.getElementById(`course_detail_data_button_${id}`).onclick = function() { enableEditCourseClassMode(id); };
}




// delete



function deleteCourseClass(id) {
    changeLockStatus($(`#course_detail_row_${id}`), false);
    $(`#course_detail_data_button_span_${id}`).className = "glyphicon glyphicon-hourglass";
    $(`#course_detail_data_button_${id}`).onclick = function() {};
    $.ajax({
        url : `/api/delete_course_class/`,
        type : "POST",
        data : {'csrfmiddlewaretoken': get_scrf_token(), 'id': id},
        dataType : "json",
        success : function(json) {
            if (json.result) deleteCourseClassSuccess(id);
            else alert(json.error); deleteCourseClassFailure(id);
            },
        error : function(xhr,errmsg,err) { console.log(xhr); console.log(errmsg); console.log(err); alert("Err: " + "1)" + xhr.responseText + "\n\n\n2) " + errmsg + "\n\n\n3) " + err); deleteCourseClassFailure(id); }
    });
}


function deleteCourseClassSuccess(id) {
    $(`#course_detail_row_${id}`).remove();
}


function deleteCourseClassFailure(id) {
    changeLockStatus(document.getElementById(`${type}_row_${id}`), true);
    document.getElementById(`delete_course_detail_data_button_span_${id}`).className = "glyphicon glyphicon-remove";
    document.getElementById(`delete_course_detail_data_button_${id}`).onclick = function() { deleteCourseClass(id) };
}