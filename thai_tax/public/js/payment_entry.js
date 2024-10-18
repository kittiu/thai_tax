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
		// Create Deduct Withholding Tax button
		if (frm.doc.docstatus == 0 && frm.doc.references && frm.doc.references.length > 0) {
			frm.trigger("add_withholding_tax_deduction_buttons");
		}
		// Add button to create withholding tax cert
		if (
			frm.doc.docstatus == 1 &&
			frm.doc.payment_type == "Pay" &&
			frm.doc.deductions.length > 0
		) {
			frm.trigger("add_create_withholding_tax_cert_button");
		}
		// Create Clear Undue VAT Journal Entry
		if (frm.doc.docstatus == 1) {
			frm.trigger("add_create_undue_vat_journal_entry_button");
		}
	},

	add_withholding_tax_deduction_buttons: function (frm) {
		// 1. Based On Manual Selection
		frm.add_custom_button(
			__("Based On Manual Selection"),
			function () {
				frm.trigger("manual_deduct_withholding_tax");
			},
			__("Withhold Tax")
		);
		// 2. Based On Paying Document's Line Items
		frappe.call({
			method: "thai_tax.custom.payment_entry.test_require_withholding_tax",
			args: {
				doc: frm.doc,
			},
			callback: function (r) {
				if (r.message) {
					frm.dashboard.add_comment(
						__(
							"Please be noted that, some paying documents may require <b>Withholding Tax Deduction</b>"
						),
						"blue",
						true
					);
					frm.add_custom_button(
						__("Based On Paying Document's Line Items"),
						function () {
							frm.trigger("auto_deduct_withholding_tax");
						},
						__("Withhold Tax")
					);
				}
			},
		});
	},

	add_create_withholding_tax_cert_button: function (frm) {
		frm.add_custom_button(__("Create Withholding Tax Cert"), async function () {
			let income_tax_form = "";
			if (frm.doc.party_type == "Supplier") {
				income_tax_form = (
					await frappe.db.get_value(
						frm.doc.party_type,
						frm.doc.party,
						"custom_default_income_tax_form"
					)
				).message.custom_default_income_tax_form;
			}
			const fields = [
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
					default: income_tax_form,
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
	},

	add_create_undue_vat_journal_entry_button: function (frm) {
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
	},

	manual_deduct_withholding_tax: function (frm) {
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
			(filters) => {
				frm.events.manual_add_withholding_tax_deduction(frm, filters);
			},
			__("Deduct Withholding Tax"),
			__("Add Withholding Tax Deduction")
		);
	},

	auto_deduct_withholding_tax: function (frm) {
		frappe.confirm(
			__(
				"Scan through all reference documents for line items that require tax withholding."
			),
			() => {
				frm.trigger("auto_add_withholding_tax_deduction");
			}
		);
	},

	manual_add_withholding_tax_deduction: function (frm, filters) {
		return frappe.call({
			method: "thai_tax.custom.payment_entry.get_withholding_tax_from_type",
			args: {
				filters: filters,
				doc: frm.doc,
			},
			callback: function (r) {
				var d = frm.add_child("deductions");
				d.custom_withholding_tax_type = r.message["withholding_tax_type"];
				d.account = r.message["account"];
				d.cost_center = r.message["cost_center"];
				d.custom_withholding_tax_base = r.message["base"];
				d.amount = r.message["amount"];
				frm.doc.paid_amount = frm.doc.paid_amount - Math.abs(d.amount);
				frm.refresh();
				frappe.show_alert(
					{
						message: __("Deducted {0} for Withholding Tax", [
							d.amount.toLocaleString(),
						]),
						indicator: "green",
					},
					5
				);
			},
		});
	},

	auto_add_withholding_tax_deduction: function (frm) {
		return frappe.call({
			method: "thai_tax.custom.payment_entry.get_withholding_tax_from_docs_items",
			args: {
				doc: frm.doc,
			},
			callback: function (r) {
				var deduct = 0;
				r.message.forEach(function (item) {
					var d = frm.add_child("deductions");
					d.custom_withholding_tax_type = item["withholding_tax_type"];
					d.account = item["account"];
					d.cost_center = item["cost_center"];
					d.custom_withholding_tax_base = item["base"];
					d.amount = item["amount"];
					deduct += d.amount;
				});
				frm.doc.paid_amount = frm.doc.paid_amount - Math.abs(deduct);
				frm.refresh();
				frappe.show_alert(
					{
						message: __("Deducted {0} for Withholding Tax", [deduct.toLocaleString()]),
						indicator: "green",
					},
					5
				);
			},
		});
	},

	make_withholding_tax_cert: function (frm, filters) {
		return frappe.call({
			method: "thai_tax.custom.payment_entry.make_withholding_tax_cert",
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
