# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import Case, CustomFunction


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, None, None


def get_columns():
	return [
		{
			"label": _("Tax Address"),
			"fieldname": "company_tax_address",
			"fieldtype": "Link",
			"options": "Address",
			"width": 0,
		},
		{
			"label": _("Report Date"),
			"fieldname": "report_date",
			"fieldtype": "Date",
			"width": 0,
		},
		{
			"label": _("Number"),
			"fieldname": "name",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Customer"),
			"fieldname": "party_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Tax ID"),
			"fieldname": "tax_id",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Tax Base"),
			"fieldname": "tax_base",
			"fieldtype": "Currency",
			"options": "Company:company:default_currency",
			"width": 0,
		},
		{
			"label": _("Tax Amount"),
			"fieldname": "tax_amount",
			"fieldtype": "Currency",
			"options": "Company:company:default_currency",
			"width": 0,
		},
		{
			"label": _("Ref Voucher Type"),
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Ref Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 200,
		},
	]


def get_data(filters):

	tinv = frappe.qb.DocType("Sales Tax Invoice")
	cust = frappe.qb.DocType("Customer")
	round = CustomFunction("round", ["value", "digit"])
	month = CustomFunction("month", ["date"])
	year = CustomFunction("year", ["date"])
	concat = CustomFunction("concat", ["1", "2"])

	query = (
		frappe.qb.from_(tinv)
		.left_join(cust)
		.on(cust.name == tinv.party)
		.select(
			tinv.company_tax_address.as_("company_tax_address"),
			tinv.report_date.as_("report_date"),
			Case()
			.when(tinv.docstatus == 1, tinv.name)
			.else_(concat(tinv.name, " (CANCEL)"))
			.as_("name"),
			tinv.party_name.as_("party_name"),
			cust.tax_id.as_("tax_id"),
			Case().when(tinv.docstatus == 1, round(tinv.tax_base, 2)).else_(0).as_("tax_base"),
			Case()
			.when(tinv.docstatus == 1, round(tinv.tax_amount, 2))
			.else_(0)
			.as_("tax_amount"),
			tinv.voucher_type.as_("voucher_type"),
			tinv.voucher_no.as_("voucher_no"),
		)
		.where(
			(tinv.docstatus.isin([1, 2]))
			& (month(tinv.report_date) == filters.get("month"))
			& (year(tinv.report_date) == filters.get("year"))
		)
		.orderby(tinv.name)
	)

	if filters.get("company_tax_address"):
		query = query.where(tinv.company_tax_address == filters.get("company_tax_address"))

	result = query.run(as_dict=True)

	return result
