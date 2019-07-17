REGIONS_DICT = {
    1: 'Адыгея Респ',
    2: 'Башкортостан Респ',
    3: 'Бурятия Респ',
    4: 'Алтай Респ',
    5: 'Дагестан Респ',
    6: 'Ингушетия Респ',
    7: 'Кабардино-Балкарская Респ',
    8: 'Калмыкия Респ',
    9: 'Карачаево-Черкесская Респ',
    10: 'Карелия Респ',
    11: 'Коми Респ',
    12: 'Марий Эл Респ',
    13: 'Мордовия Респ',
    14: 'Саха /Якутия/ Респ',
    15: 'Северная Осетия - Алания Респ',
    16: 'Татарстан Респ',
    17: 'Тыва Респ',
    18: 'Удмуртская Респ',
    19: 'Хакасия Респ',
    20: 'Чеченская Респ',
    21: 'Чувашская Респ',
    22: 'Алтайский край',
    23: 'Краснодарский край',
    24: 'Красноярский край',
    25: 'Приморский край',
    26: 'Ставропольский край',
    27: 'Хабаровский край',
    28: 'Амурская обл',
    29: 'Архангельская обл',
    30: 'Астраханская обл',
    31: 'Белгородская обл',
    32: 'Брянская обл',
    33: 'Владимирская обл',
    34: 'Волгоградская обл',
    35: 'Вологодская обл',
    36: 'Воронежская обл',
    37: 'Ивановская обл',
    38: 'Иркутская обл',
    39: 'Калининградская обл',
    40: 'Калужская обл',
    41: 'Камчатский край',
    42: 'Кемеровская обл',
    43: 'Кировская обл',
    44: 'Костромская обл',
    45: 'Курганская обл',
    46: 'Курская обл',
    47: 'Ленинградская обл',
    48: 'Липецкая обл',
    49: 'Магаданская обл',
    50: 'Московская обл',
    51: 'Мурманская обл',
    52: 'Нижегородская обл',
    53: 'Новгородская обл',
    54: 'Новосибирская обл',
    55: 'Омская обл',
    56: 'Оренбургская обл',
    57: 'Орловская обл',
    58: 'Пензенская обл',
    59: 'Пермский край',
    60: 'Псковская обл',
    61: 'Ростовская обл',
    62: 'Рязанская обл',
    63: 'Самарская обл',
    64: 'Саратовская обл',
    65: 'Сахалинская обл',
    66: 'Свердловская обл',
    67: 'Смоленская обл',
    68: 'Тамбовская обл',
    69: 'Тверская обл',
    70: 'Томская обл',
    71: 'Тульская обл',
    72: 'Тюменская обл',
    73: 'Ульяновская обл',
    74: 'Челябинская обл',
    75: 'Забайкальский край',
    76: 'Ярославская обл',
    77: 'г. Москва',
    78: 'г. Санкт-Петербург',
    79: 'Еврейская Аобл',
    82: 'Республика Крым',
    83: 'Ненецкий АО',
    86: 'Ханты-Мансийский Автономный округ - Югра АО',
    87: 'Чукотский АО',
    89: 'Ямало-Ненецкий АО',
    92: 'г. Севастополь'
};


PAYMENT_TYPES = {
    0: 'Секретарь',
    1: 'Банк',
    2: 'Сбербанк онлайн'
};


// class ContractPayment {
//     id = 0;
//     payment_day = 0;
//     payment_month = 0;
//     payment_year = 0;
//     payment_amt = 0;
//
// }










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
    changeLockStatus(document.getElementById(edit_node_type + "_data_form_" + document_id.toString()), false);
    document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-floppy-disk";
    document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick = function() {disableEditDocumentMode(edit_node_type, document_id); };
}


