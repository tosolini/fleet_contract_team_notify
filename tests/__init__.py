from . import test_fleet_contract_team_notify


class TestFleetContractTeamNotify(TransactionCase):
    """Test cases per fleet_contract_team_notify"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Crea utenti di test
        cls.user1 = cls.env['res.users'].create({
            'name': 'Test User 1',
            'login': 'testuser1',
            'email': 'user1@test.com',
        })
        cls.user2 = cls.env['res.users'].create({
            'name': 'Test User 2',
            'login': 'testuser2',
            'email': 'user2@test.com',
        })
        cls.user3 = cls.env['res.users'].create({
            'name': 'Test User 3',
            'login': 'testuser3',
            'email': 'user3@test.com',
        })
        
        # Crea partner di test
        cls.partner1 = cls.env['res.partner'].create({
            'name': 'External Partner 1',
            'email': 'partner1@test.com',
        })
        cls.partner2 = cls.env['res.partner'].create({
            'name': 'External Partner 2',
            'email': 'partner2@test.com',
        })
        
        # Crea team di test
        cls.team = cls.env['fleet.contract.team'].create({
            'name': 'Test Team',
            'description': 'Team per test',
            'user_ids': [(6, 0, [cls.user1.id, cls.user2.id, cls.user3.id])],
            'partner_ids': [(6, 0, [cls.partner1.id, cls.partner2.id])],
        })
        
        # Crea veicolo di test
        cls.vehicle = cls.env['fleet.vehicle'].create({
            'name': 'Test Vehicle',
            'license_plate': 'TEST123',
        })
        
        # Crea tipo contratto
        cls.contract_type = cls.env['fleet.service.type'].create({
            'name': 'Insurance',
            'category': 'contract',
        })

    def test_01_team_creation(self):
        """Test creazione team con membri"""
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(len(self.team.user_ids), 3)
        self.assertEqual(len(self.team.partner_ids), 2)
        self.assertTrue(self.team.active)

    def test_02_contract_team_assignment(self):
        """Test assegnazione team a contratto"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        # Verifica che gli utenti siano popolati automaticamente
        self.assertEqual(len(contract.notify_user_ids), 3)
        self.assertIn(self.user1, contract.notify_user_ids)
        self.assertIn(self.user2, contract.notify_user_ids)
        self.assertIn(self.user3, contract.notify_user_ids)

    def test_03_followers_added_on_create(self):
        """Test che i follower vengano aggiunti automaticamente alla creazione"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        # Verifica follower
        follower_partners = contract.message_follower_ids.mapped('partner_id')
        self.assertIn(self.user1.partner_id, follower_partners)
        self.assertIn(self.user2.partner_id, follower_partners)
        self.assertIn(self.user3.partner_id, follower_partners)

    def test_04_onchange_team(self):
        """Test onchange del team"""
        contract = self.env['fleet.vehicle.log.contract'].new({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
        })
        
        # Simula onchange
        contract.team_id = self.team
        contract._onchange_team_id()
        
        # Verifica che gli utenti siano popolati
        self.assertEqual(len(contract.notify_user_ids), 3)

    def test_05_change_team(self):
        """Test cambio team su contratto esistente"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        # Crea nuovo team
        new_team = self.env['fleet.contract.team'].create({
            'name': 'New Team',
            'user_ids': [(6, 0, [self.user1.id])],
        })
        
        # Cambia team
        contract.write({'team_id': new_team.id})
        
        # Verifica che gli utenti siano aggiornati
        self.assertEqual(len(contract.notify_user_ids), 1)
        self.assertIn(self.user1, contract.notify_user_ids)

    def test_06_contract_without_team(self):
        """Test retrocompatibilità: contratto senza team usa solo user_id"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'user_id': self.user1.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        # Verifica che non ci siano utenti notify
        self.assertEqual(len(contract.notify_user_ids), 0)
        # Ma user_id deve funzionare
        self.assertEqual(contract.user_id, self.user1)

    def test_07_expiry_notification_recipients(self):
        """Test lista destinatari per notifiche scadenza"""
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'user_id': self.user1.id,
            'team_id': self.team.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        recipients = contract._get_expiry_notification_recipients()
        
        # Deve includere user_id + tutti i membri del team
        self.assertIn(self.user1, recipients)
        self.assertIn(self.user2, recipients)
        self.assertIn(self.user3, recipients)

    def test_08_team_contract_count(self):
        """Test conteggio contratti per team"""
        # Crea contratti
        self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=180),
        })
        
        # Verifica count
        self.team._compute_contract_count()
        self.assertEqual(self.team.contract_count, 2)

    def test_09_manual_notify_partners(self):
        """Test aggiunta manuale partner extra"""
        partner_extra = self.env['res.partner'].create({
            'name': 'Extra Partner',
            'email': 'extra@test.com',
        })
        
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'notify_partner_ids': [(6, 0, [partner_extra.id])],
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        # Verifica partner extra
        self.assertIn(partner_extra, contract.notify_partner_ids)
        
        # Verifica follower (deve includere anche partner extra)
        follower_partners = contract.message_follower_ids.mapped('partner_id')
        self.assertIn(partner_extra, follower_partners)

    def test_10_inactive_team(self):
        """Test team archiviato"""
        self.team.active = False
        self.assertFalse(self.team.active)
        
        # Può comunque essere usato su contratti esistenti
        contract = self.env['fleet.vehicle.log.contract'].create({
            'vehicle_id': self.vehicle.id,
            'cost_subtype_id': self.contract_type.id,
            'team_id': self.team.id,
            'start_date': fields.Date.today(),
            'expiration_date': fields.Date.today() + timedelta(days=365),
        })
        
        self.assertEqual(contract.team_id, self.team)
