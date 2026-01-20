#!/usr/bin/env python3
"""
Script di validazione installazione fleet_contract_team_notify

Usage:
    python3 validate_installation.py

Questo script verifica che tutti i file necessari siano presenti
e che la struttura del modulo sia corretta.
"""

import os
import sys
from pathlib import Path

# Colori per output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file(filepath, description):
    """Verifica esistenza file"""
    if os.path.exists(filepath):
        print(f"{GREEN}✓{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {filepath} {RED}MANCANTE{RESET}")
        return False

def check_directory(dirpath, description):
    """Verifica esistenza directory"""
    if os.path.isdir(dirpath):
        print(f"{GREEN}✓{RESET} {description}: {dirpath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {dirpath} {RED}MANCANTE{RESET}")
        return False

def validate_python_syntax(filepath):
    """Valida sintassi Python"""
    try:
        with open(filepath, 'r') as f:
            compile(f.read(), filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"{RED}  Errore sintassi: {e}{RESET}")
        return False

def validate_xml_syntax(filepath):
    """Valida sintassi XML"""
    try:
        import xml.etree.ElementTree as ET
        ET.parse(filepath)
        return True
    except ET.ParseError as e:
        print(f"{RED}  Errore XML: {e}{RESET}")
        return False

def main():
    """Main validation function"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Fleet Contract Team Notify - Validazione Installazione{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Determina base path
    script_dir = Path(__file__).parent.absolute()
    module_path = script_dir
    
    print(f"📁 Module path: {module_path}\n")
    
    errors = []
    warnings = []
    
    # ===== CHECK STRUTTURA BASE =====
    print(f"{YELLOW}[1/7] Verifica struttura base...{RESET}")
    
    base_files = [
        ('__init__.py', 'Init principale'),
        ('__manifest__.py', 'Manifest'),
        ('README.md', 'Documentazione'),
    ]
    
    for filename, desc in base_files:
        filepath = module_path / filename
        if not check_file(filepath, desc):
            errors.append(f"File mancante: {filename}")
    
    base_dirs = [
        ('models', 'Directory models'),
        ('views', 'Directory views'),
        ('security', 'Directory security'),
        ('data', 'Directory data'),
    ]
    
    for dirname, desc in base_dirs:
        dirpath = module_path / dirname
        if not check_directory(dirpath, desc):
            errors.append(f"Directory mancante: {dirname}")
    
    print()
    
    # ===== CHECK MODELS =====
    print(f"{YELLOW}[2/7] Verifica models...{RESET}")
    
    model_files = [
        'models/__init__.py',
        'models/fleet_contract_team.py',
        'models/fleet_vehicle_log_contract.py',
    ]
    
    for filename in model_files:
        filepath = module_path / filename
        if check_file(filepath, f"Model {filename}"):
            if not validate_python_syntax(filepath):
                errors.append(f"Errore sintassi Python: {filename}")
    
    print()
    
    # ===== CHECK VIEWS =====
    print(f"{YELLOW}[3/7] Verifica views...{RESET}")
    
    view_files = [
        'views/fleet_contract_team_views.xml',
        'views/fleet_vehicle_log_contract_views.xml',
    ]
    
    for filename in view_files:
        filepath = module_path / filename
        if check_file(filepath, f"View {filename}"):
            if not validate_xml_syntax(filepath):
                errors.append(f"Errore sintassi XML: {filename}")
    
    print()
    
    # ===== CHECK DATA =====
    print(f"{YELLOW}[4/7] Verifica data...{RESET}")
    
    data_files = [
        'data/mail_template_data.xml',
        'data/cron_data.xml',
    ]
    
    for filename in data_files:
        filepath = module_path / filename
        if check_file(filepath, f"Data {filename}"):
            if filename.endswith('.xml') and not validate_xml_syntax(filepath):
                errors.append(f"Errore sintassi XML: {filename}")
    
    print()
    
    # ===== CHECK SECURITY =====
    print(f"{YELLOW}[5/7] Verifica security...{RESET}")
    
    security_file = module_path / 'security/ir.model.access.csv'
    if check_file(security_file, "Access rights"):
        # Verifica che abbia almeno 2 righe (header + dati)
        with open(security_file, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                warnings.append("ir.model.access.csv sembra vuoto o incompleto")
            else:
                print(f"  {GREEN}→{RESET} {len(lines)-1} regole access rights trovate")
    
    print()
    
    # ===== CHECK TESTS =====
    print(f"{YELLOW}[6/7] Verifica tests...{RESET}")
    
    test_files = [
        'tests/__init__.py',
        'tests/test_fleet_contract_team_notify.py',
    ]
    
    test_dir = module_path / 'tests'
    if check_directory(test_dir, "Directory tests"):
        for filename in test_files:
            filepath = module_path / filename
            if check_file(filepath, f"Test {filename}"):
                if not validate_python_syntax(filepath):
                    errors.append(f"Errore sintassi Python: {filename}")
    else:
        warnings.append("Directory tests mancante - i test sono opzionali ma consigliati")
    
    print()
    
    # ===== CHECK DOCUMENTAZIONE =====
    print(f"{YELLOW}[7/7] Verifica documentazione...{RESET}")
    
    doc_files = [
        'README.md',
        'INSTALL.md',
        'CHANGELOG.md',
    ]
    
    optional_doc_files = [
        'doc/SCHEDULER_INTEGRATION.md',
        'doc/ADVANCED_USAGE.md',
        'PROJECT_SUMMARY.md',
    ]
    
    for filename in doc_files:
        filepath = module_path / filename
        if not check_file(filepath, f"Doc {filename}"):
            warnings.append(f"Documentazione mancante: {filename}")
    
    print(f"\n{BLUE}Documentazione opzionale:{RESET}")
    for filename in optional_doc_files:
        filepath = module_path / filename
        check_file(filepath, f"  {filename}")
    
    print()
    
    # ===== CHECK MANIFEST =====
    print(f"{YELLOW}Verifica manifest details...{RESET}")
    
    manifest_file = module_path / '__manifest__.py'
    if manifest_file.exists():
        with open(manifest_file, 'r') as f:
            manifest_content = f.read()
            
        required_keys = ['name', 'version', 'depends', 'data', 'installable']
        for key in required_keys:
            if f"'{key}'" in manifest_content or f'"{key}"' in manifest_content:
                print(f"{GREEN}✓{RESET} Manifest contiene '{key}'")
            else:
                errors.append(f"Manifest mancante chiave: {key}")
                
        # Check depends
        if "'fleet'" in manifest_content or '"fleet"' in manifest_content:
            print(f"{GREEN}✓{RESET} Dipendenza 'fleet' presente")
        else:
            errors.append("Dipendenza 'fleet' mancante nel manifest")
            
        if "'mail'" in manifest_content or '"mail"' in manifest_content:
            print(f"{GREEN}✓{RESET} Dipendenza 'mail' presente")
        else:
            warnings.append("Dipendenza 'mail' consigliata per notifiche")
    
    print()
    
    # ===== SUMMARY =====
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}RIEPILOGO VALIDAZIONE{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    if not errors and not warnings:
        print(f"{GREEN}✅ TUTTO OK!{RESET}")
        print(f"{GREEN}Il modulo è pronto per l'installazione.{RESET}\n")
        return 0
    
    if warnings:
        print(f"{YELLOW}⚠️  WARNINGS ({len(warnings)}):{RESET}")
        for warning in warnings:
            print(f"  {YELLOW}•{RESET} {warning}")
        print()
    
    if errors:
        print(f"{RED}❌ ERRORI ({len(errors)}):{RESET}")
        for error in errors:
            print(f"  {RED}•{RESET} {error}")
        print()
        print(f"{RED}Correggi gli errori prima di installare il modulo.{RESET}\n")
        return 1
    
    if warnings and not errors:
        print(f"{YELLOW}⚠️  Il modulo può essere installato ma con alcune avvertenze.{RESET}\n")
        return 0

if __name__ == '__main__':
    sys.exit(main())
