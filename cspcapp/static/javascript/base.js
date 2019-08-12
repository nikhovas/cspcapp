function update_students_forms() {
    $.ajax({
        url : `/google/api/dump_data/`
    });
}

function update_google_info() {
    $.ajax({
        url : `/google/api/update_form/`
    });
}