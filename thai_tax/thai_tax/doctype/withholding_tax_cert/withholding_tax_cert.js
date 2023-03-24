// Copyright (c) 2023, Kitti U. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Withholding Tax Cert', {
	refresh(frm) {
	    frm.set_query('supplier_address', function() {
            return {
				filters: {
				    link_doctype: 'Supplier',
				    link_name: frm.doc.supplier,
				}
            }
        })
	}
})
