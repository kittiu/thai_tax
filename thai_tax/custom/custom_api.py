import frappe
from frappe import _


def create_tax_invoice_on_gl_tax(doc, method):

    def create_tax_invoice(doc, doctype, base_amount, tax_amount, voucher):
        tinv_dict = {}
        # For sales invoice / purchase invoice / payment and journal entry, we can get the party from GL
        gl = frappe.db.get_all(
            'GL Entry',
            filters={'voucher_type': doc.voucher_type, 'voucher_no': doc.voucher_no, 'party': ['!=', '']},
            fields=['party'],
        )
        party = gl and gl[0].get('party')
        # Case use Journal Entry
        if not party and doc.voucher_type == 'Journal Entry':
            je = frappe.get_doc(doc.voucher_type, doc.voucher_no)
            party = je.supplier
            if je.for_payment:
                tinv_dict.update({
                    'against_voucher_type': 'Payment Entry',
                    'against_voucher': je.for_payment,
                })
        if not party:
            frappe.throw(_('Cannot find party for the creating tax invoice'))
        # Case expense claim, partner is not employee, but the supplier, correct it first.
        if doc.voucher_type == 'Expense Claim':
            if not voucher.supplier:
                frappe.throw(_('Please fill in Supplier for Purchase Tax Invoice'))
            party = voucher.supplier
        # Create Tax Invoice
        tinv_dict.update({
            'doctype': doctype,
            'gl_entry': doc.name,
            'tax_amount': tax_amount,
            'tax_base': base_amount,
            'party': party,
        })
        tinv = frappe.get_doc(tinv_dict)
        tinv.insert(ignore_permissions=True)
        return tinv
        
    def update_voucher_tinv(doctype, voucher, tinv):
        # Set company tax address
        def update_company_tax_address(voucher, tinv):
            # From Sales Invoice and Purchase Invoice, use voucher address
            if tinv.voucher_type == 'Sales Invoice':
                tinv.company_tax_address = voucher.company_address
            elif tinv.voucher_type == 'Purchase Invoice':
                tinv.company_tax_address = voucher.billing_address
            else:  # From Payment Entry, Expense Claim and Journal Entry
                tinv.company_tax_address = voucher.company_tax_address
            if not tinv.company_tax_address:
                frappe.throw(_('No Company Billing/Tax Address'))

        update_company_tax_address(voucher, tinv)

        # Sales Invoice - use Sales Tax Invoice as Tax Invoice
        # Purchase Invoice - use Bill No as Tax Invoice
        if doctype == 'Sales Tax Invoice':
            voucher.tax_invoice_number = tinv.name
            voucher.tax_invoice_date = tinv.date
            tinv.report_date = tinv.date
        if doctype == 'Purchase Tax Invoice':
            if not (voucher.tax_invoice_number and voucher.tax_invoice_date):
                frappe.throw(_('Please enter Tax Invoice Number / Tax Invoice Date'))
            voucher.save()
            tinv.number = voucher.tax_invoice_number
            tinv.report_date = tinv.date = voucher.tax_invoice_date
        voucher.save()
        tinv.save()
        return tinv

    # Auto create Tax Invoice only when account equal to tax account.
    setting = frappe.get_doc('Tax Invoice Settings')
    doctype = False
    tax_amount = 0.0
    voucher = frappe.get_doc(doc.voucher_type, doc.voucher_no)
    is_return = False
    if doc.voucher_type in ['Sales Invoice', 'Purchase Invoice']:
        is_return = voucher.is_return  # Case Debit/Credit Note
    sign = is_return and -1 or 1
    # Tax amount, use Dr/Cr to ensure it support every case
    if doc.account in [setting.sales_tax_account, setting.purchase_tax_account]:
        tax_amount = doc.credit - doc.debit
        if (tax_amount > 0 and not is_return) or (tax_amount < 0 and is_return):
            doctype = 'Sales Tax Invoice'
        if (tax_amount < 0 and not is_return) or (tax_amount > 0 and is_return):
            doctype = 'Purchase Tax Invoice'
        tax_amount = abs(tax_amount) * sign
    if doctype:
        voucher = frappe.get_doc(doc.voucher_type, doc.voucher_no)
        if voucher.docstatus == 2:
            tax_amount = 0
        if tax_amount != 0:
            # Base amount, use base amount from origin document
            if voucher.doctype == 'Expense Claim':
                base_amount = voucher.base_amount_overwrite or voucher.total_sanctioned_amount
            elif voucher.doctype in ['Purchase Invoice', 'Sales Invoice']:
                base_amount = voucher.base_net_total
            elif voucher.doctype == 'Payment Entry':
                base_amount = voucher.tax_base_amount
            elif voucher.doctype == 'Journal Entry':
                base_amount = voucher.tax_base_amount
            base_amount = abs(base_amount) * sign
            # Validate base amount
            tax_rate = frappe.get_cached_value('Account', doc.account, 'tax_rate')
            if round(base_amount * tax_rate/100) != round(tax_amount):
                frappe.throw(_(
                    'Tax should be {0}% of the base amount<br/>'
                    '<b>Note:</b> To correct base amount, fill in Base Amount Overwrite.'.format(tax_rate)
                ))
            tinv = create_tax_invoice(doc, doctype, base_amount, tax_amount, voucher)
            tinv = update_voucher_tinv(doctype, voucher, tinv)
            tinv.submit()


