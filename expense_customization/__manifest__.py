# -*- coding: utf-8 -*-

{
    'name': 'Expense To Submit Customization',
    'description': """
    
    1) Expense Module - Expense to Submit - Create New -

      a) Date -  make mandatory and default blank

      b) Add field Contractor Name - mandatory drop down from Contractor Labour table.

      c) Payment By  -  make default company
    """,
    'version': '10.0.1.0',
 	'summary': '',
	'sequence': 1,
    'category': 'expense',

    'author': '',
    'website': '',
	
    'depends': [
        'hr_expense','mrp_rs_weighted_wires_packaging_contractors'
    ],

    'data': [
        'expense.xml'
        ],
	'images' : [],
 	'demo': [],
    'qweb': [],

    'application': False,
    'installable': True,
	'auto_install': False,
}

