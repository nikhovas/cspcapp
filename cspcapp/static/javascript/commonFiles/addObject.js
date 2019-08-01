function addNewObject(type, parent_id) {
    document.getElementById(`${type}_add_button_span_${parent_id}`).className = "glyphicon glyphicon-hourglass";
    document.getElementById(`${type}_add_button_${parent_id}`).onclick = function() { };
    changeLockStatus($( `#${type}_add_row_${parent_id}` ), true);
    $.ajax({
        url : `/api/add/${type}/`,
        type : "POST",
        data : $(`#${type}_add_form_${parent_id}`).serialize(),
        dataType : "json",
        success : function(json) {
            if (json.result) {
                addObjectSuccess(type, json["new_element_id"], parent_id);
                console.log(json.result);
            } else {
                console.log("Произошла ошибка: " + json.error);
                addObjectFailure(type, parent_id);
            }
        },
        error : function(xhr,errmsg,err) {
            alert("Произошла ошибка: " + xhr.responseText);
            addObjectFailure(type, parent_id);
        }
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


function addObjectSuccess(type, id, parent_id) {
    let form = $(`#${type}_add_form_${parent_id}`);
    let form_data = pair_array_to_map(form.serializeArray());
    // let template = window[`${type}Template`](form_data, id);
    // let table = document.getElementById(`${type}_table_${parent_id}`);
    $(`#${type}_table_${parent_id}`).find('tbody').append(window[`${type}Template`](form_data, id));
    // table.insertRow(table.rows.length - 1).innerHTML = template;
    form.trigger("reset");
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