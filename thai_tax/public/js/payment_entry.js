frappe.ui.form.on("Payment Entry", {
	refresh(frm) {
		// Filter company tax address
		frm.set_query("company_tax_address", function () {
			return {
				filters: {
					is_your_company_address: true,
				},
			};
		});

		// Add button to create withholding tax cert
		if (
			frm.doc.docstatus == 1 &&
			frm.doc.payment_type == "Pay" &&
			frm.doc.deductions.length > 0
		) {
			frm.add_custom_button(__("Create Withholding Tax Cert"), function () {
				const fields = [
					{
						fieldtype: "Link",
						label: __("WHT Type"),
						fieldname: "wht_type",
						options: "Withholding Tax Type",
						reqd: 1,
					},
					{
						fieldtype: "Date",
						label: __("Date"),
						fieldname: "date",
						reqd: 1,
					},
					{
						fieldtype: "Select",
						label: __("Income Tax Form"),
						fieldname: "income_tax_form",
						options: "PND3\nPND53",
					},
					{
						fieldtype: "Link",
						label: __("Company Address"),
						fieldname: "company_address",
						options: "Address",
						get_query: () => {
							return {
								filters: {
									is_your_company_address: 1,
								},
							};
						},
					},
				];
				frappe.prompt(
					fields,
					function (filters) {
						frm.events.make_withholding_tax_cert(frm, filters);
					},
					__("Withholding Tax Cert"),
					__("Create Withholding Tax Cert")
				);
			});
		}

		// Create Clear Undue VAT Journal Entry
		if (frm.doc.docstatus == 1) {
			// Check first whether all tax has been cleared, to add button
			frappe.call({
				method: "thai_tax.custom.custom_api.to_clear_undue_tax",
				args: {
					dt: cur_frm.doc.doctype,
					dn: cur_frm.doc.name,
				},
				callback: function (r) {
					if (r.message == true) {
						// Add button
						frm.add_custom_button(__("Clear Undue Tax"), function () {
							frm.trigger("make_clear_vat_journal_entry");
						});
					}
				},
			});
		}
	},

	// Called from button Duduct Withholding Tax
	deduct_withholding_tax: function (frm) {
		const fields = [
			{
				fieldtype: "Link",
				label: __("WHT Type"),
				fieldname: "wht_type",
				options: "Withholding Tax Type",
				reqd: 1,
			},
		];
		frappe.prompt(
			fields,
			function (filters) {
				frm.events.add_withholding_tax_deduction(frm, filters);
			},
			__("Deduct Withholding Tax"),
			__("Add Withholding Tax Deduction")
		);
	},

	add_withholding_tax_deduction: function (frm, filters) {
		return frappe.call({
			method: "thai_tax.custom.custom_api.get_withholding_tax",
			args: {
				filters: filters,
				doc: frm.doc,
			},
			callback: function (r) {
				var d = frm.add_child("deductions");
				d.account = r.message["account"];
				d.cost_center = r.message["cost_center"];
				d.amount = r.message["amount"];
				frm.refresh();
			},
		});
	},

	make_withholding_tax_cert: function (frm, filters) {
		return frappe.call({
			method: "thai_tax.custom.custom_api.make_withholding_tax_cert",
			args: {
				filters: filters,
				doc: frm.doc,
			},
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			},
		});
	},

	make_clear_vat_journal_entry() {
		return frappe.call({
			method: "thai_tax.custom.custom_api.make_clear_vat_journal_entry",
			args: {
				dt: cur_frm.doc.doctype,
				dn: cur_frm.doc.name,
			},
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			},
		});
	},
});
