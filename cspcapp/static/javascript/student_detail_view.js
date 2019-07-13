function demo() {
    alert('gsdagadsf')
}

class DocumentEditFunctions {
    static enableEditDocumentMode(document_id) {
        document.getElementById("document_data_" + document_id.toString()).childNodes.forEach(function(item) {
            item.readOnly = false;
        });
        document.getElementById("document_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-floppy-disk";
        document.getElementById("document_data_button_" + document_id.toString()).onclick = function() {DocumentEditFunctions.disableEditDocumentMode(document_id); };
    }

    static disableEditDocumentMode(document_id) {
        document.getElementById("document_data_" + document_id.toString()).childNodes.forEach(function(item) {
            item.readOnly = true;
        });
        document.getElementById("document_data_button_span_" + document_id.toString()).className = "glyphicon glyphicon-pencil";
        document.getElementById("document_data_button_" + document_id.toString()).onclick = function() {DocumentEditFunctions.enableEditDocumentMode(document_id); };
    }
}

