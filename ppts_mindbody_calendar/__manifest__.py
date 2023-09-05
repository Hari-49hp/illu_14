# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: MindBody In Odoo',
    'version': '1.1',
    'category': 'Marketing/Events',
    'sequence': 140,
    'summary': 'Publish events, sell tickets',
    'website': 'https://www.odoo.com/page/events',
    'description': "",
    'depends': [
        'base',
        'calendar',
        'event',
        'website',
        'website_partner',
        'sale_management',
        'website_mail',
        'website_event',
        'website_event_sale',
        'ppts_employee_availability'
    ],
    'data': [
        'templates/assets.xml',
        'templates/time.xml',
        'templates/calendar.xml',
        'templates/pos.xml',
        'templates/room.xml',
        'templates/room_book_form.xml',


        'views/event.xml',
        'views/calendar.xml',
        'views/model.xml',
        'views/form.xml',
        'views/popover.xml',
        'views/navbar.xml',
            ],
    'application': True,
}
