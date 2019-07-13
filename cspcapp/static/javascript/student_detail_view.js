function demo() {
    alert('gsdagadsf')
}

class DocumentEditFunctions {
    static enableEditDocumentMode(document_id) {
        document.getElementById("document_data_form_" + document_id.toString()).childNodes.forEach(function(item) {
            // Console.log(111);
            item.readOnly = false;
        });
        document.getElementById("document_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-floppy-disk";
        document.getElementById("document_data_button_" + document_id.toString()).onclick = function() {DocumentEditFunctions.disableEditDocumentMode(document_id); };
    }

    static disableEditDocumentMode(document_id) {
        let form_name = "#document_data_form_" + document_id.toString();

        $.ajax({
            url : "/api/document_data_edit/",
            type : "POST",
            data : $(form_name).serialize(),
            success : function(json) {
                if (json['success'] == true) {

                } else {
                    alert('Some Error!');
                }
            },
            error : function(xhr,errmsg,err) {
                alert(xhr.responseText);
            }
        });

        document.getElementById("document_data_form_" + document_id.toString()).childNodes.forEach(function(item) {
            item.readOnly = true;
        });
        document.getElementById("document_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-pencil";
        document.getElementById("document_data_button_" + document_id.toString()).onclick = function() { DocumentEditFunctions.enableEditDocumentMode(document_id); };
    }
}

