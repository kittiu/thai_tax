// Copyright (c) 2023, Kitti U. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tax Invoice Settings", {
	onload: function (frm) {
		for (let field of [
			"sales_tax_account",
			"sales_tax_account_undue",
			"purchase_tax_account",
			"purchase_tax_account_undue",
		]) {
			frm.set_query(field, function (doc) {
				return {
					filters: {
						account_type: "Tax",
						company: doc.company,
					},
				};
			});
		}
	},

	company: function (frm) {
		frm.set_value("sales_tax_account", null);
		frm.set_value("sales_tax_account_undue", null);
		frm.set_value("purchase_tax_account", null);
		frm.set_value("purchase_tax_account_undue", null);
	},
});
