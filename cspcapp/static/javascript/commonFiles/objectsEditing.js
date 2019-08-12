var in_editing_mode = false;


function changeLockStatus(element, state) {
    element.find("input").attr('readonly', state);
    element.find("select").attr('disabled', state);
}


function enableEditObjectMode(edit_node_type, document_id) {
    if (in_editing_mode) {
        alert('Закончите редактирование другого элемента, перед редактированием нового');
    } else {
        in_editing_mode = true;
        changeLockStatus($(`#${edit_node_type}_row_${document_id}`), false);
        document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-floppy-disk";
        document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick =
            function() {disableEditObjectMode(edit_node_type, document_id); };
    }
}


function disableEditObjectMode(edit_node_type, document_id) {
    changeLockStatus($(`${edit_node_type}_row_${document_id}`), true);
    document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-hourglass";
    document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick = function() { };

    $.ajax({
        url : `/api/edit/${edit_node_type}/`,
        type : "POST",
        data : serializeObject($(`#${edit_node_type}_row_${document_id}`)),
        dataType : "json",
        success : function(json) { finishEditObjectMode(edit_node_type, document_id); },
        error : function(xhr,errmsg,err) { alert("Err: " + xhr.responseText); finishEditObjectMode(edit_node_type, document_id); }
    });
}


function finishEditObjectMode(edit_node_type, document_id) {
    in_editing_mode = false;
    changeLockStatus($(`#${edit_node_type}_row_${document_id}`), true);
    document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-pencil";
    document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick = function() { enableEditObjectMode(edit_node_type, document_id); };
}