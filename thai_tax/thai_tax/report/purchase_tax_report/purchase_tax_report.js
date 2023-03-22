// Copyright (c) 2023, Kitti U. and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Purchase Tax Report"] = {
	filters: [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
		},
		{
			"fieldname": "company_tax_address",
			"label": __("Company Address"),
			"fieldtype": "Link",
			"options": "Address",
			get_query: () => {
				return {
					filters: {
						'is_your_company_address': 1
					}
				};
			}
		}
	]
};
