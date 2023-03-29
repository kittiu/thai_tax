# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import CustomFunction, Case
from frappe.query_builder.functions import Sum, Avg, GroupConcat, Coalesce

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, None, None


def get_columns():
	return [
		{
			"label": _("Undue Tax"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
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
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 0,
		},
		{
			"label": _("Undue Tax Amount"),
			"fieldname": "undue_tax_amount",
			"fieldtype": "Float",
			"width": 0,
		},
		{
			"label": _("Clear Tax Amount"),
			"fieldname": "clear_tax_amount",
			"fieldtype": "Float",
			"width": 0,
		},
		{
			"label": _("Open Tax Amount"),
			"fieldname": "open_tax_amount",
			"fieldtype": "Float",
			"width": 0,
		},
		{
			"label": _("Clearing Vouchers"),
			"fieldname": "clearing_vouchers",
			"fieldtype": "Data",
			"width": 300,
		},
	]


def get_data(filters):

	undue = frappe.qb.DocType("GL Entry")
	clear = frappe.qb.DocType("GL Entry")
	round = CustomFunction("round", ["value", "digit"])
	setting = frappe.get_doc('Tax Invoice Settings')
	purchase_tax = setting.purchase_tax_account_undue
	avg_undue = Coalesce(Avg(undue.debit-undue.credit), 0)
	sum_clear = Coalesce(Sum(clear.debit-clear.credit), 0)

	query = (
		frappe.qb.from_(undue)
		.left_outer_join(clear)
		.on(
			(undue.name == clear.against_gl_entry)
			& (clear.account == undue.account)
		)
		.select(
			undue.account,
			undue.voucher_type,
			undue.voucher_no,
			undue.posting_date,
			Case().when(undue.account == purchase_tax, avg_undue).else_(-avg_undue).as_("undue_tax_amount"),
			Case().when(undue.account == purchase_tax, -sum_clear).else_(sum_clear).as_("clear_tax_amount"),
			Case().when(undue.account == purchase_tax, avg_undue + sum_clear).else_(-(avg_undue + sum_clear)).as_("open_tax_amount"),
			GroupConcat(clear.voucher_no).distinct().as_("clearing_vouchers")
		)
		.where(undue.against_gl_entry.isnull())
		.where(undue.account == filters["account"])
		.groupby(undue.account, undue.voucher_type, undue.voucher_no, undue.posting_date)
		.orderby(undue.account, undue.voucher_type, undue.voucher_no, undue.posting_date)
	)

	if filters.get("voucher_type"):
		query = query.where(undue.voucher_type == filters["voucher_type"])
	if filters.get("voucher_no"):
		query = query.where(undue.voucher_no.like("%{0}%".format(filters["voucher_no"])))
	if filters.get("from_date"):
		query = query.where(undue.posting_date >= filters["from_date"])
	if filters.get("to_date"):
		query = query.where(undue.posting_date <= filters["to_date"])

	query2 = frappe.qb.from_(query).select("*")

	if filters.get("is_open") == 1:
		query2 = query2.where(round(query.open_tax_amount, 3) != 0)

	result = query2.run(as_dict=True)

	return result
