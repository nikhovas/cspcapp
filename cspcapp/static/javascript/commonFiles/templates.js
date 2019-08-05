function paymentTemplate(form_data, id) {
    let template =
        `<form action="" method="post" id="payment_data_form_${id}" name=\"payment_data_form_${id}">\
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
        </form>\
        <td>\
            <button id="payment_data_button_${id}" onclick="enableEditObjectMode('payment', ${id})">\
                <span class="glyphicon glyphicon-pencil" id="payment_data_button_span_${id}"></span>\
            </button>\
            <button type="submit"><span class="glyphicon glyphicon-time"></span></button>\
            <button><span class="glyphicon glyphicon-remove"></span></button>\
        </td>`
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
    let template = `
    <tr id="course_element_row_${id}">
                            <form method="post" id="course_element_data_form_${id}">
                                ${scrfTokenInput()}
                                <input type="hidden" name="course_element_id" value="${id}">
                                <td>
                                    <select name="teacher_id">`;
    TEACHERS_LIST.forEach(function(item) {
        template += `<option value="${item.id}"`;
        if (item.id === form_data.teacher_id) {
            template += ' selected';
        }
        template += `>${item.surname} ${item.name} ${item.fatherName} - ${item.username} </option>`;
    });
    template += `</select></td>`;
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
    </form>
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


function courseTemplate(form_data, id) {
    let template = `
    <tr id="course_row_${id}">
            <form method="post" id="course_data_form_${id}">
                <input type="hidden" name="csrfmiddlewaretoken" value="${get_scrf_token()}">
                <input type="hidden" name="course_id" value="${id}">
                <td>${id}</td>
                <td><input type="text" name="sphere_txt" value="${form_data.sphere_txt}" style="border-width: 0; width: 100%;" readonly/></td>
                <td><input type="text" name="name_txt" value="${form_data.name_txt}" style="border-width: 0; width: 100%;" readonly/></td>
                <td><input type="text" name="short_nm" value="${form_data.short_nm}" style="border-width: 0; width: 100%;" readonly/></td>
                <td><input type="text" name="price_per_hour" value="${form_data.price_per_hour}" style="border-width: 0; width: 100%;" readonly/></td>
                <td><input type="text" name="payment_dt_day" value="${form_data.payment_dt_day}" style="border-width: 0; width: 100%;" readonly/></td>
                <td>dev</td>
                </form>
                <td>
                    <button onclick="toggleInfoTab('course', ${id})">
                        <span id="course_row_more_info_button_span_${id}" class="glyphicon glyphicon-arrow-down"></span>
                    </button>
                    <button>
                        <span class="glyphicon glyphicon-pencil"></span>
                    </button>
                    <button>
                            <span class="glyphicon glyphicon-remove"></span>
                    </button>
                </td>
            </tr>
            <tr id="course_row_more_info_${id}" hidden="true">
                <td colspan="8">
                    <table class="table main-table" style="width: 100%" id="course_element_table_${id}">
                        <thead>
                            <tr>
                                <td style="width: 40px;">№</td>
                                <td>Учитель</td>
                                <td style="width: 120px;">ПН</td>
                                <td style="width: 120px;">ВТ</td>
                                <td style="width: 120px;">СР</td>
                                <td style="width: 120px;">ЧТ</td>
                                <td style="width: 120px;">ПТ</td>
                                <td style="width: 120px;">СБ</td>
                                <td style="width: 120px;">ВС</td>
                                <td style="width: 80px;"></td>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                        <tfoot>
                        <tr id="course_element_add_row_${id}">
                                 <form method="post" id="course_element_add_form_${id}" name="course_element_add_form_${id}">
                                <input type="hidden" name="course_id" value="${id}">
                                 <input type="hidden" name="csrfmiddlewaretoken" value="${get_scrf_token()}">
                                <td >+</td>
                                <td>
                                    <select name="teacher_id">`;
    TEACHERS_LIST.forEach(function(item) {
        template += `<option value="${item.id}>${item.surname} ${item.name} ${item.fatherName} - ${item.username} </option>"`;
    });
    template += `</select>
                                </td>
                                <td>
                                        <input type="text" name="course_class_start_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_start_minute" value="" style="border-width: 0; width: 18px;" />-
                                        <input type="text" name="course_class_end_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_end_minute" value="" style="border-width: 0; width: 18px;" />
                                    </td>
                                 <td>
                                        <input type="text" name="course_class_start_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_start_minute" value="" style="border-width: 0; width: 18px;" />-
                                        <input type="text" name="course_class_end_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_end_minute" value="" style="border-width: 0; width: 18px;" />
                                    </td>
                                 <td>
                                        <input type="text" name="course_class_start_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_start_minute" value="" style="border-width: 0; width: 18px;" />-
                                        <input type="text" name="course_class_end_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_end_minute" value="" style="border-width: 0; width: 18px;" />
                                    </td>
                                 <td>
                                        <input type="text" name="course_class_start_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_start_minute" value="" style="border-width: 0; width: 18px;" />-
                                        <input type="text" name="course_class_end_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_end_minute" value="" style="border-width: 0; width: 18px;" />
                                    </td>
                                 <td>
                                        <input type="text" name="course_class_start_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_start_minute" value="" style="border-width: 0; width: 18px;" />-
                                        <input type="text" name="course_class_end_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_end_minute" value="" style="border-width: 0; width: 18px;" />
                                    </td>
                                 <td>
                                        <input type="text" name="course_class_start_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_start_minute" value="" style="border-width: 0; width: 18px;" />-
                                        <input type="text" name="course_class_end_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_end_minute" value="" style="border-width: 0; width: 18px;" />
                                    </td>
                                 <td>
                                        <input type="text" name="course_class_start_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_start_minute" value="" style="border-width: 0; width: 18px;" />-
                                        <input type="text" name="course_class_end_hour" value="" style="border-width: 0; width: 18px;" />:
                                        <input type="text" name="course_class_end_minute" value="" style="border-width: 0; width: 18px;" />
                                    </td>
                                </form>
                                <td>
                                    <button id="course_element_add_button_${id}" onclick="addNewObject('course_element', ${id})">
                                        <span class="glyphicon glyphicon-plus" id="course_element_add_button_span_${id}"></span>
                                    </button>
                                    <button>
                                        <span class="glyphicon glyphicon-erase"></span>
                                    </button>
                                </td>

                            </tr>
                        </tfoot>
                    </table>
                </td>
            </tr>
    `;
    return template;
}