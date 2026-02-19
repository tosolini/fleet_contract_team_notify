# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo import api, fields, models


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    team_id = fields.Many2one(
        comodel_name='fleet.contract.team',
        string='Notification Team',
        help='Team of people who will receive notifications for this contract',
        tracking=True,
    )
    notify_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='fleet_contract_notify_users_rel',
        column1='contract_id',
        column2='user_id',
        string='Users to Notify',
        compute='_compute_notify_users',
        store=True,
        readonly=False,
        help='Internal users who will receive activities and notifications for this contract',
    )

    @api.depends('team_id', 'team_id.user_ids')
    def _compute_notify_users(self):
        """Automatically populate users from the selected team"""
        for contract in self:
            if contract.team_id:
                contract.notify_user_ids = contract.team_id.user_ids
            else:
                contract.notify_user_ids = False

    @api.onchange('team_id')
    def _onchange_team_id(self):
        """Onchange to update recipients when a team is selected"""
        if self.team_id:
            self.notify_user_ids = self.team_id.user_ids
        else:
            self.notify_user_ids = False

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically add followers"""
        contracts = super().create(vals_list)
        for contract in contracts:
            contract._subscribe_team_members()
            contract._send_new_contract_notification()
        return contracts

    def write(self, vals):
        """Override write to update followers if team changes"""
        res = super().write(vals)
        if 'team_id' in vals or 'notify_user_ids' in vals:
            self._subscribe_team_members()
            self._send_new_contract_notification()
        return res

    def _subscribe_team_members(self):
        """Add team members as contract followers"""
        for contract in self:
            partner_ids = []
            
            # Add partners of team users
            if contract.notify_user_ids:
                partner_ids.extend(contract.notify_user_ids.mapped('partner_id').ids)
            
            # Remove duplicates and subscribe
            if partner_ids:
                contract.message_subscribe(partner_ids=list(set(partner_ids)))

    def _get_expiry_notification_recipients(self):
        """
        Return the list of users who should receive activities for expiries.
        Includes user_id (original field) + all team members.
        """
        self.ensure_one()
        recipients = self.env['res.users']
        
        # Original user_id (for backward compatibility)
        if self.user_id:
            recipients |= self.user_id
        
        # Team members
        if self.notify_user_ids:
            recipients |= self.notify_user_ids
        
        return recipients

    def _create_expiry_activities(self, activity_type_xmlid='mail.mail_activity_data_warning'):
        """
        Create expiry activities for all configured recipients.
        Method to be called from cron or scheduler.
        """
        activity_type = self.env.ref(activity_type_xmlid, raise_if_not_found=False)
        if not activity_type:
            return
        
        for contract in self:
            recipients = contract._get_expiry_notification_recipients()
            for user in recipients:
                # Avoid duplicates
                existing = self.env['mail.activity'].search([
                    ('res_id', '=', contract.id),
                    ('res_model', '=', 'fleet.vehicle.log.contract'),
                    ('user_id', '=', user.id),
                    ('activity_type_id', '=', activity_type.id),
                    ('date_deadline', '=', contract.expiration_date),
                ], limit=1)
                
                if not existing:
                    self.env['mail.activity'].create({
                        'activity_type_id': activity_type.id,
                        'date_deadline': contract.expiration_date,
                        'summary': f'Contract expiry {contract.cost_subtype_id.name or ""}',
                        'note': f'The contract for vehicle {contract.vehicle_id.display_name} expires on {contract.expiration_date}',
                        'res_id': contract.id,
                        'res_model_id': self.env['ir.model']._get('fleet.vehicle.log.contract').id,
                        'user_id': user.id,
                    })

    def _send_expiry_notification_email(self, template_xmlid='fleet_contract_team_notify.mail_template_contract_expiry'):
        """
        Send notification email with multiple CCs to team members.
        Uses the configured template with automatic CCs.
        """
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            return
        
        for contract in self:
            # Send email to all team members
            template.send_mail(contract.id, force_send=False)

    def _send_new_contract_notification(self):
        """Send email when a new contract is created or a team is assigned."""
        template = self.env.ref('fleet_contract_team_notify.mail_template_contract_notification', raise_if_not_found=False)
        if not template:
            return

        for contract in self:
            if not contract.notify_user_ids:
                continue
            template.send_mail(contract.id, force_send=False)

    @api.model
    def _cron_notify_expiring_contracts(self, days=30, template_xmlid='fleet_contract_team_notify.mail_template_contract_expiry'):
        """Daily cron job to create activities and send expiry notifications."""
        today = fields.Date.today()
        deadline = today + timedelta(days=days)

        contracts = self.search([
            ('expiration_date', '>=', today),
            ('expiration_date', '<=', deadline),
            ('state', '!=', 'closed'),
            '|',
            ('team_id', '!=', False),
            ('user_id', '!=', False),
        ])

        for contract in contracts:
            contract._create_expiry_activities()
            contract._send_expiry_notification_email(template_xmlid=template_xmlid)
