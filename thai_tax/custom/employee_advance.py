import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import flt
from hrms.hr.doctype.employee_advance.employee_advance import EmployeeAdvance


class ThaiTaxEmployeeAdvance(EmployeeAdvance):

    # For python bug fix only, to be removed if fixed in the core
    def set_total_advance_paid(self):
        gle = frappe.qb.DocType("GL Entry")

        paid_amount = (
            frappe.qb.from_(gle)
            .select(Sum(gle.debit).as_("paid_amount"))
            .where(
                (gle.against_voucher_type == "Employee Advance")
                & (gle.against_voucher == self.name)
                & (gle.party_type == "Employee")
                & (gle.party == self.employee)
                & (gle.docstatus == 1)
                & (gle.is_cancelled == 0)
            )
        ).run(as_dict=True)[0].paid_amount or 0

        return_amount = (
            frappe.qb.from_(gle)
            .select(Sum(gle.credit).as_("return_amount"))
            .where(
                (gle.against_voucher_type == "Employee Advance")
                & (gle.voucher_type != "Expense Claim")
                & (gle.against_voucher == self.name)
                & (gle.party_type == "Employee")
                & (gle.party == self.employee)
                & (gle.docstatus == 1)
                & (gle.is_cancelled == 0)
            )
        ).run(as_dict=True)[0].return_amount or 0

        if paid_amount != 0:
            paid_amount = flt(paid_amount) / flt(self.exchange_rate)
        if return_amount != 0:
            return_amount = flt(return_amount) / flt(self.exchange_rate)

        if flt(paid_amount) > self.advance_amount:
            frappe.throw(
                _("Row {0}# Paid Amount cannot be greater than requested advance amount"),
                EmployeeAdvanceOverPayment,
            )

        # FIX: because python result in 2000.0-1780.2 = 219.79999999999995
        # if flt(return_amount) > self.paid_amount - self.claimed_amount:
        if flt(return_amount) > flt(self.paid_amount - self.claimed_amount, 4):
            frappe.throw(_("Return amount cannot be greater unclaimed amount"))

        self.db_set("paid_amount", paid_amount)
        self.db_set("return_amount", return_amount)
        self.set_status(update=True)
