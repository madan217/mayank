# -*- coding: utf-8 -*-

{
    'name': 'MRP RS Weighted Wires & Packaging Contractors',
    'description': """
    """,
    'version': '10.0.1.0',
 	'summary': '',
	'sequence': 1,
    'category': 'mrp',

    'author': '',
    'website': '',
	
    'depends': [
        'mrp',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/mrp_config_settings_views.xml',
        'views/mrp_view.xml',
        'wizard/contractor_cost.xml',
        'wizard/production_details.xml'
        ],
	'images' : [],
 	'demo': [],
    'qweb': [],

    'application': False,
    'installable': True,
	'auto_install': False,
}

