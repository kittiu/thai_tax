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
			"label": _("No."),
			"fieldname": "no",
			"fieldtype": "Int",
			"width": 0,
		},
		{
			"label": _("Supplier Tax ID"),
			"fieldname": "supplier_tax_id",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Branch"),
			"fieldname": "branch",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Supplier Name"),
			"fieldname": "supplier_name",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Address"),
			"fieldname": "address_line1",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Tambon"),
			"fieldname": "city",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Amphur"),
			"fieldname": "county",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Province"),
			"fieldname": "state",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Zip Code"),
			"fieldname": "pincode",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 0,
		},
		{
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Tax Base"),
			"fieldname": "tax_base",
			"fieldtype": "Currency",
			"options": "Company:company:default_currency",
			"width": 0,
		},
		{
			"label": _("Tax Rate"),
			"fieldname": "tax_rate",
			"fieldtype": "Int",
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
			"label": _("Tax Payer"),
			"fieldname": "tax_payer",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("WHT Cert."),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Withholding Tax Cert",
			"width": 0,
		},
		{
			"label": _("Voucher Type"),
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 0,
		},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 0,
		},
	]


def get_data(filters):

	wht_cert = frappe.qb.DocType("Withholding Tax Cert")
	wht_items = frappe.qb.DocType("Withholding Tax Items")
	supplier = frappe.qb.DocType("Supplier")
	address = frappe.qb.DocType("Address")
	round = CustomFunction("round", ["value", "digit"])
	month = CustomFunction("month", ["date"])
	year = CustomFunction("year", ["date"])

	query = (
		frappe.qb.from_(wht_cert)
		.join(wht_items)
		.on(wht_items.parent == wht_cert.name)
		.join(supplier)
		.on(supplier.name == wht_cert.supplier)
		.left_join(address)
		.on(address.name == wht_cert.supplier_address)
		.select(
			supplier.tax_id.as_("supplier_tax_id"),
			supplier.branch_code.as_("branch"),
			supplier.supplier_name.as_("supplier_name"),
			address.address_line1.as_("address_line1"),
			address.city.as_("city"),
			address.county.as_("county"),
			address.state.as_("state"),
			address.pincode.as_("pincode"),
			wht_cert.date.as_("date"),
			wht_items.description.as_("description"),
			round(wht_items.tax_base, 2).as_("tax_base"),
			wht_items.tax_rate.as_("tax_rate"),
			round(wht_items.tax_amount, 2).as_("tax_amount"),
			Case()
			.when(wht_cert.tax_payer == "Withholding", "1")
			.when(wht_cert.tax_payer == "Paid One Time", "3")
			.else_(wht_cert.tax_payer)
			.as_("tax_payer"),
			wht_cert.name.as_("name"),
			wht_cert.voucher_type.as_("voucher_type"),
			wht_cert.voucher_no.as_("voucher_no"),
		)
		.distinct()
		.where(
			(wht_cert.docstatus == 1)
			& (wht_cert.income_tax_form == "PND53")
			& (month(wht_cert.date) == filters.get("month"))
			& (year(wht_cert.date) == filters.get("year"))
		)
		.orderby(wht_cert.date, wht_cert.name)
	)

	if filters.get("company_address"):
		query = query.where(wht_cert.company_address == filters.get("company_address"))

	result = query.run(as_dict=True)

	# Add row number column
	i = 0
	for r in result:
		r["no"] = i = i + 1

	return result
