# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class FleetContractTeam(models.Model):
    _name = 'fleet.contract.team'
    _description = 'Fleet Contract Notification Team'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Team Name',
        required=True,
        translate=True,
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='fleet_contract_team_users_rel',
        column1='team_id',
        column2='user_id',
        string='Users to Notify',
        help='Internal users who will receive notifications for contracts assigned to this team',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    contract_count = fields.Integer(
        string='Contract Count',
        compute='_compute_contract_count',
    )

    @api.depends('user_ids')
    def _compute_contract_count(self):
        """Calculate the number of contracts assigned to this team"""
        for team in self:
            team.contract_count = self.env['fleet.vehicle.log.contract'].search_count([
                ('team_id', '=', team.id)
            ])

    def action_view_contracts(self):
        """Open the contracts view filtered by this team"""
        self.ensure_one()
        return {
            'name': 'Contracts',
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.log.contract',
            'view_mode': 'list,form',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id},
        }
