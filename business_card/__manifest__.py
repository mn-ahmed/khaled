
{
    'name': 'Business card',
    'category': 'ESS',
    'description': """
                   ESS Requests.
                 """,
    'summary': 'Business card Request'
               ,
    'author': 'Israa Elkolaly <<israa.elkolaly@bbi-consultancy.com>>',
    # 'website': 'http://www.bbi-consultancy.com',
    'images': [

    ],
    'depends': ['base','employees_self_services',
                ],
    'images': [],
    'data': [

        'security/groups_rules.xml',
        'views/business_card_views.xml',
        'views/templates.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',


    ],
    'demo': [],
    # 'external_dependencies': {
    #     'python': [
    #         'numpy'
    #     ],
    # },
    'installable': True,
    'auto_install': False,
}
