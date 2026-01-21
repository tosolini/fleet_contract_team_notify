# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Fleet Contract Team Notify',
    'version': '18.0.1.0.0',
    'category': 'Fleet',
    'summary': 'Team-based notification system for fleet contracts',
    'description': """
        Extends fleet contract notification system by adding:
        - Configurable notification teams
        - Multiple recipients (internal users)
        - Automatic email CC
        - Automatic followers
        - Scheduler activities for expiry notifications
    """,
    'author': 'Community',
    'website': 'https://github.com/OCA/fleet',
    'license': 'LGPL-3',
    'depends': [
        'fleet',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_contract_team_views.xml',
        'views/fleet_vehicle_log_contract_views.xml',
        'data/mail_template_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
