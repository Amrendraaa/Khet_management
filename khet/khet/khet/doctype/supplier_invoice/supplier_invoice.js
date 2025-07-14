// Copyright (c) 2025, amrendra and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0 && frm.doc.payment_status !== "Cleared") {
            frm.add_custom_button(__('Mark as Cleared'), function () {
                frappe.call({
                    method: "khet.khet.doctype.supplier_invoice.supplier_invoice.mark_as_cleared",
                    args: {
                        invoice_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint("Marked as Cleared");
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
    }
});

