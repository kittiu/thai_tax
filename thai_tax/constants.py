ERP_CUSTOM_FIELDS = {
    "Payment Entry": [

 {"depends_on": "eval:doc.payment_type=='Pay'",
  "fieldname": "has_purchase_tax_invoice",
  "fieldtype": "Check",
  "insert_after": "payment_order_status",
  "label": "Has Purchase Tax Invoice",
 },
 {
  "fieldname": "tax_invoice",
  "fieldtype": "Tab Break",
  "insert_after": "title",
  "label": "Tax Invoice",
 },
 {

  "fieldname": "company_tax_address",
  "fieldtype": "Link",
  "insert_after": "tax_invoice",
  "label": "Company Tax Address",
  "options": "Address",
 },
 {

  "fieldname": "column_break_bqyze",
  "fieldtype": "Column Break",
  "insert_after": "company_tax_address",
 },
 {

  "fieldname": "tax_base_amount",
  "fieldtype": "Float",
  "insert_after": "column_break_bqyze",
  "label": "Tax Base Amount",
 },
 {

  "fieldname": "section_break_owjbn",
  "fieldtype": "Section Break",
  "insert_after": "tax_base_amount",
 },
 {
  "allow_on_submit": 1,
  "fieldname": "tax_invoice_number",
  "fieldtype": "Data",
  "in_standard_filter": 1,
  "insert_after": "section_break_owjbn",
  "label": "Tax Invoice Number",
  "no_copy": 1,
  "read_only_depends_on": "eval:doc.docstatus!=0",
 },
 {
  "allow_on_submit": 1,
  "depends_on": "eval:doc.party_type=='Employee'",
  "fieldname": "supplier",
  "fieldtype": "Link",
  "insert_after": "tax_invoice_number",
  "label": "Supplier",
  "no_copy": 1,
  "options": "Supplier",
 },
 {

  "fieldname": "column_break_yio5c",
  "fieldtype": "Column Break",
  "insert_after": "supplier",
 },
 {
  "allow_on_submit": 1,
  "fieldname": "tax_invoice_date",
  "fieldtype": "Date",
  "insert_after": "column_break_yio5c",
  "label": "Tax Invoice Date",
  "no_copy": 1,
  "read_only_depends_on": "eval:doc.docstatus!=0",
 },
 {
  "allow_on_submit": 1,
  "depends_on": "eval:doc.party_type=='Employee'",
  "fetch_from": "supplier.supplier_name",
  "fieldname": "supplier_name",
  "fieldtype": "Data",
  "insert_after": "tax_invoice_date",
  "label": "Supplier Name",
  "no_copy": 1,
  "translatable": 1,
 },
    ],
    "Payment Entry Deduction": [
{
  "fieldname": "custom_section_break_s4fwa",
  "fieldtype": "Section Break",
  "insert_after": "description",
 },
 {"fieldname": "custom_withholding_tax_type",
  "fieldtype": "Link",
  "insert_after": "custom_section_break_s4fwa",
  "label": "Withholding Tax Type",
  "options": "Withholding Tax Type",
 },
 {
  "fieldname": "custom_column_break_lx8hk",
  "fieldtype": "Column Break",
  "insert_after": "custom_withholding_tax_type",
 },
 {
    "fieldname": "custom_withholding_tax_base",
  "fieldtype": "Float",
  "insert_after": "custom_column_break_lx8hk",
  "label": "Withholding Tax Base",
 },


    ],
    "Supplier": [
       
 {
"default": "00000",
  "fieldname": "branch_code",
  "fieldtype": "Data",
  "insert_after": "irs_1099",
  "label": "Branch Code",
 },
 {
  "fieldname": "custom_wht",
  "fieldtype": "Section Break",
  "insert_after": "tax_withholding_category",
  "label": "WHT",
 },
 {
  "fieldname": "custom_default_income_tax_form",
  "fieldtype": "Select",
  "insert_after": "custom_wht",
  "label": "Default Income Tax Form",
  "options": "\nPND3\nPND53",
 },
 {
  "fieldname": "custom_column_break_7q1md",
  "fieldtype": "Column Break",
  "insert_after": "custom_default_income_tax_form",
 }, 
    ],
    "Customer": [
        
 {
  "default": "00000",
  "fieldname": "branch_code",
  "fieldtype": "Data",
  "insert_after": "tax_id",
  "label": "Branch Code",
 },
    ],
    "Journal Entry": [
        
 {"fieldname": "tax_invoice",
  "fieldtype": "Tab Break",
  "insert_after": "auto_repeat",
  "label": "Tax Invoice",
 },
 {
  "fieldname": "company_tax_address",
  "fieldtype": "Link",
  "insert_after": "tax_invoice",
  "label": "Company Tax Address",
  "options": "Address",
 },
 {
  "fieldname": "column_break_3djv9",
  "fieldtype": "Column Break",
  "insert_after": "company_tax_address",
 },
 {
  "fieldname": "for_payment",
  "fieldtype": "Link",
  "insert_after": "column_break_3djv9",
  "label": "For Payment",
  "options": "Payment Entry",
 },
 {
  "fieldname": "section_break_pxm0e",
  "fieldtype": "Section Break",
  "insert_after": "for_payment",
 },
 {
  "fieldname": "tax_invoice_details",
  "fieldtype": "Table",
  "insert_after": "section_break_pxm0e",
  "label": "Tax Invoice Details",
  "no_copy": 1,
  "options": "Journal Entry Tax Invoice Detail",
 },
    ],
    "Sales Invoice": [

 {
  "fieldname": "tax_invoice",
  "fieldtype": "Tab Break",
  "insert_after": "total_billing_amount",
  "label": "Tax Invoice",
 },
 {
  "allow_on_submit": 1,
  "fieldname": "tax_invoice_number",
  "fieldtype": "Data",
  "in_list_view": 1,
  "in_standard_filter": 1,
  "insert_after": "tax_invoice",
  "label": "Tax Invoice Number",
  "no_copy": 1,
 },
 {
  "fieldname": "column_break_cijbv",
  "fieldtype": "Column Break",
  "insert_after": "tax_invoice_number",
 },
 {
  "allow_on_submit": 1,
  "fieldname": "tax_invoice_date",
  "fieldtype": "Date",
  "insert_after": "column_break_cijbv",
  "label": "Tax Invoice Date",
  "no_copy": 1,
 },
    ],
    "Purchase Invoice": [

 {
  "fieldname": "tax_invoice",
  "fieldtype": "Tab Break",
  "insert_after": "supplied_items",
  "label": "Tax Invoice",
 },
 {
  "allow_on_submit": 1,
  "fieldname": "tax_invoice_number",
  "fieldtype": "Data",
  "in_list_view": 1,
  "in_standard_filter": 1,
  "insert_after": "tax_invoice",
  "label": "Tax Invoice Number",
  "no_copy": 1,
  "read_only_depends_on": "eval:doc.docstatus!=0",
 },
 {
  "fieldname": "column_break_t0qgt",
  "fieldtype": "Column Break",
  "insert_after": "tax_invoice_number",
 },
 {
  "allow_on_submit": 1,
  "fieldname": "tax_invoice_date",
  "fieldtype": "Date",
  "insert_after": "column_break_t0qgt",
  "label": "Tax Invoice Date",
  "no_copy": 1,
  "read_only_depends_on": "eval:doc.docstatus!=0",
 },

    ],
    "Item": [

 {
  "fieldname": "custom_section_break_6buh1",
  "fieldtype": "Section Break",
  "insert_after": "taxes",
 },
 {
  "description": "Select withholding tax type for service item to be deducted during payment.",
  "fieldname": "custom_withholding_tax_type",
  "fieldtype": "Link",
  "insert_after": "custom_section_break_6buh1",
  "label": "Withholding Tax Type",
  "options": "Withholding Tax Type",
 },

    ],
    "Purchase Invoice Item": [

 {
  "description": "Default Withholding Tax Type setup on Item",
  "fetch_from": "item_code.custom_withholding_tax_type",
  "fetch_if_empty": 1,
  "fieldname": "custom_withholding_tax_type",
  "fieldtype": "Link",
  "insert_after": "item_tax_template",
  "label": "Withholding Tax Type",
  "options": "Withholding Tax Type",
  "print_hide": 1,
  "read_only": 1,
 },

    ],
    "Sales Invoice Item": [

 {
  "description": "Default Withholding Tax Type setup on Item",
  "fetch_from": "item_code.custom_withholding_tax_type",
  "fetch_if_empty": 1,
  "fieldname": "custom_withholding_tax_type",
  "fieldtype": "Link",
  "insert_after": "item_tax_template",
  "label": "Withholding Tax Type",
  "options": "Withholding Tax Type",
  "print_hide": 1,
  "read_only": 1,
 },

    ],
    "Journal Entry Account": [

 {
  "collapsible": 1,
  "depends_on": "eval:doc.account_type == 'Tax'",
  "fieldname": "overwrite_tax_invoice",
  "fieldtype": "Section Break",
  "insert_after": "credit",
  "label": "Overwrite Tax Invoice",
 },
 {
  "fieldname": "tax_invoice_number",
  "fieldtype": "Data",
  "insert_after": "overwrite_tax_invoice",
  "label": "Tax Invoice Number",
 },
 {
  "fieldname": "tax_invoice_date",
  "fieldtype": "Date",
  "insert_after": "tax_invoice_number",
  "label": "Tax Invoice Date",
 },
 {
  "fieldname": "column_break_cun7x",
  "fieldtype": "Column Break",
  "insert_after": "tax_invoice_date",
 },
 {
  "fieldname": "supplier",
  "fieldtype": "Link",
  "insert_after": "column_break_cun7x",
  "label": "Supplier",
  "options": "Supplier",
 },
 {
  "fieldname": "customer",
  "fieldtype": "Link",
  "insert_after": "supplier",
  "label": "Customer",
  "options": "Customer",
 },
 {
  "description": "Leave this value to 0 and system will auto calculate based on tax rate.",
  "fieldname": "tax_base_amount",
  "fieldtype": "Float",
  "insert_after": "customer",
  "label": "Tax Base Amount",
 },

    ]
}

