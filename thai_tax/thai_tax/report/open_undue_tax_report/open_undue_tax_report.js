// Copyright (c) 2023, Kitti U. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Open Undue Tax Report"] = {
	"filters": [
		{
			"fieldname": "account",
			"label": __("Undue Tax Account"),
			"fieldtype": "Link",
			"options": "Account",
			get_query: () => {
				return {
					query: "thai_tax.custom.queries.undue_tax_query",
				};
			},
			"width": "800px",
			"reqd": 1,
		},
		{
			"fieldname": "voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Select",
			"options": "\nPurchase Invoice\nSales Invoice\nJournal Entry",
		},
		
		{
			"fieldname": "voucher_no",
			"label": __("Voucher No"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "is_open",
			"label": __("Is Open Only"),
			"fieldtype": "Check",
		},
	]
};