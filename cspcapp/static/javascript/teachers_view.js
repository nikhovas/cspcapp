function newPassword(user_id) {
    document.getElementById(`teacher_data_change_password_${user_id}`).innerHTML = `<span class="glyphicon glyphicon-hourglass"></span>`;
    document.getElementById(`teacher_data_change_password_${user_id}`).onclick = function() { };
    let new_password = prompt('Введите новый пароль (ОТКРЫТЫЕ ДАННЫЕ!!!): ');
    if (new_password === null) {
        document.getElementById(`teacher_data_change_password_${user_id}`).innerHTML = `П`;
        document.getElementById(`teacher_data_change_password_${user_id}`).onclick = function() { newPassword(user_id) };

        return;
    }
    $.ajax({
        url: '/api/change_password/',
        type: 'POST',
        data:  {'csrfmiddlewaretoken': get_scrf_token(), 'user_id': user_id, 'new_password': new_password},
        dataType: 'json',
        success : function(json) {
            if (!json.result) {
                alert(`Ошибка: ${json.error}`);
            }
            document.getElementById(`teacher_data_change_password_${user_id}`).innerHTML = `П`;
            document.getElementById(`teacher_data_change_password_${user_id}`).onclick = function() { newPassword(user_id) };
            },
        error : function(xhr,errmsg,err) {
            alert("Ошибка:\n " + xhr.responseText);
            document.getElementById(`teacher_data_change_password_${user_id}`).innerHTML = `П`;
            document.getElementById(`teacher_data_change_password_${user_id}`).onclick = function() { newPassword(user_id) };
            },
    })
}