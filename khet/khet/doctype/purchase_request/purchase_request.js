// Copyright (c) 2025, amrendra and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Request', {
    refresh: function(frm) {
        // Show "Fulfill Request" button only if:
        // - It's in Draft
        // - Supplier is already assigned
        if (frm.doc.docstatus === 0 && frm.doc.supplier) {
            frm.add_custom_button(__('Fulfill Request'), function () {
                frappe.call({
                    method: "khet.khet.doctype.purchase_request.purchase_request.fulfill_request",
                    args: {
                        pr_name: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('Supplier Invoice {0} created').format(r.message));
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
    }
});