def validate_company_address(doc, method):
    if not doc.company_tax_address:
        addresses = frappe.db.get_all(
            'Address',
            filters={'is_your_company_address': 1, 'address_type': 'Billing'},
            fields=['name', 'address_type'],
        )
        if len(addresses) == 1:
            doc.company_tax_address = addresses[0]['name']


def validate_tax_invoice(doc, method):
    # If taxes contain tax account, tax invoice is required.
    tax_account = frappe.db.get_single_value('Tax Invoice Settings', 'purchase_tax_account')
    voucher = frappe.get_doc(doc.doctype, doc.name)
    for tax in voucher.taxes:
        if tax.account_head == tax_account and not doc.tax_invoice_number:
            frappe.throw(_('This document require Tax Invoice Number'))
 

def get_uncleared_tax_amount(gl_name, payment_type):
    or_filters = {'name': gl_name, 'against_gl_entry': gl_name}
    uncleared_gl = frappe.db.get_all(
        'GL Entry', or_filters=or_filters, fields=['debit_in_account_currency', 'credit_in_account_currency'],
    )
    uncleared_tax = sum([x.debit_in_account_currency - x.credit_in_account_currency for x in uncleared_gl])
    if payment_type == 'Receive':
        uncleared_tax = -uncleared_tax
    if uncleared_tax < 0:
        uncleared_tax = 0
    return uncleared_tax


def get_clear_undue_tax_je(payment_no):
    je = frappe.db.get_all(
        'Journal Entry',
        filters={'docstatus': 1, 'for_payment': payment_no}
    )
    return je and je[0]['name']

@frappe.whitelist()
def to_clear_undue_tax(dt, dn):
    to_clear = True
    if get_clear_undue_tax_je(dn):
        to_clear = False
    if not get_clear_vat_journal_entry(dt, dn):
        to_clear = False
    return to_clear

