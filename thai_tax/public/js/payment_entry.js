frappe.ui.form.on('Payment Entry', {
	refresh(frm) {
        // Filter company tax address
	    frm.set_query('company_tax_address', function() {
            return {
				filters: {
				    is_your_company_address: true 
				}
            }
        })

        // Add button to create withholding tax cert
		if(frm.doc.docstatus == 1 && frm.doc.payment_type == 'Pay' && frm.doc.deductions.length > 0) {
			frm.add_custom_button(__('Create Withholding Tax Cert'), function () {
			    frappe.route_options = {
			        'supplier': frm.doc.party_type == 'Supplier' ? frm.doc.party : '',
                    'voucher_type': 'Payment Entry',
                    'voucher_no': frm.doc.name
				};
				frappe.set_route('withholding-tax-cert', 'new-withholding-tax-cert');
			    
			});
		}
	},

	deduct_withholding_tax: function(frm) {
		const fields = [
			{
                fieldtype: 'Link',
                label: __('WHT Type'),
                fieldname: 'wht_type',
                options: 'Withholding Tax Type',
                reqd: 1
			},
		];
		frappe.prompt(fields, function(filters){
			frm.events.add_withholding_tax_deduction(frm, filters);
		}, __('Deduct Withholding Tax'), __('Add Withholding Tax Deduction'));
	},

	add_withholding_tax_deduction: function(frm, filters) {
	    frappe.db.get_doc('Withholding Tax Type', filters['wht_type']).then(wht => {
            frappe.db.get_doc('Company', frm.doc.company).then(c => {
                var d = frm.add_child('deductions');
        	    d.account = wht.account
        	    d.cost_center = c.cost_center
        	    d.amount = -wht.percent / (100 + wht.before_vat) * frm.doc.base_total_allocated_amount
        		frm.refresh();
            })
        })
	},

})