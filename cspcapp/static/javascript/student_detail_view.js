var in_editing_mode = false;


function get_scrf_token() {
    return document.getElementById('csrf_token_div').value;
}


function changeLockStatus(element, state) {
    [...element.elements].forEach(function (item) {
        if (item.nodeName === "SELECT") {
            item.disabled = state;
        } else if (item.nodeName === "INPUT") {
            item.readOnly = state;
        }
    });
}


function enableEditDocumentMode(edit_node_type, document_id) {
    if (in_editing_mode) {
        alert('Закончите редактирование другого элемента, перед редактированием нового');
    } else {
        in_editing_mode = true;
        changeLockStatus(document.getElementById(edit_node_type + "_data_form_" + document_id.toString()), false);
        document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-floppy-disk";
        document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick = function() {disableEditDocumentMode(edit_node_type, document_id); };
    }
}


function disableEditDocumentMode(edit_node_type, document_id) {
    let form_name = "#" + edit_node_type + "_data_form_" + document_id.toString();

    changeLockStatus(document.getElementById(edit_node_type + "_data_form_" + document_id.toString()), true);

    document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-hourglass";
    document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick = function() { };

    $.ajax({
        url : "/api/" + edit_node_type + "_data_edit/",
        type : "POST",
        data : $(form_name).serialize(),
        dataType : "json",
        success : function(json) {
            if (json.result) {
                console.log(json.result);
            } else {
                console.log("Произошла ошибка: " + json.error);
            }
            finishEditDocumentMode(edit_node_type, document_id);
        },
        error : function(xhr,errmsg,err) {
            alert("Произошла ошибка: " + xhr.responseText);
            finishEditDocumentMode(edit_node_type, document_id);
        }
    });
}


function finishEditDocumentMode(edit_node_type, document_id) {
    in_editing_mode = false;
    changeLockStatus(document.getElementById(edit_node_type + "_data_form_" + document_id.toString()), true);
    document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-pencil";
    document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick = function() { enableEditDocumentMode(edit_node_type, document_id); };
}


function paymentsToggle(contract_id) {
    let elem = document.getElementById('payments_' + contract_id.toString());
    elem.hidden = !elem.hidden;
}


function add_new_payment(contract_id) {
    document.getElementById("payment_add_button_span_" + contract_id.toString()).className = "glyphicon glyphicon-hourglass";
    document.getElementById("payment_add_button_" + contract_id.toString()).onclick = function() { };
    changeLockStatus(document.getElementById("payment_add_form_" + contract_id.toString()), true);
    $.ajax({
        url : "/api/payment_add/",
        type : "POST",
        data : $("#payment_add_form_" + contract_id.toString()).serialize(),
        dataType : "json",
        success : function(json) {
            if (json.result) {
                success_end_adding_payment(contract_id, json["new_element_id"]);
                console.log(json.result);
            } else {
                console.log("Произошла ошибка: " + json.error);
                end_adding_payment(contract_id);
            }
        },
        error : function(xhr,errmsg,err) {
            alert("Произошла ошибка: " + xhr.responseText);
            end_adding_payment(contract_id);
        }
    });
}


function add_new_payment_row(contract_id) {
    let table = document.getElementById("payments_" + contract_id.toString()).childNodes[0].childNodes[0];

}


function pair_array_to_map(array) {
    var dict = {};
    for (const i in array) {
        dict[array[i].name] = array[i].value;
    }
    return dict;
}


function end_adding_payment(contract_id) {
    document.getElementById("payment_add_button_span_" + contract_id.toString()).className = "glyphicon glyphicon-plus";
    document.getElementById("payment_add_button_" + contract_id.toString()).onclick = function() { add_new_payment(contract_id); };
    changeLockStatus(document.getElementById("payment_add_form_" + contract_id.toString()), false);
}


function success_end_adding_payment(contract_id, payment_id) {
    document.getElementById("payment_add_button_span_" + contract_id.toString()).className = "glyphicon glyphicon-plus";
    document.getElementById("payment_add_button_" + contract_id.toString()).onclick = function() { add_new_payment(contract_id); };
    changeLockStatus(document.getElementById("payment_add_form_" + contract_id.toString()), false);
    let form = $(`#payment_add_form_${contract_id}`);
    let form_data = pair_array_to_map(form.serializeArray());

    let template =
        `<form action="" method="post" id="payment_data_form_${payment_id}" name=\"payment_data_form_${payment_id}">\
            <td>\
                <input type="hidden" name="csrfmiddlewaretoken" value="${get_scrf_token()}">
                <input type="hidden" name="id" value="${payment_id}">\
                <input type="text" name="issue_dt_day" value="${form_data.issue_dt_day}" style=\"border-width: 0; width: 18px;" readonly/>-\
                <input type="text" name="issue_dt_month" value="${form_data.issue_dt_month}" style=\"border-width: 0; width: 18px" readonly/>-\
                <input type="text" name="issue_dt_year" value="${form_data.issue_dt_year}" style=\"border-width: 0; width: 33px" readonly/>\
            </td>\
            <td>\
                <input type="text" name="payment_amt" value="${form_data.payment_amt}" style="border-width: 0; width: 100%;" readonly/>\
            </td>\
            <td>\
                <select name="payment_type" style="border-width: 0; width: 100%; -webkit-appearance:none;" disabled>\n`;

    for (const key in PAYMENT_TYPES) {
        template += `<option value="${key}">${PAYMENT_TYPES[key]}</option>\n`;
    }

    template += `</select>\
             </td>\
             <td><input type="text" name="voucher_no" value="${form_data.voucher_no}" style="border-width: 0; width: 100%;" readonly/></td>\
        </form>\
        <td>\
            <button id="payment_data_button_${payment_id}" onclick="enableEditDocumentMode('payment', ${payment_id})">\
                <span class="glyphicon glyphicon-pencil" id="payment_data_button_span_${payment_id}"></span>\
            </button>\
            <button type="submit"><span class="glyphicon glyphicon-time"></span></button>\
            <button><span class="glyphicon glyphicon-remove"></span></button>\
        </td>`
    ;
    let table = document.getElementById("payments_table_" + contract_id.toString());
    table.insertRow(table.rows.length - 1).innerHTML = template;
    form.trigger("reset");
}


function delete_object(type, id) {
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
        }
    });
}


function delete_object_success_end(type, id) {
    switch (type) {
        case 'contract':
            $('#contract_tr_main_' + id.toString()).remove();
            $('#payments_' + id.toString()).remove();
            break;
        case 'payment':
            $('#payment_row_' + id.toString()).remove();
            break;
        default:
            break;
    }
}


function delete_object_failure_end(type, id) {

}