function disableEditDocumentMode(edit_node_type, document_id) {
    let form_name = "#" + edit_node_type + "_data_form_" + document_id.toString();

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
        },
        error : function(xhr,errmsg,err) {
            alert("Произошла ошибка: " + xhr.responseText);
        }
    });

    changeLockStatus(document.getElementById(edit_node_type + "_data_form_" + document_id.toString()), true);

    document.getElementById(edit_node_type + "_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-pencil";
    document.getElementById(edit_node_type + "_data_button_" + document_id.toString()).onclick = function() { enableEditDocumentMode(edit_node_type, document_id); };
}


function paymentsToggle(contract_id) {
    let elem = document.getElementById('payments_' + contract_id.toString());
    elem.hidden = !elem.hidden;
}


function add_new_element(object_type, object_id) {
    document.getElementById(object_type + "_add_button_span").className = "glyphicon glyphicon-hourglass";
    document.getElementById(object_type + "_add_button").onclick = function() { };
    changeLockStatus(document.getElementById(object_type + "_add_form"), true);

    $.ajax({
        url : "/api/" + object_type + "_add/",
        type : "POST",
        data : $("#" + object_type + "_add_form").serialize(),
        dataType : "json",
        success : function(json) {
            if (json.result) {
                console.log(json.result);
            } else {
                console.log("Произошла ошибка: " + json.error);
            }
            end_adding(object_type);
        },
        error : function(xhr,errmsg,err) {
            alert("Произошла ошибка: " + xhr.responseText);
            end_adding(object_type);
        }
    });
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
                // let form_element = document.getElementById("payment_add_form_" + contract_id.toString());
                // success_end_adding_payment(contract_id, {
                //     issue_dt_day: form_element.getElementById("new_payment_issue_dt_day").value,
                //     issue_dt_month: form_element.getElementById("new_payment_issue_dt_month").value,
                //     issue_dt_year: form_element.getElementById("new_payment_issue_dt_year").value,
                //     payment_amt: form_element.getElementById("new_payment_payment_amt").value,
                //     payment_type: form_element.getElementById("new_payment_payment_type").value,
                //     voucher_no: form_element.getElementById("new_payment_voucher_no").value,
                //     payment_id: json["new_element_id"]
                // });
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


// function add_new_payment() {
//
//     document.getElementById("payment_add_button_span").className = "glyphicon glyphicon-hourglass";
//     document.getElementById("payment_add_button").onclick = function() { };
//     changeLockStatus(document.getElementById("payment_add_form"), true);
//
//     var form_data = {
//         issue_dt_day: document.getElementById("new_payment_issue_dt_day").value,
//         issue_dt_month: document.getElementById("new_payment_issue_dt_month").value,
//         issue_dt_year: document.getElementById("new_payment_issue_dt_year").value,
//         payment_amt: document.getElementById("new_payment_payment_amt").value,
//         payment_type: document.getElementById("new_payment_payment_type").value,
//         voucher_no: document.getElementById("new_payment_voucher_no").value,
//         csrfmiddlewaretoken: document.getElementById("payment_add_div_csrf_token").childNodes[0].value
//     };
//
//     let ddd = $("#payment_add_form").serialize();
//
//     // alert(document.getElementById("payment_add_div_csrf_token").childNodes[0].data);
//     // alert(JSON.stringify(form_data));
//
//
//     $.ajax({
//         url : "/api/payment_add/",
//         type : "POST",
//         data : JSON.stringify(form_data),
//         dataType : "json",
//         success : function(json) {
//             if (json.result) {
//                 console.log(json.result);
//             } else {
//                 console.log("Произошла ошибка: " + json.error);
//             }
//             end_adding(object_type);
//         },
//         error : function(xhr,errmsg,err) {
//             alert("Произошла ошибка: " + xhr.responseText);
//             end_adding(object_type);
//         }
//     });
// }


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
    let table = document.getElementById("payments_table_" + contract_id.toString());
    let new_row = table.insertRow(table.rows.length - 1);
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
    new_row.innerHTML = template;
    form.trigger("reset");
}