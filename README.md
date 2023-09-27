## Thai Tax

Additional tax functionality to comply with Thailand Tax regulation.

### 1. Tax Point on both Invoice and Payment
    
Tax Point determine when tax is recorded in general ledger. And on tax point, with Sales Tax Invoice or Purchase Tax Invoice will be created.

Trading of stockable product, tax point occur when deliver product and invoice is issued. The selling party will issue out document called "Delivery Note / Tax Invoice". And so Tax Invoice doctype got created when submit sales/purchase invoice.

For service, tax point occur when service is done and payment is made. When submit sales/purchase invoice, account ledger will record Undue Tax. Until when the seller get paid, it will then create Tax Invoice doctype on payment submission, in which account ledger will clear Undue Tax into Tax. The document issued from seller is called "Receipt / Tax Invoice"

### 2. Withholding Tax and Certificate

When a company purchase service from a supplier, when making payment, it is responsible to withhold (deduct) a tax amount (i.e., 3%) of invoice amount and issue out the Withholding Tax Certificate (pdf) to supplier.

### 3. Reports that require for submission to RD, i.e.,
    
- Purchase Tax Report, Sales Tax Report
- Withholding Tax Report (PND or ภงด)

### TODO:

- Thailand e-Tax Invoice, e-Withholding Tax

## Features

- Sales Tax and Undue Sales Tax
- Purchase Tax and Undue Purchase Tax
- Sales and Purchase Tax Report
- Withholding Tax on Payment (based on invoice amount before tax) and Withholding Tax Cert (pdf)
- Withholding Tax Report (PND3, PND53)
- Get Address by Tax ID

## Setup

### Installation

```
$ cd frappe-bench
$ bench get-app https://github.com/kittiu/thai_tax
$ bench install-app thai_tax
```

### Configurations

#### For Tax Invoice setup

1. In chart of account, make sure to have with Rate, i.e, 7% for Thailand Tax (Tax)
    - Sales Tax, Undue Sales Tax
    - Purchase Tax, Undue Purchase Tax
2. Open Tax Invoice Settings, and setup above taxes
3. Setup Sales / Purchase Taxes and Charges Template, we just want to make sure that,
    - When buy/sell product, Sales/Purchase Tax is record on invoice
    - When buy/sell service, Undue Sales/Purchase Tax is record on invoice, then on payment, clear Undue Tax and record Tax
4. Make sure you have setup Company's Billing Address, as it will be used for Tax Invoice
5. Make sure all Supplier/Customer have setup Billing Address, they will be used for Tax Invoice

Whenever Tax is recorded (with Tax Invoice and Tax Date), Sales/Purchase Tax Invoice will be created.

#### For Withholding Tax setup

1. In chart of account, make sure to have Withholding Tax Account
2. Create Withholding Tax Types (1%, 2%, 3% and 5%)

During payment, user will manually choose to deduct with one of these Withholding Tax Type, and then click button Create Withholding Tax cert with the deducted amount plus some additional deduction information.

-----------------------
#### License

MIT
