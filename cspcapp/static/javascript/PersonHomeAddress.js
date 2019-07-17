class PersonHomeAddressInfo {
    constructor(dict) {
        this.region_cd = dict.region_cd;
        this.city_txt = dict.city_txt;
        this.street_txt = dict.street_txt;
        this.house_txt = dict.house_txt;
        this.building_no = dict.building_no;
        this.structure_no = dict.structure_no;
        this.flat_nm = dict.flat_nm;
    }
}


class PersonHomeAddressDBObject extends PersonHomeAddressInfo{
    constructor(dict) {
        super(dict);
        this.id = dict.id;
    }

    get_edit_div() {
        return `

<div class="address-data-box" id="address_data_{{ contract.0.payer_address.pk }}">
                            ${this.get_edit_form()}
                        </div>
                        <button style="background-color: #3b5998; height: 65px;" onclick="enableEditDocumentMode('address', {{ contract.0.payer_address.pk }})" id="address_data_button_{{ contract.0.payer_address.pk }}">
                            <span class="glyphicon glyphicon-pencil" id="address_data_button_span_{{ contract.0.payer_address.pk }}"/>
                        </button>
        `;
    }

    get_edit_form() {
        template = `
        <form action="" method="post" id="address_data_form_${this.id}" name="address_data_form_${this.id}">
            {% csrf_token %}
            <input type="hidden" name="id" value="${this.id}">
            ${this.get_selected_regions()}
            <input type="text" name="city_txt" value="${this.city_txt}" style="background-color: #3b5998; border-width: 0; width: calc(100% - 160px)" readonly/>
            <input type="text" name="street_txt" value="${this.street_txt}" style="background-color: #3b5998; border-width: 0; width: calc(100% - 194px)" readonly/>
            <input type="text" name="house_txt" value="${this.house_txt}" style="background-color: #3b5998; border-width: 0; width: 40px" readonly/>-
            <input type="text" name="building_no" value="${this.building_no}" style="background-color: #3b5998; border-width: 0; width: 40px" readonly/>-
            <input type="text" name="structure_no" value="${this.structure_no}" style="background-color: #3b5998; border-width: 0; width: 40px" readonly/>-
            <input type="text" name="flat_nm" value="${this.flat_nm}" style="background-color: #3b5998; border-width: 0; width: 40px" readonly/>
        </form>
        `;

    }

    get_selected_regions() {
        template = `<select name="region_cd" style="background-color: #3b5998; border-width: 0; width: 150px; -webkit-appearance:none;" onclick="return false;">`;
        for (const key in REGIONS_DICT) {
            template += `<option value="${key}"`;
            if (this.region_cd === key) {
                template += `selected`;
            }
            template += `>${REGIONS_DICT[key]} ${REGIONS_DICT[key]}</option>`;
        }
        template += `</select>;
        return template;
    }
}