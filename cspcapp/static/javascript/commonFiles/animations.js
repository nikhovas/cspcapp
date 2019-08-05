function toggleInfoTab(type, id) {
    let elem = document.getElementById(`${type}_row_more_info_${id}`);
    elem.hidden = !elem.hidden;
    let span = document.getElementById(`${type}_row_more_info_button_span_${id}`);
    if (span.className == "glyphicon glyphicon-arrow-down") {
        span.className = "glyphicon glyphicon-arrow-up";
    } else {
        span.className = "glyphicon glyphicon-arrow-down";
    }
}