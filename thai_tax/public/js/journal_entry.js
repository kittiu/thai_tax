frappe.ui.form.on("Journal Entry", {
	refresh(frm) {
		frm.set_query("company_tax_address", function () {
			return {
				filters: {
					is_your_company_address: true,
				},
			};
		});
		frm.set_query("company_tax_address", "tax_invoice_details", () => {
			return {
				filters: {
					is_your_company_address: true,
				},
			};
		});
	},
});
