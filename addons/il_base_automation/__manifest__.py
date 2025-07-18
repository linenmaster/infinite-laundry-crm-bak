# -*- coding: utf-8 -*-
{
    'name': "Infinite Laundry - Base Automation",
    'summary': """ Base Automation Customization """,
    'description': """ Base Automation Customization """,
    'author': "Tilsol",
    # Categories can be used to filter modules in modules listing

    # for the full list
    'category': 'base',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['base_automation','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/automation_security.xml',
        'views/base_automation_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    "application": True,
    "installable": True,
    'auto_install': True,
}