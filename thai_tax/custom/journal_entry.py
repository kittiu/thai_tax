import frappe
from .payment_entry import reconcile_undue_tax_gls


def reconcile_undue_tax(jv, method):
	""" If bs_reconcile is installed, reconcile undue tax gls """
	if jv.for_payment:
		pay = frappe.get_doc("Payment Entry", jv.for_payment)
		vouchers = [jv.name, pay.name] + [r.reference_name for r in pay.references]
		reconcile_undue_tax_gls(vouchers)
