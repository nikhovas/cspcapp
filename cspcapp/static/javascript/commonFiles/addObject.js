function addNewObject(type, parent_id) {
    document.getElementById(`${type}_add_button_span_${parent_id}`).className = "glyphicon glyphicon-hourglass";
    document.getElementById(`${type}_add_button_${parent_id}`).onclick = function() { };
    changeLockStatus($( `#${type}_add_row_${parent_id}` ), true);
    $.ajax({
        url : `/api/add/${type}/`,
        type : "POST",
        data : serializeObject( $(`#${type}_add_row_${parent_id}`) ),
        dataType : "json",
        success : function(json) { addObjectSuccess(type, json, parent_id); },
        error : function(xhr,errmsg,err) { alert("Err: " + xhr.responseText); addObjectFailure(type, parent_id); },
    });
}


function resetAddButtonStatus(type, parent_id) {
    document.getElementById(`${type}_add_button_span_${parent_id}`).className = "glyphicon glyphicon-plus";
    document.getElementById(`${type}_add_button_${parent_id}`).onclick = function() { addNewObject(type, parent_id); };
    changeLockStatus($(`#${type}_add_row_${parent_id}`), false);
}


function addObjectFailure(type, parent_id) {
    resetAddButtonStatus(type, parent_id);
}


function addObjectSuccess(type, json, parent_id) {
    $(`#${type}_table_body_${parent_id}`).append(json.html);
    console.log(json.html);
    $(`#${type}_add_row_${parent_id}`).trigger("reset");
    resetAddButtonStatus(type, parent_id);
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