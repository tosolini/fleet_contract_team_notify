# Fleet Contract Team Notify

This module is for Odoo 18 CE to extend the fleet contract notification system with configurable teams.

## Features

### Core
- **Notification Teams**: Create reusable teams with internal users
- **Team Assignment**: Assign a team to each contract to manage notifications
- **Compatibility**: Maintains the original `user_id` field for backward compatibility

### Notifications
- **Multiple Email CC**: Team members automatically receive email notifications
- **Automatic Followers**: Team members are automatically added as contract followers
- **Activities**: System to create expiry activities for all team members
- **Email Templates**: Predefined templates for expiry and new contract notifications

### UI
- **Dedicated Section**: Contract form with "Team Notifications" section
- **Filters and Grouping**: List views with team filters
- **Configuration Menu**: Dedicated menu to manage teams
- **Tag Widgets**: Intuitive visualization with colored tags

## Structure

```
fleet_contract_team_notify/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── fleet_contract_team.py         # New team model
│   └── fleet_vehicle_log_contract.py  # Extend contracts
├── views/
│   ├── fleet_contract_team_views.xml
│   └── fleet_vehicle_log_contract_views.xml
├── data/
│   └── mail_template_data.xml         # Email templates
├── security/
│   └── ir.model.access.csv
├── tests/
│   └── test_fleet_contract_team_notify.py
└── README.md
```

## Models

### fleet.contract.team
New model to configure notification teams:

**Fields:**
- `name`: Team name (required)
- `description`: Description
- `user_ids`: Many2many with res.users (internal members)
- `active`: Active/archived flag
- `contract_count`: Computed field to count assigned contracts

### fleet.vehicle.log.contract (inherit)
Extends the contract model with:

**New Fields:**
- `team_id`: Many2one to fleet.contract.team
- `notify_user_ids`: Many2many computed from team users (store=True)

**Main Methods:**
- `_compute_notify_users()`: Automatically populates users from team
- `_onchange_team_id()`: Onchange to update recipients
- `_subscribe_team_members()`: Adds automatic followers
- `_get_expiry_notification_recipients()`: Returns list of users for notifications
- `_create_expiry_activities()`: Creates expiry activities for members
- `_send_expiry_notification_email()`: Sends emails with multiple CC

## Installation

### Method 1: Manual Installation
1. Copy the module to your Odoo addons directory
2. Restart Odoo server
3. Update apps list: Apps > Update Apps List
4. Search "Fleet Contract Team Notify"
5. Click Install

### Method 2: Command Line
```bash
odoo-bin -u fleet_contract_team_notify -d your_database_name
```

## Dependencies

- `fleet`: Standard Odoo Fleet module
- `mail`: Messaging and notification system

## Usage

### 1. Create a Team
1. Fleet > Configuration > Contract Teams
2. Create a new team specifying:
   - Name (e.g., "Maintenance Team")
   - Team Members: select internal users
   - Description (optional)

### 2. Assign Team to Contract
1. Fleet > Contracts > Open/Create contract
2. In the "Team Notifications" section:
   - Select the team
   - The "Users to Notify" field populates automatically
   - You can manually add additional users if needed

### 3. Automatic Notifications
Team members will receive:
- **Emails**: as CC when notifications are sent about the contract
- **Internal Notifications**: as followers of the contract
- **Activities**: expiry reminders (via scheduler)

## Scheduler/Cron (Example)

To integrate with existing scheduler, add in `data/cron_data.xml`:

```xml
<record id="ir_cron_contract_expiry_notify_team" model="ir.cron">
    <field name="name">Fleet: Contract Expiry Team Notification</field>
    <field name="model_id" ref="fleet.model_fleet_vehicle_log_contract"/>
    <field name="state">code</field>
    <field name="code">model._cron_contract_expiry_notify()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

And in the model:

```python
def _cron_contract_expiry_notify(self):
    """Scheduled action to notify expiries"""
    today = fields.Date.today()
    expiring = self.search([
        ('expiration_date', '<=', today + timedelta(days=30)),
        ('expiration_date', '>=', today),
        ('state', '!=', 'closed'),
    ])
    for contract in expiring:
        contract._create_expiry_activities()
        contract._send_expiry_notification_email()
```

## Testing

### Suggested Test Cases:
1. Create team with 3 users → Verify followers added to contract
2. Simulate expiry → Verify mail.activity created for all notify_user_ids
3. Send test email → Verify multiple CC in email
4. Change team → Verify onchange and followers update
5. Contract without team → Verify it uses only user_id (backward compatibility)

### Running Tests
```bash
odoo-bin -d test_db -i fleet_contract_team_notify --test-enable --stop-after-init
```

## Compatibility

- **Odoo 18 CE**: Tested and working
- **OCA Fleet Modules**: Compatible, doesn't override existing fields
- **Existing Data**: Preserved, the original `user_id` field remains functional

## Technical Notes

### Followers
Followers are automatically added in `create()` and `write()` when a team is set/modified.

### Email CC
The email template uses the `email_cc` field to include team members. The `_send_expiry_notification_email()` method can be called manually or from scheduler.

### Activities
Activities are created via `_create_expiry_activities()` with type `mail.mail_activity_data_warning` (standard Odoo warning).

### Store vs Compute
`notify_user_ids` is compute+store for performance, so searches on notified users are fast.

## License

LGPL-3.0 or later

## Credits

### Contributors
- Community contributors

### Maintainer
This module is maintained by the community. For issues or contributions, please use the GitHub repository.
