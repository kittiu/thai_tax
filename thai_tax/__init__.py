__version__ = "0.0.1"

# Monkey patching
# ------------------
import erpnext.accounts.doctype.gl_entry.gl_entry as gl_entry
import thai_tax.custom.monkey_patches as patch
gl_entry.rename_temporarily_named_docs = patch.rename_temporarily_named_docs
