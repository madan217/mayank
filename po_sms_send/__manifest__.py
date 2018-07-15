# -*- coding: utf-8 -*-

{
    'name': 'SMS Send On Confirm PO',
    'description': """
    """,
    'version': '10.0.1.0',
 	'summary': '',
	'sequence': 1,
    'category': 'purchase',

    'author': '',
    'website': '',
	
    'depends': [
        'purchase', 'sms_frame'
    ],

    'data': [
        'data/sms_template.xml'
        ],
	'images' : [],
 	'demo': [],
    'qweb': [],

    'application': False,
    'installable': True,
	'auto_install': False,
}

