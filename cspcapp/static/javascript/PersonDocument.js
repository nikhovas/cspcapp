class PersonPassportDataInfo {
    constructor(dict) {
        this.person_surname = dict.person_surname;
        this.person_name = dict.person_name;
        this.person_father_name = dict.person_father_name;
        this.authority_txt = dict.authority_txt;
        this.document_type_txt = dict.document_type_txt;
        this.authority_no = dict.authority_no;
        this.issue_dt_day = dict.issue_dt_day;
        this.issue_dt_month = dict.issue_dt_month;
        this.issue_dt_year = dict.issue_dt_year;
        this.document_series = dict.document_series;
        this.document_no = dict.document_no;
    }
}


class PersonPassportDataDBObject extends PersonPassportDataInfo{
    constructor(dict) {
        super(dict);
        this.id = dict.id;
    }

    get_edit_div() {
        return `
        <div class="passport-data-box" id="document_data_${this.id}">
            ${this.get_edit_form()}
        </div>
        <button style="background-color: #3b5998; height: 89px;" onclick="enableEditDocumentMode('document', ${this.id})" id="document_data_button_${this.id}">
            <span class="glyphicon glyphicon-pencil" id="document_data_button_span_${this.id}"/>
        </button>
        `;
    }

    get_edit_form() {
        return `
        <form action="" method="post" id="document_data_form_${this.id}" name="document_data_form_${this.id}">
                                {% csrf_token %}
                                <input type="hidden" name="id" value="${this.id}">
                                <input type="text" name="person_surname_txt" value="${this.person_surname}" style="background-color: #3b5998; border-width: 0; width: calc(33% - 2px)" readonly/>
                                <input type="text" name="person_name_txt" value="${this.person_name}" style="background-color: #3b5998; border-width: 0; width: calc(33% - 2px)" readonly/>
                                <input type="text" name="person_father_name_txt" value="${this.person_father_name}" style="background-color: #3b5998; border-width: 0; width: calc(33% - 2px)" readonly/>
                                <input type="text" name="authority_txt" value="${this.authority_txt}" style="background-color: #3b5998; border-width: 0; width: 100%" readonly/>
                                <input type="text" name="document_type_txt" value="${this.document_type_txt}" style="background-color: #3b5998; border-width: 0; width: calc(100% - 314px)" readonly/>
                                <input type="text" name="authority_no" value="${this.authority_no}" style="background-color: #3b5998; border-width: 0; width: 90px" readonly/>
                                <input type="text" name="issue_dt_day" value="${this.issue_dt_day}" style="background-color: #3b5998; border-width: 0; width: 16px; margin-left: 20px" readonly/>-
                                <input type="text" name="issue_dt_month" value="${this.issue_dt_month}" style="background-color: #3b5998; border-width: 0; width: 16px" readonly/>-
                                <input type="text" name="issue_dt_year" value="${this.issue_dt_year}" style="background-color: #3b5998; border-width: 0; width: 33px" readonly/>
                                <input type="text" name="document_series" value="${this.document_series}" style="background-color: #3b5998; border-width: 0; width: 33px; margin-left: 20px" readonly/>
                                <input type="text" name="document_no" value="${this.document_no}" style="background-color: #3b5998; border-width: 0; width: 50px" readonly/>
                            </form>
        `;
    }
}