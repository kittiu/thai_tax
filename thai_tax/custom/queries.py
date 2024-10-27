import frappe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def undue_tax_query(doctype, txt, searchfield, start, page_len, filters):
	setting = frappe.get_doc("Tax Invoice Settings")
	res = list({setting.purchase_tax_account_undue, setting.sales_tax_account_undue})
	return [[x] for x in res if x]
