// Copyright (c) 2023, Kitti U. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Withholding Tax Type", {
	refresh: function (frm) {
		if (frm.doc.name === "Auto" && !frappe.boot.developer_mode) {
			// make the document read-only
			frm.disable_form();
		} else {
			frm.enable_save();
		}
	},
});
