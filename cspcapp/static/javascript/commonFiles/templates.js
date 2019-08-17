function paymentTemplate(form_data, id) {
    let template =
        `<tr id="payment_row_${id}">\
            <td>\
                <input type="hidden" name="csrfmiddlewaretoken" value="${get_scrf_token()}">
                <input type="hidden" name="id" value="${id}">\
                <input type="text" name="issue_dt_day" value="${form_data.payment_dt_day}" style=\"border-width: 0; width: 18px;" readonly/>-\
                <input type="text" name="issue_dt_month" value="${form_data.payment_dt_month}" style=\"border-width: 0; width: 18px" readonly/>-\
                <input type="text" name="issue_dt_year" value="${form_data.payment_dt_year}" style=\"border-width: 0; width: 33px" readonly/>\
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
        
        <td>\
            <button id="payment_data_button_${id}" onclick="enableEditObjectMode('payment', ${id})">\
                <span class="glyphicon glyphicon-pencil" id="payment_data_button_span_${id}"></span>\
            </button>\
            <button type="submit"><span class="glyphicon glyphicon-time"></span></button>\
            <button><span class="glyphicon glyphicon-remove"></span></button>\
        </td>
    </tr>`
    ;
    return template;
}


let TEACHERS_LIST = [
    {
        id: 5,
        surname: 'fdsadf',
        name: 'name',
        fatherName: 'fdsfdsfddfa',
        username: 'fasdfds'
    }
];


function course_elementTemplate(form_data, id) {
    console.log('aaaaa');
    console.log(form_data);
    let select_copy = $('#add_row_teacher_id').clone();
    select_copy.removeAttr('id');
    let template = `
    <tr id="course_element_row_${id}">
                                ${scrfTokenInput()}
                                <input type="hidden" name="course_element_id" value="${id}">
                                <td>
                                ${select_copy[0].outerHTML}
                                    </td>`;
    for (let i = 0; i < 7; ++i) {
        template += `
        <td>
            <input type="text" name="course_class_start_hour" value="${form_data.course_class_start_hour[i]}" style="border-width: 0; width: 18px;" readonly/>:
            <input type="text" name="course_class_start_minute" value="${form_data.course_class_start_minute[i]}" style="border-width: 0; width: 18px;" readonly/>-
            <input type="text" name="course_class_end_hour" value="${form_data.course_class_end_hour[i]}" style="border-width: 0; width: 18px;" readonly/>:
            <input type="text" name="course_class_end_minute" value="${form_data.course_class_end_minute[i]}" style="border-width: 0; width: 18px;" readonly/>
        </td>
        `
    }
    template += `
                                <td>
                                    <button id="course_element_data_button_${id}" onclick="enableEditObjectMode('course_element', ${id})">
                                        <span id="course_element_data_button_span_${id}" class="glyphicon glyphicon-pencil"></span>
                                    </button>
                                    <button onclick="deleteItem('course_element', ${id})">
                                            <span class="glyphicon glyphicon-remove"></span>
                                    </button>
                                </td>
                            </tr>
    `;
    return template;
}


// function course_elementTemplate(form_data, id) {
//     console.log('aaaaa');
//     console.log(form_data);
//     let template = `
//     <tr id="course_element_row_${id}">
//                                 ${scrfTokenInput()}
//                                 <input type="hidden" name="course_element_id" value="${id}">
//                                 <td>
//                                 ${$('#add_row_teacher_id').clone()}
//                                     <select name="teacher_id">`;
//
//     TEACHERS_LIST.forEach(function(item) {
//         template += `<option value="${item.id}"`;
//         if (item.id === form_data.teacher_id) {
//             template += ' selected';
//         }
//         template += `>${item.surname} ${item.name} ${item.fatherName} - ${item.username} </option>`;
//     });
//     template += `</select></td>`;
//     template += `</td>`;
//     for (let i = 0; i < 7; ++i) {
//         template += `
//         <td>
//             <input type="text" name="course_class_start_hour" value="${form_data.course_class_start_hour[i]}" style="border-width: 0; width: 18px;" readonly/>:
//             <input type="text" name="course_class_start_minute" value="${form_data.course_class_start_minute[i]}" style="border-width: 0; width: 18px;" readonly/>-
//             <input type="text" name="course_class_end_hour" value="${form_data.course_class_end_hour[i]}" style="border-width: 0; width: 18px;" readonly/>:
//             <input type="text" name="course_class_end_minute" value="${form_data.course_class_end_minute[i]}" style="border-width: 0; width: 18px;" readonly/>
//         </td>
//         `
//     }
//     template += `
//                                 <td>
//                                     <button id="course_element_data_button_${id}" onclick="enableEditObjectMode('course_element', ${id})">
//                                         <span id="course_element_data_button_span_${id}" class="glyphicon glyphicon-pencil"></span>
//                                     </button>
//                                     <button onclick="deleteItem('course_element', ${id})">
//                                             <span class="glyphicon glyphicon-remove"></span>
//                                     </button>
//                                 </td>
//                             </tr>
//     `;
//     return template;
// }

function course_detailTemplate(form_data, id) {

    let template = `<tr id="course_detail_row_${id}">
                                {% csrf_token %}
                                <input type="hidden" name="id" value="${id}">
                                <td><input type="text" name="class_dt_day" value="${form_data.class_dt_day}" placeholder="ДД" style="width: 24px; border-width: 0" readonly>-
                                <input type="text" name="class_dt_month" value="${form_data.class_dt_month}" placeholder="ММ" style="width: 24px; border-width: 0" readonly>-
                                <input type="text" name="class_dt_year" value="${form_data.class_dt_year}" placeholder="ГГГГ" style="width: 48px; border-width: 0" readonly></td>
                                    <td><input type="text" name="start_tm_hour" value="${form_data.start_tm_hour}" placeholder="ЧЧ" style="width: 24px; border-width: 0" readonly>
                                        : <input type="text" name="start_tm_minute" value="${form_data.start_tm_minute}" placeholder="ММ" style="width: 24px; border-width: 0" readonly></td>
                                    <td><input type="text" name="end_tm_hour" value="${form_data.end_tm_hour}" placeholder="ЧЧ" style="width: 24px; border-width: 0" readonly>
                                        : <input type="text" name="end_tm_minute" value="${form_data.end_tm_minute}" placeholder="ММ" style="width: 24px; border-width: 0" readonly></td>
                                <td>

                    <button id="course_detail_data_button_${id}" onclick="enableEditObjectMode('course_detail', ${id})">
                        <span id="course_detail_data_button_span_${id}" class="glyphicon glyphicon-pencil"></span>
                    </button>
                    <button id="delete_course_detail_data_button_${id}" onclick="deleteItem('course_detail', ${id})">
                            <span id="delete_course_detail_data_button_span_${id}" class="glyphicon glyphicon-remove"></span>
                    </button>
                                </td>
                            </tr>`;
    return template;
}