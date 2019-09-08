var newRowID = 1;

function addRow() {
    let val = $('#add_course_element_select').val();
    let text = $('#add_course_element_select option:selected').text();
    $('#course_elements_table').find('tbody').append(`
<tr id="course_row_${newRowID}">
                        <td><input type="hidden" name="course_element" value="${val}">${text}</td>
                        <td>
                        <div class="buttons-table-horizontal default-buttons">
                            <button type="button" onclick="deleteRow(${newRowID})">
                                <span class="glyphicon glyphicon-trash" "></span>
                            </button>
                            </div>
                        </td>
                        </tr>
    `);
    ++newRowID;
}

function deleteRow(num) {
    $(`#course_row_${num}`).remove();
}