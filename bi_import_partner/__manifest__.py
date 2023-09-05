# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
	'name': "Import Partner from Excel and CSV",
	'version': "14.0.0.1",
	'category': "Partner",
	'summary': "Apps helps to import partner from excel import partner from csv, import multiple partner, import bulk partner import from excel",
	'description':	"""
					import partner  import multiple partner  import bulk partner
					import partner from excel  import partner from xls
					import partner from csv  import multiple partner from xls and csv
					""",
	'author': "PPTS",
	'depends': ['base'],
	'data': [
				'security/ir.model.access.csv',
				'wizard/import_partner_view.xml',
				'views/import_partner_menu.xml',
			],
	'demo': [],
	'qweb': [],
	'installable': True,
	'auto_install': False,
	'application': True,
	"images":['static/description/icon.png'],
}

