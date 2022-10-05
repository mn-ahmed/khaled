
{
    'name': 'ESS Requests',
    'category': 'ESS',
    'description': """
                   ess requests.
                 """,
    'summary': 'Experience letter request,'
               'SIM Card request,'
               'SIM card rate plan request '
               ,
    'author': 'Israa Elkolaly <<israa.elkolaly@bbi-consultancy.com>>',
    # 'website': 'http://www.bbi-consultancy.com',
    'images': [

    ],
    'depends': ['base','employees_self_services','hr','hiring_and_resign'
                ],
    'images': [],
    'data': [

        #experience_letter_request
        'experience_letter/security/ir.model.access.csv',
        'experience_letter/security/groups_rules.xml',
        'experience_letter/views/experience_letter_views.xml',
        'experience_letter/views/templates.xml',
        'experience_letter/data/sequence.xml',
        #sim_card_request
        'sim_card_request/security/ir.model.access.csv',
        'sim_card_request/security/groups_rules.xml',
        'sim_card_request/views/sim_card_views.xml',
        'sim_card_request/views/templates.xml',
        'sim_card_request/data/sequence.xml',
        'sim_card_request/views/sim_card_change_view.xml',
        'sim_card_request/views/sim_change_template.xml',

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
