import json
from ast import literal_eval

import frappe
import pandas as pd
from frappe import _

REF_DOCTYPES = ["Purchase Invoice", "Expense Claim", "Journal Entry"]


@frappe.whitelist()
def test_require_withholding_tax(doc):
	"""Check if any of the payment references has withholding tax type"""
	pay = json.loads(doc)
	for d in pay.get("references"):
		# Purchase Invoice
		if d.get("reference_doctype") in ["Purchase Invoice", "Sales Invoice"]:
			ref_doc = frappe.get_doc(d.get("reference_doctype"), d.get("reference_name"))
			for item in ref_doc.items:
				if item.custom_withholding_tax_type:
					return True
	return False


@frappe.whitelist()
def get_withholding_tax_from_type(filters, doc):
	filters = literal_eval(filters)
	pay = json.loads(doc)
	wht = frappe.get_doc("Withholding Tax Type", filters["wht_type"])
	company = frappe.get_doc("Company", pay["company"])
	base_amount = 0
	for ref in pay.get("references"):
		if ref.get("reference_doctype") not in [
			"Sales Invoice",
			"Purchase Invoice",
			"Expense Claim",
			"Journal Entry",
		]:
			return
		if not ref.get("allocated_amount") or not ref.get("total_amount"):
			continue
		# Find gl entry of ref doc that has undue amount
		gl_entries = frappe.db.get_all(
			"GL Entry",
			filters={
				"voucher_type": ref["reference_doctype"],
				"voucher_no": ref["reference_name"],
			},
			fields=[
				"name",
				"account",
				"debit",
				"credit",
			],
		)
		for gl in gl_entries:
			credit = gl["credit"]
			debit = gl["debit"]
			alloc_percent = ref["allocated_amount"] / ref["total_amount"]
			report_type = frappe.get_cached_value("Account", gl["account"], "report_type")
			if report_type == "Profit and Loss":
				base_amount += alloc_percent * (credit - debit)
	if not base_amount:
		frappe.throw(_("There is nothing to withhold tax for"))
	sign = -1 if pay.get("party_type") == "Receive" else 1
	return {
		"withholding_tax_type": wht.name,
		"account": wht.account,
		"cost_center": company.cost_center,
		"base": base_amount * sign,
		"rate": wht.percent,
		"amount": wht.percent / 100 * base_amount * sign,
	}


@frappe.whitelist()
def get_withholding_tax_from_docs_items(doc):
	pay = json.loads(doc)
	company = frappe.get_doc("Company", pay["company"])
	result = []
	wht_types = frappe.get_all(
		"Withholding Tax Type",
		fields=["name", "percent", "account"],
		as_list=True,
	)
	wht_rates = frappe._dict({x[0]: {"percent": x[1], "account": x[2]} for x in wht_types})
	for ref in pay.get("references"):
		# Purchase Invoice
		if ref.get("reference_doctype") in ["Purchase Invoice", "Sales Invoice"]:
			if not ref.get("allocated_amount") or not ref.get("total_amount"):
				continue
			sign = -1 if pay.get("payment_type") == "Pay" else 1
			ref_doc = frappe.get_doc(ref.get("reference_doctype"), ref.get("reference_name"))
			for item in ref_doc.items:
				if item.custom_withholding_tax_type:
					wht = item.custom_withholding_tax_type
					result.append(
						{
							"withholding_tax_type": wht,
							"account": wht_rates[wht]["account"],
							"cost_center": company.cost_center,
							"base": sign * item.amount,
							"rate": wht_rates[wht]["percent"],
							"amount": wht_rates[wht]["percent"] / 100 * sign * item.amount,
						}
					)
	# Group by and sum
	df = pd.DataFrame(result)
	group_fields = ["withholding_tax_type", "account", "cost_center", "rate"]
	sum_fields = ["base", "amount"]
	dict_sum_fields = {x: sum for x in sum_fields}
	result = df.groupby(group_fields, as_index=False).aggregate(dict_sum_fields)
	result = result.to_dict(orient="records")
	return result


@frappe.whitelist()
def make_withholding_tax_cert(filters, doc):
	filters = literal_eval(filters)
	pay = json.loads(doc)
	cert = frappe.new_doc("Withholding Tax Cert")
	cert.supplier = pay.get("party_type") == "Supplier" and pay.get("party") or ""
	if cert.supplier != "":
		supplier = frappe.get_doc("Supplier", cert.supplier)
		cert.supplier_name = supplier and supplier.supplier_name or ""
		cert.supplier_address = supplier and supplier.supplier_primary_address or ""
	cert.voucher_type = "Payment Entry"
	cert.voucher_no = pay.get("name")
	cert.company_address = filters.get("company_address")
	cert.income_tax_form = filters.get("income_tax_form")
	cert.date = filters.get("date")
	for d in pay.get("deductions"):
		base = d.get("custom_withholding_tax_base", 0)
		amount = d.get("amount", 0)
		rate = 0
		wht_type = d.get("custom_withholding_tax_type")
		if wht_type:
			rate = frappe.get_cached_value("Withholding Tax Type", wht_type, "percent")
		cert.append(
			"withholding_tax_items",
			{
				"tax_base": -base,
				"tax_rate": rate,
				"tax_amount": -amount,
			},
		)
	return cert


def reconcile_undue_tax(doc, method):
	""" If bs_reconcile is installed, unreconcile undue tax gls """
	vouchers = [doc.name] + [r.reference_name for r in doc.references]
	reconcile_undue_tax_gls(vouchers)


def reconcile_undue_tax_gls(vouchers, unreconcile=False):
	""" Only if bs_reconcile app is install, reconcile/unreconcile undue tax gl entries """
	if "bs_reconcile" not in frappe.get_installed_apps():
		return 
	try:
		from bs_reconcile.balance_sheet_reconciliation import utils
	except ImportError:
		pass
	tax = frappe.get_single("Tax Invoice Settings")
	undue_taxes = [tax.purchase_tax_account_undue, tax.sales_tax_account_undue]
	gl_entries = utils.get_gl_entries_by_vouchers(vouchers)
	undue_tax_gls = list(filter(lambda x: x.account in undue_taxes, gl_entries))
	if unreconcile:
		utils.unreconcile_gl(undue_tax_gls)
	else:
		utils.reconcile_gl(undue_tax_gls)
