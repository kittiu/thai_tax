frappe.ui.form.on('Address', {

	refresh(frm) {

        // Add button to use VAT Service
		frm.add_custom_button(__('Get Address by Tax ID'), function () {
			const fields = [
				{
					fieldtype: 'Data',
					label: __('Tax ID'),
					fieldname: 'tax_id',
					reqd: 1
				},
				{
					fieldtype: 'Data',
					label: __('Branch'),
					fieldname: 'branch',
					default: '00000',
					reqd: 1
				},
			];
			frappe.prompt(fields, function(filters){
				frm.events.get_address_by_tax_id(frm, filters);
			}, __('RD VAT Service'), __('Get Address'));
		})
	},

	get_address_by_tax_id: function(frm, filters) {
		return frappe.call({
			method: 'thai_tax.custom.custom_api.get_address_by_tax_id',
			args: {
				tax_id: filters.tax_id,
				branch: filters.branch
			},
			callback: function(r) {
				cur_frm.set_value('address_title', r.message['name']);
				cur_frm.set_value('address_line1', r.message['address_line1']);
				cur_frm.set_value('city', r.message['city']);
				cur_frm.set_value('county', r.message['county']);
				cur_frm.set_value('state', r.message['state']);
				cur_frm.set_value('pincode', r.message['pincode']);
			}
		});
	}

})