@frappe.whitelist()
def get_clear_vat_journal_entry(dt, dn):
    tax_setting = frappe.get_single('Tax Invoice Settings')
    pay = frappe.get_doc(dt, dn)
    je = frappe.new_doc('Journal Entry')
    je.entry_type = 'Journal Entry'
    je.supplier = pay.party
    je.company_tax_address = pay.company_tax_address
    je.for_payment = pay.name
    je.user_remark = _('Clear Undue Tax on %s' % pay.name)
    # Loop through all paid doc, pick only ones with Undue Tax
    base_total = 0
    tax_total = 0
    for ref in pay.references:
        if not ref.allocated_amount or not ref.total_amount:
            continue
        alloc_percent = ref.allocated_amount / ref.total_amount
        # Find gl entry of ref doc that has undue amount
        gl_entries = frappe.db.get_all(
            'GL Entry',
            filters={
                'voucher_type': ref.reference_doctype,
                'voucher_no': ref.reference_name,
            },
            fields=[
                'name', 'account',
                'debit_in_account_currency',
                'credit_in_account_currency',
            ])
        for gl in gl_entries:
            # Find Base
            report_type = frappe.get_cached_value('Account', gl['account'], 'report_type')
            if report_type == 'Profit and Loss':
                base_amount = alloc_percent * gl['debit_in_account_currency']
                base_total += base_amount
            # Find Tax
            if gl['account'] == tax_setting.purchase_tax_account_undue:
                undue_tax = alloc_percent * gl['debit_in_account_currency']
                undue_remain = get_uncleared_tax_amount(gl['name'], 'Pay')
                undue_tax = undue_tax if undue_tax < undue_remain else undue_remain
                if not undue_tax:
                    continue
                je.append('accounts',
                    {
                        'account': tax_setting.purchase_tax_account_undue,
                        'credit_in_account_currency': undue_tax,
                        'against_gl_entry': gl['name'],
                    },
                )
                tax_total += undue_tax
    if not tax_total:
        return False
    # To due tax
    je.append('accounts',
        {
            'account': tax_setting.purchase_tax_account,
            'debit_in_account_currency': tax_total
        }
	)
    # Base amount
    je.tax_base_amount = base_total
    return je

def clear_sales_invoice_undue_tax(doc, method):
    if doc.payment_type != 'Receive':
        return
    old_doc = doc.get_doc_before_save()
    if old_doc and old_doc.total_allocated_amount == doc.total_allocated_amount:
        return
    doc.taxes = []
    tax_setting = frappe.get_single('Tax Invoice Settings')
    base_total = 0
    tax_total = 0
    for ref in doc.references:
        if not ref.allocated_amount or not ref.total_amount:
            continue
        alloc_percent = ref.allocated_amount / ref.total_amount
        # Find gl entry of ref doc that has undue amount
        gl_entries = frappe.db.get_all(
            'GL Entry',
            filters={
                'voucher_type': ref.reference_doctype,
                'voucher_no': ref.reference_name,
            },
            fields=[
                'name', 'account',
                'debit_in_account_currency',
                'credit_in_account_currency',
            ])
        for gl in gl_entries:
            # Find Base
            report_type = frappe.get_cached_value('Account', gl['account'], 'report_type')
            if report_type == 'Profit and Loss':
                base_amount = alloc_percent * gl['credit_in_account_currency']
                base_total += base_amount
            # Find Tax
            if gl['account'] == tax_setting.sales_tax_account_undue:
                undue_tax = alloc_percent * gl['credit_in_account_currency']
                undue_remain = get_uncleared_tax_amount(gl['name'], 'Receive')
                undue_tax = undue_tax if undue_tax < undue_remain else undue_remain
                if not undue_tax:
                    continue
                doc.append('taxes',
                    {
                        'add_deduct_tax': 'Deduct',
                        'description': 'Clear Undue Tax',
                        'charge_type': 'Actual',
                        'account_head': tax_setting.sales_tax_account_undue,
                        'tax_amount': undue_tax,
                        'against_gl_entry': gl['name'],
                    },
                )
                tax_total += undue_tax
    if not tax_total:
        return
    # To due tax
    doc.append('taxes',
        {
            'add_deduct_tax': 'Add',
            'description': 'Clear Undue Tax',
            'charge_type': 'Actual',
            'account_head': tax_setting.sales_tax_account,
            'tax_amount': tax_total,
        },
	)
    doc.tax_base_amount = base_total
    doc.calculate_taxes()
