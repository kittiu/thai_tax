from frappe.utils import flt
from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry
from frappe.utils import cint, cstr, flt, formatdate, getdate, now


def check_if_in_list(gle, gl_map, dimensions=None):

    account_head_fieldnames = [
        "voucher_detail_no",
        "party",
        "against_voucher",
        "cost_center",
        "against_voucher_type",
        "party_type",
        "project",
        "finance_book",
        "against_gl_entry" # Additional column
    ]

    if dimensions:
        account_head_fieldnames = account_head_fieldnames + dimensions

    for e in gl_map:
        same_head = True
        if e.account != gle.account:
            same_head = False
            continue

        for fieldname in account_head_fieldnames:
            if cstr(e.get(fieldname)) != cstr(gle.get(fieldname)):
                same_head = False
                break

        if same_head:
            return e
