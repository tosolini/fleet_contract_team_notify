# Copyright 2026
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta
from odoo import fields
from odoo.tests.common import TransactionCase


class TestFleetContractTeamNotify(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create users
        cls.user1 = cls.env['res.users'].create({
            'name': 'Test User 1',
            'login': 'testuser1',
            'email': 'testuser1@example.com',
        })
        cls.user2 = cls.env['res.users'].create({
            'name': 'Test User 2',
            'login': 'testuser2',
            'email': 'testuser2@example.com',
        })
        
        # Create team
        cls.team = cls.env['fleet.contract.team'].create({
            'name': 'Test Team',
            'user_ids': [(6, 0, [cls.user1.id, cls.user2.id])],
        })
        
        # Create vehicle
        cls.brand = cls.env['fleet.vehicle.model.brand'].create({'name': 'Test Brand'})
        cls.model = cls.env['fleet.vehicle.model'].create({
            'name': 'Test Model',
            'brand_id': cls.brand.id,
        })
        cls.vehicle = cls.env['fleet.vehicle'].create({
            'model_id': cls.model.id,
            'license_plate': 'TEST123',
        })
        
        # Create contract type
        cls.contract_type = cls.env['fleet.service.type'].create({
            'name': 'Test Contract Type',
            'category': 'contract',
        })

    def test_team_users_computed_on_contract(self):
        """Test that notify_user_ids is automatically populated from team"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'expiration_date': fields.Date.today() + timedelta(days=30),
        })
        
        self.assertEqual(contract.notify_user_ids, self.team.user_ids)
        self.assertIn(self.user1, contract.notify_user_ids)
        self.assertIn(self.user2, contract.notify_user_ids)

    def test_followers_added_on_create(self):
        """Test that team members become followers when contract is created"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'expiration_date': fields.Date.today() + timedelta(days=30),
        })
        
        follower_partners = contract.message_follower_ids.mapped('partner_id')
        self.assertIn(self.user1.partner_id, follower_partners)
        self.assertIn(self.user2.partner_id, follower_partners)

    def test_followers_updated_on_team_change(self):
        """Test that followers are updated when team changes"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'expiration_date': fields.Date.today() + timedelta(days=30),
        })
        
        # Initially no team followers
        initial_followers = contract.message_follower_ids.mapped('partner_id')
        self.assertNotIn(self.user1.partner_id, initial_followers)
        
        # Assign team
        contract.write({'team_id': self.team.id})
        
        # Now team members should be followers
        updated_followers = contract.message_follower_ids.mapped('partner_id')
        self.assertIn(self.user1.partner_id, updated_followers)
        self.assertIn(self.user2.partner_id, updated_followers)

    def test_expiry_activities_creation(self):
        """Test that expiry activities are created for all team members"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'expiration_date': fields.Date.today() + timedelta(days=30),
        })
        
        contract._create_expiry_activities()
        
        # Check activities were created for both users
        activities = self.env['mail.activity'].search([
            ('res_id', '=', contract.id),
            ('res_model', '=', 'fleet.vehicle.log.contract'),
        ])
        
        activity_users = activities.mapped('user_id')
        self.assertIn(self.user1, activity_users)
        self.assertIn(self.user2, activity_users)

    def test_team_contract_count(self):
        """Test that team contract count is correctly computed"""
        initial_count = self.team.contract_count
        
        self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'expiration_date': fields.Date.today() + timedelta(days=30),
        })
        
        self.team._compute_contract_count()
        self.assertEqual(self.team.contract_count, initial_count + 1)

    def test_backward_compatibility_with_user_id(self):
        """Test that original user_id field still works without team"""
        single_user = self.env['res.users'].create({
            'name': 'Single User',
            'login': 'singleuser',
            'email': 'single@example.com',
        })
        
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'user_id': single_user.id,
            'expiration_date': fields.Date.today() + timedelta(days=30),
        })
        
        recipients = contract._get_expiry_notification_recipients()
        self.assertIn(single_user, recipients)
