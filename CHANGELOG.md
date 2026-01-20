# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [18.0.1.0.0] - 2026-01-20

### Added
- Initial release for Odoo 18.0 CE
- New model `fleet.contract.team` for configurable notification teams
- Extended `fleet.vehicle.log.contract` with team-based notifications
- Automatic follower subscription for team members
- Email templates for contract notifications
- UI views for team management and configuration
- Comprehensive test suite with 10 test cases
- English translations for all user-facing strings
- Security access rules for Fleet User and Fleet Manager groups

### Features
- Team-based notification system for fleet contracts
- Multiple internal user notifications
- Automatic follower management
- Backward compatibility with original `user_id` field
- Integration with Odoo mail system
- Configurable through user interface
- Search filters and grouping by team

### Technical
- Computed and stored `notify_user_ids` field for performance
- Override create/write methods for automatic follower subscription
- Methods for scheduler integration:
  - `_create_expiry_activities()`: Create activities for expiring contracts
  - `_send_expiry_notification_email()`: Send notification emails
  - `_get_expiry_notification_recipients()`: Get list of users to notify
- Proper access rights configuration
- Mail thread integration with automatic follower management
- Onchange methods for real-time UI updates

### Changed
- None (initial release)

### Deprecated
- None

### Removed
- None

### Fixed
- None (initial release)

### Security
- Access rights properly configured for Fleet groups
- Only Fleet Managers can create/delete teams
- Fleet Users can read and assign teams

## Future Enhancements

Potential features for future versions:

- [ ] Scheduler/cron integration for automatic expiry notifications
- [ ] Additional notification channels (SMS, push notifications)
- [ ] Team templates and presets
- [ ] Advanced filtering and reporting
- [ ] Multi-company support
- [ ] Team hierarchy and escalation rules
- [ ] Custom notification rules per team
- [ ] Integration with calendar for expiry reminders
- [ ] Batch operations on multiple contracts
- [ ] Export/import team configurations

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

Tutte le modifiche rilevanti a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce a [Semantic Versioning](https://semver.org/lang/it/).

## [18.0.1.0.0] - 2026-01-20

### Aggiunto
- Nuovo modello `fleet.contract.team` per configurare team di notifica riutilizzabili
- Campo `team_id` su `fleet.vehicle.log.contract` per assegnare team ai contratti
- Campi `notify_user_ids` e `notify_partner_ids` per gestire destinatari multipli
- Follower automatici: membri del team vengono aggiunti automaticamente come follower
- Template email con supporto CC multipli per notifiche contratti
- Metodi per creazione attività di scadenza per tutti i membri del team
- Viste dedicate per gestione team (tree, form, search)
- Sezione "Team Notifiche" nel form contratti
- Filtri e raggruppamenti per team nelle viste contratti
- Menu configurazione in Fleet > Configurazione > Team Contratti
- Security/access rights per utenti e manager fleet
- Widget many2many_tags per visualizzazione intuitiva membri team
- Smart button per conteggio contratti nel form team
- Campo computed `contract_count` nel modello team
- Documentazione completa (README, SCHEDULER_INTEGRATION, ADVANCED_USAGE)
- Test unitari per tutte le funzionalità principali
- Template email per notifiche nuovi contratti
- Esempio scheduler cron per notifiche automatiche
- Tracking su campo `team_id` per audit trail

### Tecnico
- Dipendenze: `fleet`, `mail`
- Compatibilità: Odoo 18 CE
- Inherit di `fleet.vehicle.log.contract` preserva funzionalità esistenti
- Campo `user_id` originale mantenuto per retrocompatibilità
- Relazioni many2many con tabelle ponte dedicate
- Metodi hook per estensibilità: `_get_expiry_notification_recipients()`, `_create_expiry_activities()`, `_send_expiry_notification_email()`
- Override di `create()` e `write()` per gestione follower automatici
- Compute method con store=True su `notify_user_ids` per performance
- Onchange su `team_id` per user experience migliorata

### Caratteristiche Notifiche
- **Email**: CC automatici ai partner del team
- **Interne**: Follower automatici per notifiche Odoo
- **Attività**: Mail activities per reminder scadenze
- **Scheduler**: Supporto per cron automatici (esempio fornito)

### Documentazione
- README con guida installazione e utilizzo
- SCHEDULER_INTEGRATION con esempi integrazione cron
- ADVANCED_USAGE con casi d'uso avanzati
- Test unitari con 10 test cases
- Commenti inline nel codice
- Docstring su metodi pubblici

### Note Migrazione
Prima installazione - nessuna migrazione necessaria.
Compatibile con dati fleet esistenti.

## [Unreleased]

### Pianificato per future versioni
- Dashboard analytics per team con grafici scadenze
- Report PDF personalizzabile per contratti team
- Integrazione con moduli OCA fleet aggiuntivi
- Wizard per assegnazione massiva team a contratti
- Configurazione avanzata regole notifiche per tipo contratto
- Support multi-company con team company-specific
- API REST per integrazione sistemi esterni
- Mobile app notifiche push
- Workflow approvazione rinnovi contratti
- Budget tracking per team
