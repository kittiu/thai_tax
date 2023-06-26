frappe.ui.form.on("Journal Entry", {
	refresh(frm) {
		frm.set_query("company_tax_address", function () {
			return {
				filters: {
					is_your_company_address: true,
				},
			};
		});
	},
});
