# Insurance SOA System - Complete Documentation

**Version:** 1.0
**Last Updated:** November 2, 2025
**System Purpose:** Automated insurance Scope of Advice generation and Zapier integration

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Configuration](#configuration)
7. [Webhook Server](#webhook-server)
8. [Data Models](#data-models)
9. [Processors](#processors)
10. [Generators](#generators)
11. [Zapier Integration](#zapier-integration)
12. [Usage Guide](#usage-guide)
13. [Troubleshooting](#troubleshooting)

---

## System Overview

### What This System Does

The Insurance SOA (Scope of Advice) System is an automated pipeline that:

1. **Receives** insurance form submissions via webhooks from Gravity Forms
2. **Matches** fact find forms with automation forms by client email
3. **Processes** the combined data to extract structured insurance information
4. **Generates** comprehensive reports for all insurance types
5. **Triggers** Zapier webhooks with standardized, consistent payloads
6. **Stores** all form data and reports for record-keeping

### Key Features

- **Automatic Form Matching**: Intelligently pairs fact finds with automation forms
- **Multi-Insurance Support**: Life, Trauma, Income Protection, Health, Accidental Injury
- **Couple & Single Handling**: Processes both individual and couple applications
- **Zapier Integration**: Sends consistent, structured data to Zapier workflows
- **REST API**: Provides endpoints for manual generation and status checking
- **Data Persistence**: Saves all forms and reports to disk
- **Validation**: Ensures data quality and structure consistency

---

## Architecture

### High-Level Flow

```
┌─────────────────┐
│ Gravity Forms   │
│ (WordPress)     │
└────────┬────────┘
         │
         │ HTTP POST (Webhook)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│          Flask Webhook Server (Port 5001)               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  /ff - Fact Find Endpoint                         │  │
│  │  /automation - Automation Form Endpoint           │  │
│  └───────────────────────────────────────────────────┘  │
└────────┬────────────────────────────────────────────────┘
         │
         │ Save to Disk + Add to Matcher
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Form Matcher (In-Memory)                   │
│  • Matches forms by email                               │
│  • Calculates confidence scores                         │
│  • Triggers when both forms received                    │
└────────┬────────────────────────────────────────────────┘
         │
         │ When Match Found
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│          Auto Matcher & Processor                       │
│  • Loads raw form data                                  │
│  • Runs all generators                                  │
│  • Creates combined report                              │
└────────┬────────────────────────────────────────────────┘
         │
         │ Combined Report
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│          Zapier Payload Builder                         │
│  • Standardizes structure                               │
│  • Validates payload                                    │
│  • Ensures consistent fields                            │
└────────┬────────────────────────────────────────────────┘
         │
         │ Standardized Payload
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Zapier Trigger                             │
│  • Sends HTTP POST to Zapier webhook                   │
│  • Retries on failure                                   │
│  • Logs response                                        │
└────────┬────────────────────────────────────────────────┘
         │
         │ HTTP POST
         │
         ▼
┌─────────────────┐
│  Zapier Catch   │
│  Hook Trigger   │
└─────────────────┘
```

---

## File Structure

```
Insurance-SOA-main/
│
├── src/                                    # Source code directory
│   ├── webhook_server.py                  # Main Flask webhook server
│   ├── webhook_server_backup.py           # Backup of webhook server
│   ├── field_mapper.py                    # Maps Gravity Forms field IDs to semantic names
│   │
│   ├── models/                            # Data models
│   │   ├── __init__.py
│   │   ├── fact_find.py                   # Fact Find form model
│   │   └── automation_form.py             # Automation form model
│   │
│   ├── processors/                        # Data processors
│   │   ├── __init__.py
│   │   ├── form_matcher.py                # Matches fact finds with automation forms
│   │   ├── auto_matcher.py                # Automatic matching & Zapier trigger
│   │   ├── insurance_workflow.py          # Legacy workflow processor
│   │   ├── scope_of_advice_generator.py   # Generates scope of advice
│   │   ├── personal_information_extractor.py  # Extracts personal info
│   │   ├── assets_liabilities_extractor.py    # Extracts financial data
│   │   ├── life_insurance_extractor.py    # Extracts life/trauma insurance
│   │   ├── zapier_trigger.py              # Sends data to Zapier
│   │   └── zapier_payload_builder.py      # Builds standardized payloads
│   │
│   └── generators/                        # Insurance field generators
│       ├── life_insurance_fields.py       # Life insurance calculations
│       ├── trauma_insurance_fields.py     # Trauma insurance calculations
│       ├── income_protection_fields.py    # Income protection calculations
│       ├── health_insurance_fields.py     # Health insurance calculations
│       └── accidental_injury_fields.py    # ACC top-up calculations
│
├── config/                                # Configuration files
│   ├── field_mappings.yaml               # Fact find field mappings
│   ├── automation_form_mappings.yaml     # Automation form field mappings
│   ├── zapier_config.json                # Zapier webhook configuration
│   └── zapier_payload_schema.json        # Payload structure schema
│
├── data/                                  # Data storage
│   ├── forms/
│   │   ├── fact_finds/                   # Saved fact find submissions
│   │   │   ├── dan_at_icreatebuilding_nz_20251030_132708.json
│   │   │   ├── mitchwo_at_icloud_com_20251028_121444.json
│   │   │   └── ...
│   │   └── automation_forms/             # Saved automation form submissions
│   │       ├── dan_at_icreatebuilding_nz_20251030_141339.json
│   │       └── ...
│   └── reports/                          # Generated reports
│       └── ...
│
├── tests/                                # Test files
│   └── ...
│
├── examples/                             # Example usage
│   └── ...
│
├── Instructions/                         # Original documentation
│   ├── COMPLETE_DOCUMENTATION.md
│   ├── API_REFERENCE.md
│   ├── IMPLEMENTATION_GUIDE.md
│   └── CHANGELOG.md
│
├── main.py                               # Simple entry point
├── monitor_webhooks.sh                   # Webhook monitoring script
└── COMPLETE_SYSTEM_DOCUMENTATION.md      # This file
```

---

## Core Components

### 1. Webhook Server (`src/webhook_server.py`)

**Purpose**: Flask web server that receives form submissions and serves API endpoints

**Port**: 5001

**Key Features**:
- Receives Gravity Forms webhooks
- Loads existing forms on startup
- Provides REST API endpoints
- Automatically matches forms
- Triggers Zapier when matched

**Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ff` | POST | Receive Fact Find form |
| `/webhook/fact-find` | POST | Alias for `/ff` |
| `/automation` | POST | Receive Automation form |
| `/webhook/automation-form` | POST | Alias for `/automation` |
| `/status` | GET | Server status and statistics |
| `/matches` | GET | List all matched forms |
| `/health` | GET | Health check |
| `/generate/scope-of-advice` | POST | Generate scope of advice |
| `/generate/personal-information` | POST | Generate personal info |
| `/generate/combined-report` | POST | Generate full report |
| `/generate/life-insurance-fields` | POST | Generate life insurance data |
| `/generate/trauma-insurance-fields` | POST | Generate trauma insurance data |

**Startup Process**:
1. Initialize Flask app
2. Create data directories if they don't exist
3. Initialize FormMatcher (in-memory storage)
4. Initialize ZapierTrigger
5. Load all existing fact finds from `data/forms/fact_finds/`
6. Load all existing automation forms from `data/forms/automation_forms/`
7. Start Flask server on port 5001

**Form Reception Flow**:
```python
1. POST request received at /ff or /automation
2. Extract JSON data from request
3. Extract email identifier
4. Save form to disk with timestamp
5. Parse form into model (FactFind or AutomationForm)
6. Add to matcher
7. Check for matching form via auto_matcher
8. If match found → trigger Zapier
9. Return success response
```

---

### 2. Field Mapper (`src/field_mapper.py`)

**Purpose**: Translates Gravity Forms field IDs (numbers) to semantic field names

**Why This Exists**: Gravity Forms uses numeric field IDs (e.g., "144" = first name, "145" = last name). This mapper provides human-readable names and organizes fields into logical categories.

**Configuration Files**:
- `config/field_mappings.yaml` - Fact Find mappings
- `config/automation_form_mappings.yaml` - Automation Form mappings

**Example Mapping**:
```yaml
client:
  first_name: "144"        # Field 144 → first_name
  last_name: "145"         # Field 145 → last_name
  email: "219"             # Field 219 → email
  date_of_birth: "94"      # Field 94 → date_of_birth
  occupation: "6"          # Field 6 → occupation
```

**Usage**:
```python
from field_mapper import FieldMapper

mapper = FieldMapper('config/field_mappings.yaml')
data = mapper.extract_all(gravity_forms_data)

# data now contains:
# {
#   'client': {'first_name': 'John', 'last_name': 'Smith', ...},
#   'partner': {...},
#   'employment_main': {...},
#   ...
# }
```

**Categories**:
- `admin` - Administrative fields (case ID, date)
- `client` - Main client information
- `partner` - Partner information
- `employment_main` - Main client employment
- `employment_partner` - Partner employment
- `household` - Housing and living situation
- `assets` - Financial assets
- `liabilities` - Debts and liabilities
- `investment_properties` - Rental properties
- `kiwisaver` - KiwiSaver accounts
- `existing_insurance_main` - Main client's current insurance
- `existing_insurance_partner` - Partner's current insurance
- `medical_main` - Main client's health info
- `medical_partner` - Partner's health info
- `children` - Dependent children
- `recreational` - Hobbies and activities
- `needs_*` - Insurance needs analysis sections
- `scope_of_advice` - Scope and limitations

---

### 3. Form Matcher (`src/processors/form_matcher.py`)

**Purpose**: Intelligently matches Fact Find forms with Automation Forms based on email and other criteria

**How It Works**:

The matcher stores forms in-memory and uses multiple criteria to find matches:

1. **Email Matching** (50% weight)
   - Primary matching criterion
   - Emails must match exactly (case-insensitive)
   - If emails don't match, confidence = 0

2. **Couple Status** (20% weight)
   - Both forms should indicate same couple/single status
   - Checks if both have partner information

3. **Case ID Present** (10% weight)
   - Bonus points if fact find has a case ID

4. **Timing Proximity** (10% weight)
   - Forms submitted within 7 days: +10%
   - Forms submitted within 30 days: +5%
   - Forms submitted >30 days apart: warning

5. **Insurance Consistency** (10% weight)
   - Existing insurance amounts match
   - Provider names match
   - Allows 5% variance for rounding

**Confidence Threshold**: 0.7 (70%) for automatic processing

**Key Methods**:

```python
# Add forms to matcher
matcher.add_fact_find(fact_find_instance)
matcher.add_automation_form(automation_form_instance)

# Find match by email
match = matcher.match_by_email('client@example.com')

# Check if confident match
if match and match.is_confident_match(threshold=0.7):
    # Process the match
    fact_find = match.fact_find
    automation_form = match.automation_form
    confidence = match.confidence
    reasons = match.reasons  # Why it matched
```

**Match Result Object**:
```python
{
    'confidence': 0.85,           # 0.0 to 1.0
    'is_confident': True,         # >= threshold
    'reasons': [                  # List of match reasons
        'Email match: client@example.com',
        'Couple status match: couple',
        'Case ID present: 12345',
        'Forms submitted 2.3 days apart'
    ],
    'matched_at': '2025-11-02T10:30:00',
    'fact_find_case_id': '12345',
    'automation_form_email': 'client@example.com'
}
```

**Statistics**:
```python
stats = matcher.get_match_statistics()
# {
#   'total_fact_finds': 5,
#   'total_automation_forms': 3,
#   'total_matches': 2,
#   'confident_matches': 2,
#   'average_confidence': 0.82,
#   'unmatched_fact_finds': 3,
#   'unmatched_automation_forms': 1
# }
```

---

### 4. Auto Matcher (`src/processors/auto_matcher.py`)

**Purpose**: Automatically processes matched forms and triggers Zapier webhook

**When It Runs**: Automatically called when a form is received via webhook

**Process**:

```python
def check_and_trigger_match(email, matcher, zapier_trigger):
    1. Check if both forms exist for email
    2. Verify confidence threshold (>= 0.7)
    3. Load raw form data from disk (preserves field IDs)
    4. Generate all insurance sections:
       - Life Insurance
       - Trauma Insurance
       - Income Protection
       - Health Insurance
       - Accidental Injury
    5. Generate supporting sections:
       - Scope of Advice
       - Personal Information
       - Assets & Liabilities
    6. Create combined report
    7. Trigger Zapier webhook
    8. Return result
```

**Why Load Raw Data**:
The generators expect flat field structure (e.g., "144", "380") not nested models. Loading raw JSON preserves the original Gravity Forms field structure.

**Combined Report Structure**:
```python
{
    'status': 'success',
    'client_name': 'John Smith',
    'is_couple': False,
    'email': 'john@example.com',
    'match_confidence': 0.85,
    'scope_of_advice': {...},
    'personal_information': {...},
    'assets_liabilities': {...},
    'life_insurance': {...},
    'trauma_insurance': {...},
    'income_protection': {...},
    'health_insurance': {...},
    'accidental_injury': {...},
    'validation': {
        'total_sections_generated': 20,
        'all_sections_valid': True,
        'includes_all_insurance_types': True
    }
}
```

**Error Handling**:
- If match not found: Returns `{'matched': False, 'message': 'No confident match found yet'}`
- If processing fails: Returns error message, doesn't crash server
- Logs all steps for debugging

---

## Data Models

### FactFind Model (`src/models/fact_find.py`)

**Purpose**: Represents a complete Fact Find form submission

**Responsibilities**:
- Parse Gravity Forms data using FieldMapper
- Organize data into logical sections
- Convert currency strings to floats
- Handle couple vs. single applications
- Provide helper methods for data access

**Key Sections**:
```python
fact_find = FactFind()
fact_find.load_from_dict(gravity_forms_data)

# Access sections:
fact_find.client_info          # Main client details
fact_find.partner_info         # Partner details (None if single)
fact_find.case_info            # Case ID, dates
fact_find.employment_main      # Main client employment
fact_find.employment_partner   # Partner employment
fact_find.household_info       # Housing situation
fact_find.assets               # Assets
fact_find.liabilities          # Debts
fact_find.existing_insurance_main     # Current insurance
fact_find.existing_insurance_partner  # Partner's insurance
fact_find.medical_main         # Health information
fact_find.medical_partner      # Partner's health
fact_find.needs_life_main      # Life insurance needs
fact_find.needs_trauma_main    # Trauma insurance needs
fact_find.needs_income_main    # Income protection needs
# ... and more
```

**Helper Methods**:
```python
# Get full names
full_name = fact_find.get_client_full_name()
partner_name = fact_find.get_partner_full_name()

# Check if couple
is_couple = fact_find.is_couple()  # Boolean

# Convert to dict/JSON
dict_data = fact_find.to_dict()
json_str = fact_find.to_json()
```

**Currency Parsing**:
Automatically converts strings like "$100,000", "50000", "1,234.56" to float:
```python
# Input: "380" field = "$336,700"
# Output: fact_find.needs_life_main['total_needs'] = 336700.0
```

**Loading from File**:
```python
fact_find = FactFind()
fact_find.load_from_json('data/forms/fact_finds/client_20251030.json')
```

---

### AutomationForm Model (`src/models/automation_form.py`)

**Purpose**: Represents the Automation/Recommendation form (submitted after fact find)

**Key Differences from FactFind**:
- Submitted by adviser (not client)
- Contains recommendations and provider quotes
- Has scope limitations
- Shorter form, focused on advice

**Key Sections**:
```python
automation_form = AutomationForm()
automation_form.load_from_dict(gravity_forms_data)

# Access sections:
automation_form.client_details        # Email, couple status
automation_form.scope_of_advice       # What's in scope
automation_form.limitations           # Why certain products excluded
automation_form.main_existing_cover   # Main client's current insurance
automation_form.partner_existing_cover # Partner's current insurance
automation_form.recommendation        # Provider recommendations
automation_form.additional            # Extra notes
```

**Helper Methods**:
```python
# Check couple status
is_couple = automation_form.is_couple()

# Get selected insurance types
scope = automation_form.get_selected_scope()
# Returns: ['Life Insurance', 'Income Protection', 'Trauma Cover']

# Get limitation reasons
reasons = automation_form.get_limitation_reasons()
# Returns: ['Budget limitations', 'No dependants']

# Get recommended provider
provider = automation_form.get_recommended_provider()
# Returns: 'Partners Life'

# Find lowest quote
provider, amount = automation_form.get_lowest_quote()
# Returns: ('Fidelity Life', 245.50)
```

**Scope Processing**:
Converts checkbox values to booleans:
```python
# Input: "5.1" = "Life Insurance"
# Output: scope_of_advice['life_insurance'] = True

# Input: "6.4" = "You've advised you can self-insure the risk"
# Output: limitations['self_insure'] = True
```

---

## Processors

### Scope of Advice Generator (`src/processors/scope_of_advice_generator.py`)

**Purpose**: Generates structured scope of advice data from automation form

**What It Does**:
- Determines which insurance products are in/out of scope
- Extracts limitation reasons
- Formats submission date
- Creates structured JSON output

**Function**: `generate_scope_of_advice_json(data, client_name, is_couple)`

**Input**: Raw automation form data

**Output**:
```json
{
  "products_in_scope": [
    "Life Insurance",
    "Total & Permanent Disability"
  ],
  "products_out_of_scope": [
    "Trauma Cover",
    "Income Protection",
    "Health Insurance",
    "ACC Top-Up"
  ],
  "section_type": "scope_of_advice",
  "sections": {
    "form_submission_date": "Thursday, 30 October 2025",
    "limitations": "Client can self-insure income protection risk due to strong asset base and business ownership."
  },
  "status": "success"
}
```

**Field Mappings**:
```python
# Products (field 5.x in automation form):
'5.1' → 'Life Insurance'
'5.2' → 'Income Protection'
'5.3' → 'Trauma Cover'
'5.4' → 'Health Insurance'
'5.5' → 'Total & Permanent Disability'
'5.6' → 'ACC Top-Up'

# Limitations (field 6.x):
'6.1' → 'Medical cover through employer'
'6.2' → 'No debt and strong asset base'
'6.3' → 'Budget limitations'
'6.4' → 'Can self-insure the risk'
'6.5' → 'No dependants'
'6.6' → 'Uninsurable occupation'
'6.7' → 'Other reasons'
```

---

### Personal Information Extractor (`src/processors/personal_information_extractor.py`)

**Purpose**: Extracts client and partner personal/employment information

**Function**: `extract_personal_information(combined_data)`

**Input**: Raw fact find data

**Output**:
```json
{
  "household": {
    "people": [
      {
        "label": "Daniel",
        "age": 45,
        "employer": "iCreateBuilding",
        "occupation": "Director",
        "employment_status": "Fulltime",
        "salary_before_tax_nzd": 200000,
        "will_epa_status": ""
      },
      {
        "label": "Matthew",
        "age": 28,
        "employer": "iCreateBuilding",
        "occupation": "Director",
        "employment_status": "Self-Employed",
        "salary_before_tax_nzd": 140000,
        "will_epa_status": "Not In Place"
      }
    ]
  },
  "format": {
    "currency": "NZD",
    "locale": "en-NZ"
  },
  "constraints": {
    "max_chars": 360
  },
  "section_id": "personal_information",
  "status": "success"
}
```

**Age Calculation**:
```python
# Calculates age from date of birth (field 94/95)
from datetime import datetime
dob = '1980-02-13'
age = (datetime.now() - datetime.fromisoformat(dob)).days // 365
```

**Employment Status Logic**:
```python
if self_employed (field 482/483 = 'Yes'):
    return 'Self-Employed'
elif hours_field contains 'Full time':
    return 'Fulltime'
elif hours_field contains 'Part time':
    return 'Part-time'
else:
    return 'Fulltime'  # Default
```

---

### Assets & Liabilities Extractor (`src/processors/assets_liabilities_extractor.py`)

**Purpose**: Calculates total assets, liabilities, and net position

**Function**: `extract_assets_liabilities(combined_data)`

**Output**:
```json
{
  "total_assets": 752000,
  "total_liabilities": 62000,
  "net_position": 690000,
  "assets_breakdown": {
    "business_assets": 271000,
    "business_valuation": 481000,
    "investment_properties": 0,
    "kiwisaver_main": 0,
    "kiwisaver_partner": 0,
    "other_assets": 0
  },
  "liabilities_breakdown": {
    "mortgage": 0,
    "business_debt": 62000,
    "investment_property_debt": 0,
    "other_debt": 0
  },
  "section_id": "assets_liabilities",
  "status": "success"
}
```

**Calculation**:
```python
# Assets from fields:
# 26 = Business assets/equipment
# 36 = Business valuation
# 16 = Home value (if owned)
# Investment property values
# KiwiSaver balances

# Liabilities from fields:
# 15/72 = Mortgage/business debt
# Investment property mortgages
# Other debts

net_position = total_assets - total_liabilities
```

---

### Life Insurance Extractor (`src/processors/life_insurance_extractor.py`)

**Purpose**: Extracts life and trauma insurance needs and coverage

**Functions**:
- `extract_life_insurance(combined_data, is_couple)` - Life insurance
- `extract_trauma_insurance(combined_data, is_couple)` - Trauma insurance

**Life Insurance Output**:
```json
{
  "coverage": {
    "person": {
      "sum_insured_nzd": 336700,
      "sum_insured_formatted": "$336,700",
      "existing_cover_nzd": 336700,
      "existing_cover_formatted": "$336,700",
      "shortfall_nzd": 0,
      "shortfall_formatted": "$0",
      "is_in_scope": true
    }
  },
  "needs_analysis": {
    "applies_to": "individual",
    "context": "Individual protection needs",
    "narrative": "70% of business shares owned by Dan - $336,700 value. Needs to be paid to Matt so he can buy the shares off Dan's estate. TPD cover matching their Life Cover accelerated off of the Life Cover."
  },
  "scenario": "single",
  "section_id": "life_insurance",
  "section_type": "life_insurance_single",
  "format": {
    "currency": "NZD",
    "locale": "en-NZ"
  },
  "status": "success"
}
```

**Field Sources**:
```python
# Needs analysis from field 504 (or 380 for single)
# Existing cover from existing_insurance_main
# Sum insured = needs analysis total
# Shortfall = sum_insured - existing_cover
```

**Couple Handling**:
If `is_couple=True`, output includes:
```json
{
  "coverage": {
    "person": {...},      # Main client
    "partner": {...}      # Partner
  }
}
```

---

## Generators

Generators calculate detailed insurance needs and recommendations. They're more comprehensive than extractors.

### Life Insurance Generator (`src/generators/life_insurance_fields.py`)

**Function**: `extract_life_insurance_fields(data)`

**Purpose**: Calculate detailed life insurance needs with all components

**Output Structure**:
```json
{
  "main_needs_life": true,
  "main_total_life_cover": 336700,
  "main_final_expenses": 15000,
  "main_mortgage": 0,
  "main_short_term_debt": 0,
  "main_income_replacement": 0,
  "main_education_costs": 0,
  "main_spouse_superannuation": 0,
  "main_business_overhead": 0,
  "main_shareholding_protection": 336700,
  "main_other_needs": 0,
  "main_existing_life_cover": 336700,
  "main_net_life_cover_needed": 0,
  "main_recommended_life_cover": 336700,
  "main_tpd_addon": true,
  "main_buyback_option": false,
  "main_future_insurability": true,

  "partner_needs_life": false,
  "partner_total_life_cover": 0,
  // ... partner fields

  "status": "success"
}
```

**Calculation Logic**:
```python
total_needs = (
    final_expenses +
    mortgage +
    short_term_debt +
    income_replacement +
    education_costs +
    spouse_super +
    business_overhead +
    shareholding_protection +
    other_needs
)

net_needed = total_needs - existing_cover

recommended_cover = max(total_needs, existing_cover)
```

**Field Mappings**:
- Field 389/400: Shareholding protection
- Field 380/391: Total needs
- Field 386/397: Existing cover
- Field 504/506: Needs analysis narrative

---

### Trauma Insurance Generator (`src/generators/trauma_insurance_fields.py`)

**Function**: `extract_trauma_insurance_fields(data)`

**Output**:
```json
{
  "main_needs_trauma": false,
  "main_total_trauma_cover": 0,
  "main_existing_trauma_cover": 0,
  "main_net_trauma_needed": 0,
  "main_recommended_trauma_cover": 0,
  "main_trauma_buyback": false,

  "partner_needs_trauma": false,
  "partner_total_trauma_cover": 0,
  // ... partner fields

  "trauma_notes": "Not required - Covered through personal insurances.",
  "status": "success"
}
```

---

### Income Protection Generator (`src/generators/income_protection_fields.py`)

**Function**: `extract_income_protection_fields(data)`

**Calculation**:
```python
# Monthly benefit = 75% of monthly income (capped at $30,000/month)
monthly_income = annual_salary / 12
monthly_benefit = min(monthly_income * 0.75, 30000)

# Factors:
# - Wait period (13, 26, 52, 104 weeks)
# - Claim period (2, 5 years, to age 65)
# - Agreed vs Indemnity value
# - ACC offsets
# - Redundancy cover
```

**Output**:
```json
{
  "main_needs_income_protection": true,
  "main_monthly_income": 16667,
  "main_monthly_benefit": 12500,
  "main_annual_benefit": 150000,
  "main_wait_period_weeks": 13,
  "main_claim_period_years": 5,
  "main_income_type": "Agreed Value",
  "main_acc_offsets": true,
  "main_redundancy": false,
  "main_existing_ip_cover": 0,
  "main_net_ip_needed": 12500,

  "partner_needs_income_protection": false,
  // ... partner fields

  "status": "success"
}
```

---

### Health Insurance Generator (`src/generators/health_insurance_fields.py`)

**Function**: `extract_health_insurance_fields(data)`

**Output**:
```json
{
  "main_needs_health_insurance": false,
  "main_health_plan_type": "Specialist",
  "main_health_excess": 500,
  "main_existing_health_cover": false,
  "main_employer_health_cover": false,

  "partner_needs_health_insurance": false,
  // ... partner fields

  "health_notes": "",
  "status": "success"
}
```

---

### Accidental Injury Generator (`src/generators/accidental_injury_fields.py`)

**Function**: `extract_accidental_injury_fields(data)`

**Purpose**: ACC top-up / accident cover

**Output**:
```json
{
  "main_needs_accident_cover": false,
  "main_acc_topup_recommended": false,
  "main_weekly_compensation": 0,
  "main_lump_sum_benefit": 0,

  "partner_needs_accident_cover": false,
  // ... partner fields

  "accident_notes": "",
  "status": "success"
}
```

---

## Zapier Integration

### Zapier Trigger (`src/processors/zapier_trigger.py`)

**Purpose**: Sends standardized payloads to Zapier webhooks

**Configuration**: `config/zapier_config.json`

```json
{
  "zapier_webhook_url": "https://hooks.zapier.com/hooks/catch/12679562/urq5tjh/",
  "enabled": true,
  "trigger_on_match": true,
  "include_all_fields": true,
  "retry_attempts": 3,
  "retry_delay_seconds": 5,
  "timeout_seconds": 30,
  "headers": {
    "Content-Type": "application/json",
    "X-Source": "Insurance-SOA-System"
  }
}
```

**Process Flow**:
```python
1. Check if enabled
2. Check if webhook URL configured
3. Build standardized payload (via ZapierPayloadBuilder)
4. Validate payload structure
5. Send HTTP POST to Zapier
6. Retry up to 3 times on failure
7. Log response
8. Return result
```

**Retry Logic**:
```python
for attempt in range(1, retry_attempts + 1):
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        if response.status_code in [200, 201, 202]:
            return success
        else:
            if attempt < retry_attempts:
                time.sleep(retry_delay_seconds)
                continue
    except Timeout:
        # Retry
    except RequestException:
        # Retry
```

**Response**:
```python
{
    'triggered': True,
    'timestamp': '2025-11-02T10:30:00',
    'status': 'success',
    'message': 'Successfully triggered Zapier webhook (HTTP 200)',
    'zapier_response': {
        'status_code': 200,
        'response_text': '{"status":"success","id":"..."}'
    }
}
```

---

### Zapier Payload Builder (`src/processors/zapier_payload_builder.py`)

**Purpose**: Creates standardized, consistent payloads for Zapier

**Why This Exists**: Ensures every webhook has the EXACT same structure, preventing field mapping errors in Zapier

**Key Features**:
- Guarantees all required fields are present
- Provides default values for missing sections
- Validates payload structure
- Ensures consistent data types

**Usage**:
```python
from processors.zapier_payload_builder import ZapierPayloadBuilder

builder = ZapierPayloadBuilder()
payload = builder.build_payload(combined_report)

# Validate
is_valid, errors = builder.validate_payload(payload)
if not is_valid:
    print("Errors:", errors)

# Get summary
summary = builder.get_payload_summary(payload)
print(summary)
```

**Guaranteed Structure**:

Every payload will ALWAYS have these fields:

```python
{
    # Core (always present):
    "client_email": str,
    "client_name": str,
    "partner_name": str | None,
    "case_id": str,
    "is_couple": bool,
    "match_confidence": float,

    # Sections (always present as objects):
    "scope_of_advice": dict,
    "personal_information": dict,
    "assets_liabilities": dict,
    "life_insurance": dict,
    "trauma_insurance": dict,
    "income_protection": dict,
    "health_insurance": dict,
    "accidental_injury": dict,

    # Metadata:
    "timestamp": str,  # ISO 8601
    "source": "Insurance-SOA-System",
    "payload_version": "1.0"
}
```

**Default Section Structure**:

If a section wasn't generated, it gets this default:
```python
{
    "status": "not_generated",
    "needs_analysis": {},
    "coverage": {}
}
```

If a section was generated successfully:
```python
{
    "status": "success",
    "needs_analysis": {...},  # Populated
    "coverage": {...}         # Populated
}
```

**Validation**:

The builder validates:
- All required fields present
- Correct data types (boolean, number, string)
- All sections are objects/dicts
- No missing or null required fields

**Benefits**:

✅ **Before**: Fields appeared/disappeared based on data, Zaps broke
✅ **After**: All fields always present, predictable structure

✅ **Before**: Had to constantly update Zapier field mappings
✅ **After**: Set up once, works forever

✅ **Before**: "Field not found" errors in Zapier
✅ **After**: No field mapping errors

---

## Data Flow

### Complete Flow for Form Submission

#### Step 1: Client Submits Fact Find

```
WordPress (Gravity Forms)
    │
    │ Client fills out Fact Find
    │ Clicks Submit
    │
    ▼
Gravity Forms Webhook
    │
    │ POST http://webhook-server:5001/ff
    │ Content-Type: application/json
    │ Body: {...all form data...}
    │
    ▼
Webhook Server Receives
    │
    ├─► Extract email (field 219)
    ├─► Generate filename: dan_at_icreatebuilding_nz_20251030_132708.json
    ├─► Save to: data/forms/fact_finds/
    │
    ├─► Create FactFind model
    ├─► Parse with FieldMapper
    ├─► Add to FormMatcher
    │
    ├─► Check for automation form match
    │   └─► Not found (automation form not submitted yet)
    │
    └─► Return: {"status": "success", "email": "dan@icreatebuilding.nz"}
```

#### Step 2: Adviser Submits Automation Form

```
WordPress (Gravity Forms)
    │
    │ Adviser fills out Automation Form
    │ Selects scope, provider, recommendations
    │ Clicks Submit
    │
    ▼
Gravity Forms Webhook
    │
    │ POST http://webhook-server:5001/automation
    │ Content-Type: application/json
    │ Body: {...all form data...}
    │
    ▼
Webhook Server Receives
    │
    ├─► Extract email (field 3)
    ├─► Generate filename: dan_at_icreatebuilding_nz_20251030_141339.json
    ├─► Save to: data/forms/automation_forms/
    │
    ├─► Create AutomationForm model
    ├─► Parse with FieldMapper
    ├─► Add to FormMatcher
    │
    ├─► Check for fact find match
    │   ├─► MATCH FOUND! (dan@icreatebuilding.nz)
    │   ├─► Confidence: 0.80
    │   └─► Trigger auto_matcher
    │
    └─► Auto Matcher Process Starts...
```

#### Step 3: Auto Matcher Processing

```
Auto Matcher (check_and_trigger_match)
    │
    ├─► Load raw fact find JSON
    │   └─► data/forms/fact_finds/dan_at_icreatebuilding_nz_20251030_132708.json
    │
    ├─► Load raw automation form JSON
    │   └─► data/forms/automation_forms/dan_at_icreatebuilding_nz_20251030_141339.json
    │
    ├─► Merge both JSONs into combined_data
    │
    ├─► Generate All Sections:
    │   │
    │   ├─► Scope of Advice Generator
    │   │   └─► Products in/out of scope, limitations
    │   │
    │   ├─► Personal Information Extractor
    │   │   └─► Client + partner details, employment
    │   │
    │   ├─► Assets & Liabilities Extractor
    │   │   └─► Total assets, liabilities, net position
    │   │
    │   ├─► Life Insurance Generator
    │   │   └─► Needs, coverage, shortfall
    │   │
    │   ├─► Trauma Insurance Generator
    │   │   └─► Needs, coverage, shortfall
    │   │
    │   ├─► Income Protection Generator
    │   │   └─► Monthly benefit, wait periods, etc.
    │   │
    │   ├─► Health Insurance Generator
    │   │   └─► Plan type, excess, employer cover
    │   │
    │   └─► Accidental Injury Generator
    │       └─► ACC top-up recommendations
    │
    ├─► Create Combined Report
    │   └─► {
    │         "client_name": "dan@icreatebuilding.nz",
    │         "is_couple": false,
    │         "email": "dan@icreatebuilding.nz",
    │         "match_confidence": 0.80,
    │         "scope_of_advice": {...},
    │         "personal_information": {...},
    │         ... all sections ...
    │       }
    │
    └─► Trigger Zapier
```

#### Step 4: Zapier Trigger

```
Zapier Trigger Process
    │
    ├─► Check if enabled (config/zapier_config.json)
    │   └─► enabled: true ✓
    │
    ├─► Check webhook URL configured
    │   └─► URL: https://hooks.zapier.com/hooks/catch/12679562/urq5tjh/ ✓
    │
    ├─► Build Standardized Payload
    │   │
    │   └─► ZapierPayloadBuilder.build_payload(combined_report)
    │       │
    │       ├─► Extract core fields
    │       ├─► Ensure all sections present
    │       ├─► Apply defaults for missing data
    │       └─► Add metadata (timestamp, source, version)
    │
    ├─► Validate Payload
    │   └─► ZapierPayloadBuilder.validate_payload(payload)
    │       ├─► Check required fields ✓
    │       ├─► Check data types ✓
    │       └─► Check section structure ✓
    │
    ├─► Print Summary
    │   └─► Client: dan@icreatebuilding.nz
    │       Case ID: 27236
    │       Sections: all success
    │
    ├─► Send HTTP POST
    │   │
    │   └─► POST https://hooks.zapier.com/hooks/catch/12679562/urq5tjh/
    │       Headers: Content-Type: application/json
    │       Body: {standardized payload}
    │       Timeout: 30 seconds
    │
    ├─► Receive Response
    │   └─► Status: 200 OK
    │       Body: {"status":"success","id":"019a4281..."}
    │
    └─► Return Success
        └─► {
              "triggered": true,
              "status": "success",
              "message": "Successfully triggered Zapier webhook"
            }
```

#### Step 5: Zapier Catches Webhook

```
Zapier Platform
    │
    ├─► Catch Hook trigger receives POST
    │
    ├─► Parse JSON payload
    │   └─► All fields present ✓
    │
    ├─► Make data available to Zap
    │   └─► Fields accessible in Zapier editor
    │
    └─► Execute Zap actions
        │
        ├─► Action 1: Update Google Sheet
        ├─► Action 2: Send Email
        ├─► Action 3: Create Asana Task
        └─► ...etc
```

---

## Configuration

### Zapier Configuration (`config/zapier_config.json`)

```json
{
  "zapier_webhook_url": "https://hooks.zapier.com/hooks/catch/YOUR_ID/YOUR_CODE/",
  "enabled": true,
  "trigger_on_match": true,
  "include_all_fields": true,
  "retry_attempts": 3,
  "retry_delay_seconds": 5,
  "timeout_seconds": 30,
  "headers": {
    "Content-Type": "application/json",
    "X-Source": "Insurance-SOA-System"
  }
}
```

**Fields**:
- `zapier_webhook_url`: Your Zapier catch hook URL
- `enabled`: Master on/off switch for Zapier triggers
- `trigger_on_match`: Auto-trigger when forms match
- `retry_attempts`: How many times to retry on failure
- `retry_delay_seconds`: Seconds to wait between retries
- `timeout_seconds`: HTTP request timeout

### Field Mappings (`config/field_mappings.yaml`)

Maps Gravity Forms field IDs to semantic names.

**Structure**:
```yaml
# Category name:
category_name:
  semantic_field_name: "gravity_forms_field_id"
  another_field: "another_id"

# Example:
client:
  first_name: "144"
  last_name: "145"
  email: "219"
  date_of_birth: "94"
  occupation: "6"
```

**Full Categories**:
- admin
- client
- partner
- employment_main
- employment_partner
- household
- assets
- liabilities
- investment_properties
- kiwisaver
- existing_insurance_main
- existing_insurance_partner
- medical_main
- medical_partner
- children
- recreational
- needs_life_main
- needs_life_partner
- needs_trauma_main
- needs_trauma_partner
- needs_income_main
- needs_income_partner
- needs_accident
- needs_medical_main
- needs_medical_partner
- scope_of_advice

---

## Usage Guide

### Starting the Webhook Server

```bash
cd /Users/mitchworthington/Downloads/Insurance-SOA-main
python3 src/webhook_server.py
```

**Expected Output**:
```
======================================================================
INSURANCE SOA WEBHOOK SERVER
======================================================================

Loading existing forms...
  ✓ Loaded fact find: dan_at_icreatebuilding_nz_20251030_132708.json
  ✓ Loaded automation form: dan_at_icreatebuilding_nz_20251030_141339.json
Loaded: 5 fact finds, 3 automation forms

Webhook Endpoints:
--------------------------------------------------
  Fact Find Form:     POST http://localhost:5001/ff
  Automation Form:    POST http://localhost:5001/automation
  Status:             GET  http://localhost:5001/status
  ...

Server starting on http://localhost:5001
```

### Checking Server Status

```bash
curl http://localhost:5001/status | python3 -m json.tool
```

**Response**:
```json
{
  "status": "running",
  "statistics": {
    "total_fact_finds": 5,
    "total_automation_forms": 3,
    "total_matches": 2,
    "confident_matches": 2,
    "average_confidence": 0.82,
    "unmatched_fact_finds": 3,
    "unmatched_automation_forms": 1
  }
}
```

### Viewing Matches

```bash
curl http://localhost:5001/matches | python3 -m json.tool
```

### Manual Report Generation

Generate a combined report manually:

```bash
curl -X POST http://localhost:5001/generate/combined-report \
  -H "Content-Type: application/json" \
  -d @data/forms/fact_finds/dan_at_icreatebuilding_nz_20251030_132708.json \
  | python3 -m json.tool
```

### Testing Zapier Integration

```python
import sys
sys.path.insert(0, 'src')

from processors.form_matcher import FormMatcher
from processors.zapier_trigger import ZapierTrigger
from processors.auto_matcher import check_and_trigger_match
from models.fact_find import FactFind
from models.automation_form import AutomationForm
import json

# Initialize
matcher = FormMatcher()
zapier_trigger = ZapierTrigger()

# Load a fact find
with open('data/forms/fact_finds/dan_at_icreatebuilding_nz_20251030_132708.json') as f:
    ff_data = json.load(f)
ff = FactFind()
ff.load_from_dict(ff_data)
matcher.add_fact_find(ff)

# Load automation form
with open('data/forms/automation_forms/dan_at_icreatebuilding_nz_20251030_141339.json') as f:
    af_data = json.load(f)
af = AutomationForm()
af.load_from_dict(af_data)
matcher.add_automation_form(af)

# Trigger
result = check_and_trigger_match('dan@icreatebuilding.nz', matcher, zapier_trigger)
print(f"Matched: {result['matched']}")
print(f"Zapier Triggered: {result['zapier_triggered']}")
print(f"Status: {result.get('zapier_status')}")
```

---

## Troubleshooting

### Problem: Forms Not Matching

**Symptoms**:
- Fact find received but no Zapier trigger
- Automation form received but no trigger
- Status shows unmatched forms

**Diagnosis**:
```bash
curl http://localhost:5001/matches
```

Check confidence scores and match reasons.

**Solutions**:

1. **Email Mismatch**
   - Fact find email: `dan@icreatebuilding.nz`
   - Automation email: `dan@icreatebuilding.co.nz`
   - Solution: Emails must match exactly

2. **Low Confidence**
   - Confidence: 0.65 (threshold is 0.70)
   - Solution: Check couple status matches, dates within 30 days

3. **Forms Not Loaded**
   - Restart server to reload forms from disk
   ```bash
   # Stop server (Ctrl+C)
   python3 src/webhook_server.py
   ```

### Problem: Zapier Not Receiving Data

**Symptoms**:
- Server logs show "Zapier webhook triggered"
- But no data appears in Zapier

**Diagnosis**:

1. **Check Zapier Config**
   ```bash
   cat config/zapier_config.json
   ```
   - Verify `enabled: true`
   - Verify webhook URL is correct

2. **Check Zapier Task History**
   - Go to Zapier.com
   - Click "Task History"
   - Look for recent webhook catches

3. **Check Zap Status**
   - Ensure Zap is turned ON (not draft)
   - Click "Test trigger" to catch recent webhooks

**Solutions**:

1. **Zap Not Turned On**
   - Go to Zapier editor
   - Click "Turn on Zap"

2. **Wrong Webhook URL**
   - Get fresh webhook URL from Zapier
   - Update `config/zapier_config.json`
   - Restart server

3. **Zap Filter Blocking**
   - Check if you have filters in your Zap
   - Temporarily disable filters to test

### Problem: Field Mapping Errors in Zapier

**Symptoms**:
- "Field not found" errors in Zap
- Fields appearing/disappearing
- Inconsistent data structure

**Solution**:

The new standardized payload builder fixes this. Ensure you're using the latest version:

1. **Verify payload builder is active**
   - Check server logs for "Payload validation passed"
   - Should see: "✅ Payload validation passed"

2. **Re-test Zapier trigger**
   - In Zapier editor, click "Test trigger"
   - Select the most recent webhook
   - All fields should now be present

3. **Update field mappings**
   - Fields are now guaranteed to exist
   - Safe to map: `life_insurance__status`
   - Check status before using data

### Problem: Server Won't Start

**Symptoms**:
```
Address already in use
Port 5001 is in use by another program
```

**Solution**:
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Start server
python3 src/webhook_server.py
```

### Problem: Import Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'processors'
```

**Solution**:
```bash
# Ensure you're in the project root
cd /Users/mitchworthington/Downloads/Insurance-SOA-main

# Run from root
python3 src/webhook_server.py

# Or add to path
import sys
sys.path.insert(0, 'src')
```

### Problem: Missing Data in Sections

**Symptoms**:
- Life insurance section shows `status: "not_generated"`
- Expected data not present

**Diagnosis**:

Check the raw form data has the required fields:

```python
import json

with open('data/forms/fact_finds/client_file.json') as f:
    data = json.load(f)

# Check for life insurance fields
print('Field 380:', data.get('380'))  # Total needs
print('Field 386:', data.get('386'))  # Existing cover
```

**Solution**:

1. **Field Not Filled In Form**
   - Client didn't complete that section
   - Section will show `status: "not_generated"`
   - This is expected behavior

2. **Wrong Field ID**
   - Check `config/field_mappings.yaml`
   - Verify field IDs match Gravity Forms

3. **Data Type Mismatch**
   - Field expects number, got string
   - Check generators for parsing logic

---

## API Reference

### POST /ff

Receive fact find form submission.

**Request**:
```json
{
  "219": "client@example.com",
  "516": "12345",
  "144": "John",
  "145": "Smith",
  ...
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Fact Find received",
  "email": "client@example.com",
  "matched": true,
  "zapier_triggered": true,
  "zapier_status": "success"
}
```

### POST /automation

Receive automation form submission.

**Request**:
```json
{
  "3": "client@example.com",
  "39": "My partner and I",
  "5.1": "Life Insurance",
  ...
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Automation Form received",
  "email": "client@example.com",
  "matched": true,
  "zapier_triggered": true,
  "zapier_status": "success"
}
```

### GET /status

Get server status and statistics.

**Response**:
```json
{
  "status": "running",
  "statistics": {
    "total_fact_finds": 5,
    "total_automation_forms": 3,
    "total_matches": 2,
    "confident_matches": 2,
    "average_confidence": 0.82,
    "unmatched_fact_finds": 3,
    "unmatched_automation_forms": 1
  },
  "unmatched_fact_finds": 3,
  "unmatched_automation_forms": 1
}
```

### GET /matches

Get all matched forms.

**Response**:
```json
{
  "total_matches": 2,
  "confident_matches": 2,
  "matches": [
    {
      "email": "client@example.com",
      "case_id": "12345",
      "client_name": "John Smith",
      "confidence": 0.85,
      "is_confident": true,
      "reasons": [
        "Email match: client@example.com",
        "Couple status match: single",
        "Forms submitted 1.2 days apart"
      ],
      "matched_at": "2025-11-02T10:30:00"
    }
  ]
}
```

### POST /generate/scope-of-advice

Generate scope of advice from automation form data.

**Request**: Raw automation form JSON

**Response**:
```json
{
  "status": "success",
  "section_type": "scope_of_advice",
  "products_in_scope": ["Life Insurance", "TPD"],
  "products_out_of_scope": ["Trauma", "Income Protection"],
  "sections": {
    "form_submission_date": "Thursday, 30 October 2025",
    "limitations": "..."
  }
}
```

### POST /generate/personal-information

Extract personal information.

**Request**: Raw fact find JSON

**Response**:
```json
{
  "status": "success",
  "section_id": "personal_information",
  "household": {
    "people": [...]
  }
}
```

### POST /generate/combined-report

Generate complete combined report.

**Request**: Raw fact find JSON

**Response**:
```json
{
  "status": "success",
  "client_name": "...",
  "is_couple": false,
  "scope_of_advice": {...},
  "personal_information": {...},
  "life_insurance": {...},
  ...all sections...
}
```

---

## Appendix: Field ID Reference

### Fact Find Form (ID: 100)

#### Administrative
- `516`: Case ID
- `date_created`: Submission timestamp

#### Main Client
- `144`: First name
- `145`: Last name
- `219`: Email
- `94`: Date of birth
- `6`: Occupation
- `10`: Annual income

#### Partner
- `146`: Partner first name
- `147`: Partner last name
- `523`: Partner email
- `95`: Partner date of birth
- `40`: Partner occupation
- `42`: Partner annual income

#### Life Insurance Needs
- `380`: Total life insurance needs (main)
- `386`: Existing life cover (main)
- `389`: Shareholding protection (main)
- `391`: Total life insurance needs (partner)
- `397`: Existing life cover (partner)
- `400`: Shareholding protection (partner)
- `504`: Life insurance notes (main)
- `506`: Life insurance notes (partner)

### Automation Form (ID: 124)

#### Client Details
- `3`: Email
- `39`: Couple status

#### Scope of Advice
- `5.1`: Life Insurance
- `5.2`: Income Protection
- `5.3`: Trauma Cover
- `5.4`: Health Insurance
- `5.5`: Total & Permanent Disability
- `5.6`: ACC Top-Up

#### Limitations
- `6.1`: Medical cover through employer
- `6.2`: No debt and strong asset base
- `6.3`: Budget limitations
- `6.4`: Can self-insure the risk
- `6.5`: No dependants
- `6.6`: Uninsurable occupation
- `6.7`: Other reasons

#### Provider Recommendation
- `41`: Selected provider

---

## Support

For issues or questions:

1. Check server logs for error messages
2. Verify configuration files are correct
3. Test endpoints manually with curl
4. Check Zapier task history
5. Review this documentation

**Common Issues Solved**:
- Form matching: Check email matches exactly
- Zapier not receiving: Verify Zap is ON
- Field errors: Use standardized payload builder
- Server won't start: Kill process on port 5001

---

**End of Documentation**

This documentation covers the complete Insurance SOA System. For specific implementation details, refer to the individual source files listed in each section.
