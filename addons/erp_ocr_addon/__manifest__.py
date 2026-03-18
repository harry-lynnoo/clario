{
    "name": "Clario OCR (Enterprise)",
    "version": "17.0.1.0.1",
    "category": "Accounting",
    "summary": "Enterprise-grade OCR automation for invoices and receipts",
    "author": "Clario",
    "maintainer": "Clario",
    "license": "OPL-1",
    # "price": 60.00,
    # "currency": "USD",

    "depends": [
        "base",
        "web",
        "mail",
        "account",
    ],

    "data": [
        "security/ir.model.access.csv",
        "data/ocr_sequences.xml",
        "views/actions.xml",
        "views/menus.xml",
        "views/dashboard.xml",
        "views/form.xml",
        "views/tree.xml",
        "views/search.xml",
        "views/invoice.xml",
        "views/receipt.xml",
        "views/res_config_settings_view.xml",
    ],

    "images": [
    "static/description/thumbnail.png",
    "static/description/screenshot1.png",
    "static/description/screenshot2.png",
    ],

    "application": True,
    "installable": True,
}