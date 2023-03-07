frappe.ui.form.on('Sales Tax Invoice', {
	refresh(frm) {
	    frm.set_query('company_tax_address', function() {
            return {
				filters: {
				    is_your_company_address: true 
				}
            }
        })
	}
})
