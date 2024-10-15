import frappe
from frappe.model.naming import set_name_from_naming_options


def rename_temporarily_named_docs(doctype):
    """Rename temporarily named docs using autoname options"""
    # Load monkey patch only if thai_tax is installed
    load_patch = "thai_tax" in frappe.get_installed_apps()
    # --
    docs_to_rename = frappe.get_all(doctype, {"to_rename": "1"}, order_by="creation", limit=50000)
    for doc in docs_to_rename:
        oldname = doc.name
        set_name_from_naming_options(frappe.get_meta(doctype).autoname, doc)
        newname = doc.name
        frappe.db.sql(
            f"UPDATE `tab{doctype}` SET name = %s, to_rename = 0 where name = %s",
            (newname, oldname),
            auto_commit=True,
        )
		# Monkey patch
        if load_patch:
            for tax_invoice in ["Sales Tax Invoice", "Purchase Tax Invoice"]:
                frappe.db.sql(
                    f"UPDATE `tab{tax_invoice}` SET gl_entry = %s where gl_entry = %s",
                    (newname, oldname),
                    auto_commit=True,
                )
        # --
            