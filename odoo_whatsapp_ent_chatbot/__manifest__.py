# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
{
    "name": "Odoo WhatsApp Chatbot | Odoo V17 Enterprise Edition | WhatsApp Cloud API",
    "version": "17.0",
    "author": "TechUltra Solutions Private Limited",
    "category": "Discuss",
    "live_test_url": "https://www.youtube.com/playlist?list=PL8o8i9mlxsWivZfvRKeNHP_sXrgvEYD59",
    "website": "www.techultrasolutions.com",
    "category": "Discuss",
    "live_test_url": "https://www.youtube.com/playlist?list=PL8o8i9mlxsWivZfvRKeNHP_sXrgvEYD59",
    "company": "TechUltra Solutions Private Limited",
    "website": "https://www.techultrasolutions.com/",
    "summary": "Odoo Whatsapp Chatbot Integration, Interactive Templates, Buttons send through odoo on WhatsApp and Message Automation",
    "description": """
        Odoo Whatsapp Chatbot Integration,
        Interactive Templates,
        Buttons send through odoo on WhatsApp and Message Automation
        Odoo Chatbot
        Chatbot
        Odoo
        ERP
        Odoo ERP
        WhatsApp
        Whats-App
        Discuss
        App
        Community
        Odoo Whatsapp Chatbot
        Whatsapp Chatbot
        Odoo V17 Enterprise Edition
    """,
    "depends": ["whatsapp_extended"],
    "data": [
        "security/ir.model.access.csv",
        "data/wa_template.xml",
        "data/whatsapp_chatbot.xml",
        "views/whatsapp_chatbot_script_views.xml",
        "views/discuss_channel_views.xml",
        "views/whatsapp_chatbot_views.xml",
        "views/whatsapp_ir_action_views.xml",
        "views/whatsapp_account_inherit_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/odoo_whatsapp_ent_chatbot/static/src/scss/kanban_view.scss"
        ],
    },
    "images": ["static/description/main_screen.gif"],
    "price": 180,
    "currency": "USD",
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "OPL-1",
}
