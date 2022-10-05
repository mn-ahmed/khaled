
{
    'name': 'access card',
    'category': 'ESS',
    'description': """
                   ESS Requests.
                 """,
    'summary': 'Experience letter request,'
               'SIM Card request,'
               'SIM card rate plan request,'
               'Access Card Replacement Request'
               ,
    'author': 'Israa Elkolaly <<israa.elkolaly@bbi-consultancy.com>>',
    # 'website': 'http://www.bbi-consultancy.com',
    'images': [

    ],
    'depends': ['base','employees_self_services','hr'
                ],
    'images': [],
    'data': [

        'security/groups_rules.xml',
        'views/access_card_views.xml',
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
