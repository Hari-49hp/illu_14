# Part of Softhealer Technologies.
{
    "name": "POS WhatsApp Integration",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point of sale",
    "license": "OPL-1",
    "summary": " Whatsapp Integration App,  POS To Customer Whatsapp Module, POS Order To Clients Whatsapp, Point Of Sale Whatsapp App, POS  Order Whatsapp, POS Whatsapp Odoo",
    "description": """
Nowadays, WhatsApp is frequently used. Many communications take place on WhatsApp. Currently, in Odoo there is no feature where you can send POS(Point Of Sale) direct to partner's WhatsApp. Our module will provide that feature. You need to just one-time login in WhatsApp, after that, you can send POS to direct or manually to partner's WhatsApp. You can track sent messages in chatter.""",
    "version": "14.0.2",
    "depends": ['base', 'point_of_sale'],
    "application": True,
    "data": [
        "views/res_users_inherit_view.xml",
            "views/views.xml",
            "views/templates.xml"
    ],
    "qweb": ["static/src/xml/*.xml"],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
}