HRMS_CUSTOM_FIELDS = {
    "Expense Claim": [
        {
            "fieldname": "tax_invoice",
            "fieldtype": "Tab Break",
            "insert_after": "advances",
            "label": "Tax Invoice",
        },
        {
            "allow_on_submit": 1,
            "fieldname": "company_tax_address",
            "fieldtype": "Link",
            "insert_after": "tax_invoice",
            "label": "Company Tax Address",
            "options": "Address",
        },
        {
            "fieldname": "column_break_rqacr",
            "fieldtype": "Column Break",
            "insert_after": "company_tax_address",
        },
        {
            "description": "Use this field only when you want to overwrite",
            "fieldname": "base_amount_overwrite",
            "fieldtype": "Currency",
            "label": "Base Amount Overwrite",
            "no_copy": 1,
            "options": "Company:company:default_currency",
        },
        {
            "fieldname": "section_break_uodhb",
            "fieldtype": "Section Break",
            "insert_after": "base_amount_overwrite",
        },
        {
            "allow_on_submit": 1,
            "fieldname": "tax_invoice_number",
            "fieldtype": "Data",
            "in_standard_filter": 1,
            "insert_after": "section_break_uodhb",
            "label": "Tax Invoice Number",
            "read_only_depends_on": "eval:doc.docstatus!=0",
        },
        {
            "allow_on_submit": 1,
            "fieldname": "supplier",
            "fieldtype": "Link",
            "insert_after": "tax_invoice_number",
            "label": "Supplier",
            "no_copy": 1,
            "options": "Supplier",
        },
        {
            "fieldname": "column_break_6atpw",
            "fieldtype": "Column Break",
            "insert_after": "supplier",
        },
        {
            "allow_on_submit": 1,
            "fieldname": "tax_invoice_date",
            "fieldtype": "Date",
            "insert_after": "column_break_6atpw",
            "label": "Tax Invoice Date",
            "no_copy": 1,
            "read_only_depends_on": "eval:doc.docstatus!=0",
        },
        {
            "allow_on_submit": 1,
            "fetch_from": "supplier.supplier_name",
            "fieldname": "supplier_name",
            "fieldtype": "Data",
            "insert_after": "tax_invoice_date",
            "label": "Supplier Name",
            "no_copy": 1,
        },
    ],
}

ERP_PROPERTY_SETTERS = {
	"Purchase Taxes and Charges": [
		("rate", "precision", "6", "Select"),
	],
	"Sales Taxes and Charges": [
		("rate", "precision", "6", "Select"),
	],
	"Advance Taxes and Charges": [
		("rate", "precision", "6", "Select"),
	],
}