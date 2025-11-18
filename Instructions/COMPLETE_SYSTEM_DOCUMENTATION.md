# Insurance SOA System - Complete Documentation

**Version:** 2.0
**Last Updated:** November 18, 2025
**System Purpose:** Automated insurance Scope of Advice generation with Zapier integration and insurance quote extraction

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
11. [Insurance Quotes Extraction](#insurance-quotes-extraction)
12. [Zapier Integration](#zapier-integration)
13. [Usage Guide](#usage-guide)
14. [Troubleshooting](#troubleshooting)
15. [Recent Updates](#recent-updates)

---

## System Overview

### What This System Does

The Insurance SOA (Scope of Advice) System is an automated pipeline that:

1. **Receives** insurance form submissions via webhooks from Gravity Forms
2. **Matches** fact find forms with automation forms by client email
3. **Processes** the combined data to extract structured insurance information
4. **Extracts** insurance quote URLs from uploaded provider documents
5. **Generates** comprehensive reports for all insurance types
6. **Triggers** Zapier webhooks with standardized, consistent payloads
7. **Stores** all form data and reports for record-keeping

### Key Features

- **Automatic Form Matching**: Intelligently pairs fact finds with automation forms
- **Multi-Insurance Support**: Life, Trauma, Income Protection, Health, Accidental Injury
- **Insurance Quote Extraction**: Extracts and processes insurance provider quote URLs
- **Couple & Single Handling**: Processes both individual and couple applications
- **Zapier Integration**: Sends consistent, structured data to Zapier workflows
- **Smart Data Merging**: Prevents empty fields from overwriting valid data
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
         │ When Match Found (≥0.6 confidence)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│          Auto Matcher & Processor                       │
│  • Loads raw form data                                  │
│  • Merges data (non-empty values only)                  │
│  • Runs all generators                                  │
│  • Extracts insurance quotes                            │
│  • Creates combined report                              │
└────────┬────────────────────────────────────────────────┘
         │
         │ Combined Report
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│          Zapier Payload Builder                         │
│  • Standardizes structure                               │
│  • Includes insurance quote fields                      │
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
│   │   ├── scope_of_advice_generator.py   # Generates scope of advice
│   │   ├── personal_information_extractor.py  # Extracts personal info
│   │   ├── assets_liabilities_extractor.py    # Extracts financial data (UPDATED)
│   │   ├── insurance_quotes_extractor.py  # NEW: Extracts insurance quote URLs
│   │   ├── zapier_trigger.py              # Sends data to Zapier
│   │   └── zapier_payload_builder.py      # Builds standardized payloads (UPDATED)
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
│   │   └── automation_forms/             # Saved automation form submissions
│   └── reports/                          # Generated reports
│
├── manual_trigger.py                      # Manual trigger script for testing
├── test_insurance_quotes.py              # NEW: Test script for insurance quotes
└── Instructions/                         # Documentation
    └── COMPLETE_SYSTEM_DOCUMENTATION.md  # This file
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
- Triggers Zapier when matched (confidence ≥ 0.6)

**Startup Process**:
1. Initialize Flask app
2. Create data directories if they don't exist
3. Initialize FormMatcher (in-memory storage)
4. Initialize ZapierTrigger
5. Load all existing fact finds from `data/forms/fact_finds/`
6. Load all existing automation forms from `data/forms/automation_forms/`
7. Start Flask server on port 5001

**Important**: The server only loads forms at startup. If a new automation form is submitted after the server starts, you need to restart the server to load it.

---

## Insurance Quotes Extraction

### Insurance Quotes Extractor (`src/processors/insurance_quotes_extractor.py`)

**Purpose**: Extracts insurance quote URLs from automation form upload fields

**Function**: `extract_insurance_quotes(combined_data)`

**Field Mappings**:
```python
# Quote upload fields in automation form:
'42': Partners Life quote URL
'43': Fidelity Life quote URL
'44': AIA quote URL
'45': Asteron quote URL
'46': Chubb quote URL
'47': nib quote URL
```

**How It Works**:

1. **JSON Array Format**: Fields contain JSON arrays with file info:
```json
[{"name":"filename.pdf","url":"https://..."}]
```

2. **Extraction Process**:
```python
def extract_quote_url(field_value):
    # Parse JSON array
    # Extract first item's URL
    # Return URL string or empty if not present
```

3. **Output Structure**:
```json
{
  "section_id": "insurance_quotes",
  "section_type": "quote_uploads",
  "quote_partners_life": "",
  "quote_fidelity_life": "https://...",
  "quote_aia": "",
  "quote_asteron": "",
  "quote_chubb": "",
  "quote_nib": "",
  "quotes_count": 1,
  "has_quotes": true,
  "status": "success"
}
```

**Integration with Zapier**:
- All quote URLs are included in the Zapier payload
- Each provider has its own field for easy mapping
- `quotes_count` and `has_quotes` provide summary info

---

## Data Merging Logic

### Smart Form Merging (`src/processors/auto_matcher.py`)

**Problem Solved**: Empty fields in automation forms were overwriting valid fact find data

**Solution**: Only update with non-empty values

```python
# Load fact find data first (base data)
combined_data = {}
combined_data.update(fact_find_data)

# Only update with non-empty automation form values
for key, value in automation_data.items():
    # Only update if value is not empty string, not None, and not False
    # But allow 0 as a valid value
    if value != "" and value is not None and value is not False:
        combined_data[key] = value
```

**Benefits**:
- Preserves all fact find data
- Automation form only adds/updates with actual values
- Prevents data loss from empty fields
- Maintains data integrity

---

## Assets & Liabilities Updates

### Fixed Field Mappings (`src/processors/assets_liabilities_extractor.py`)

**Recent Fixes**:

1. **Correct Field Mappings**:
```python
asset_pairs = [
    ('22', '26'),   # Asset 1: name/value (FIXED)
    ('19', '36'),   # Asset 2: name/value
    ('35', '34'),   # Asset 3: name/value
    ('45', '46'),   # Asset 4: name/value
    ('47', '287'),  # Asset 5: value field fixed
    # ... continues for all 15 assets
]
```

2. **Special Handling for Field 33**:
```python
# Field 33 not in original spec but contains data
# Paired with orphan value in field 26 when field 22 is empty
if field_33_name and field_26_value > 0 and not field_22_name:
    # Field 33 is using the orphan value from field 26
    assets.append({
        "name": field_33_name,
        "value": field_26_value,
        "formatted": format_currency(field_26_value)
    })
```

3. **Changed Labels**:
- "Primary Residence" → "Owner Occupied"

4. **Output Format**:
```json
{
  "assets_json": "[{\"name\":\"Owner Occupied\",\"value\":1127000,...}]",
  "liabilities_json": "[{\"name\":\"Home Mortgage\",\"value\":880000,...}]",
  "assets_text": "Assets\n--------------------------------------------------\nOwner Occupied...",
  "liabilities_text": "Liabilities\n--------------------------------------------------\nHome Mortgage...",
  "summary_text": "Financial Summary\n--------------------------------------------------\nTotal Assets...",
  "total_assets": 1127000,
  "total_liabilities": 880000,
  "net_worth": 247000
}
```

---

## Zapier Integration

### Zapier Payload Builder Updates (`src/processors/zapier_payload_builder.py`)

**Recent Addition**: Insurance quote fields

```python
# Added to build_payload method:
"quote_partners_life": combined_report.get('insurance_quotes', {}).get('quote_partners_life', ''),
"quote_fidelity_life": combined_report.get('insurance_quotes', {}).get('quote_fidelity_life', ''),
"quote_aia": combined_report.get('insurance_quotes', {}).get('quote_aia', ''),
"quote_asteron": combined_report.get('insurance_quotes', {}).get('quote_asteron', ''),
"quote_chubb": combined_report.get('insurance_quotes', {}).get('quote_chubb', ''),
"quote_nib": combined_report.get('insurance_quotes', {}).get('quote_nib', ''),
"quotes_count": combined_report.get('insurance_quotes', {}).get('quotes_count', 0),
"has_quotes": combined_report.get('insurance_quotes', {}).get('has_quotes', False),
```

### Complete Zapier Payload Structure

Every Zapier webhook now includes:

```python
{
    # Core identification
    "client_email": str,
    "client_name": str,
    "partner_name": str | None,
    "case_id": str,
    "is_couple": bool,
    "match_confidence": float,

    # Scope of advice (JSON string)
    "scope_of_advice_json": str,

    # Personal information (text)
    "personal_information": str,

    # Insurance sections (text format)
    "life_insurance_main": str,
    "life_insurance_partner": str,
    "life_insurance_notes": str,
    "trauma_insurance_main": str,
    "trauma_insurance_partner": str,
    "trauma_insurance_notes": str,
    "income_protection_main": str,
    "income_protection_partner": str,
    "income_protection_notes": str,
    "health_insurance_main": str,
    "health_insurance_partner": str,
    "health_insurance_notes": str,
    "accidental_injury_main": str,
    "accidental_injury_partner": str,
    "accidental_injury_notes": str,

    # Assets & Liabilities
    "assets_list": str (JSON array),
    "liabilities_list": str (JSON array),
    "assets_table": str,
    "liabilities_table": str,
    "financial_summary": str,
    "total_assets": number,
    "total_liabilities": number,
    "net_worth": number,

    # Insurance Quotes (NEW)
    "quote_partners_life": str (URL),
    "quote_fidelity_life": str (URL),
    "quote_aia": str (URL),
    "quote_asteron": str (URL),
    "quote_chubb": str (URL),
    "quote_nib": str (URL),
    "quotes_count": number,
    "has_quotes": bool,

    # Metadata
    "timestamp": str (ISO 8601),
    "source": "Insurance-SOA-System",
    "payload_version": "1.1"
}
```

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
  ✓ Loaded fact find: cameron_henderson_at_fultonhogan_com_20251112_130039.json
  ✓ Loaded automation form: cameron_henderson_at_fultonhogan_com_20251118_104829.json
  ...
Loaded: 17 fact finds, 10 automation forms

Webhook Endpoints:
--------------------------------------------------
  Fact Find Form:     POST http://localhost:5001/ff
  Automation Form:    POST http://localhost:5001/automation
  Status:             GET  http://localhost:5001/status
  ...

Server starting on http://localhost:5001
```

### Manual Trigger Script

For testing or manually triggering Zapier for existing forms:

```bash
python3 test_insurance_quotes.py email@example.com
```

This script:
1. Loads forms from disk
2. Matches them
3. Processes all data
4. Extracts insurance quotes
5. Triggers Zapier webhook
6. Shows detailed output

### Checking Server Status

```bash
curl http://localhost:5001/status | python3 -m json.tool
```

---

## Troubleshooting

### Problem: Forms Not Triggering Zapier Automatically

**Symptoms**:
- Automation form submitted but no Zapier trigger
- Server shows forms loaded but no match

**Common Causes & Solutions**:

1. **Server Started Before Automation Form Submitted**
   - The server only loads forms at startup
   - Solution: Restart the server
   ```bash
   # Stop server (Ctrl+C)
   # Restart
   python3 src/webhook_server.py
   ```

2. **Low Confidence Score**
   - Threshold is 0.6 (lowered from 0.7)
   - Check confidence: `curl http://localhost:5001/matches`

3. **Email Mismatch**
   - Emails must match exactly (case-insensitive)
   - Check both forms have same email

### Problem: Insurance Quotes Not Appearing in Zapier

**Symptoms**:
- Form has quote uploads but Zapier doesn't receive them

**Solution**:
- Ensure you're using the latest code with insurance_quotes_extractor.py
- Check ZapierPayloadBuilder includes quote fields
- Restart server to load latest code

### Problem: Assets/Liabilities Data Wrong or Missing

**Symptoms**:
- Owner Occupied property not showing
- Mortgage not appearing
- Wrong asset values

**Solution**:
- Latest code fixes field mappings (22/26, 47/287, etc.)
- Handles special case of field 33
- Restart server with latest code

### Problem: Empty Fields Overwriting Data

**Symptoms**:
- Valid fact find data disappearing
- Fields becoming empty after automation form

**Solution**:
- Latest auto_matcher.py only updates non-empty values
- Preserves all fact find data
- Automation form only adds/updates actual values

### Problem: Multiple Old Server Processes

**Symptoms**:
- Old version of code running
- Changes not taking effect

**Solution**:
```bash
# Kill ALL webhook server processes
pkill -f webhook_server

# Start fresh
python3 src/webhook_server.py
```

---

## Recent Updates (November 2025)

### Version 2.0 Changes

1. **Insurance Quotes Extraction**
   - New `insurance_quotes_extractor.py` module
   - Extracts quote URLs from fields 42-47
   - Parses JSON array format from Gravity Forms uploads
   - Adds 8 new fields to Zapier payload

2. **Fixed Assets & Liabilities**
   - Corrected field mappings (22/26, 47/287, 20)
   - Added special handling for field 33
   - Changed "Primary Residence" to "Owner Occupied"
   - Added validation for form totals

3. **Smart Data Merging**
   - Fixed issue where empty automation fields overwrote fact find data
   - Only non-empty values update combined data
   - Preserves all valid data from both forms

4. **Zapier Payload Updates**
   - Added insurance quote fields
   - Ensures all quote URLs are included
   - Added quotes_count and has_quotes summary fields

5. **Confidence Threshold**
   - Lowered from 0.7 to 0.6 for better matching

6. **Test Scripts**
   - `test_insurance_quotes.py` - Test quote extraction
   - `manual_trigger.py` - Manually trigger Zapier

### Known Issues & Workarounds

1. **Server Doesn't Auto-Reload Forms**
   - Workaround: Restart server when new forms arrive
   - Future fix: Implement file watching or periodic reload

2. **Manual Trigger Needed for Existing Forms**
   - Existing forms on disk don't auto-trigger
   - Use test_insurance_quotes.py to manually trigger

---

## Zapier Integration Details

### Webhook Payload Structure

The Zapier webhook receives a standardized payload with consistent field structure:

#### Core Identification Fields
- `client_email` - Client's email address
- `client_name` - Client's full name
- `partner_name` - Partner's name (if couple)
- `case_id` - Unique case identifier
- `is_couple` - Boolean indicating if couple
- `match_confidence` - Matching confidence score (0.0-1.0)

#### Insurance Coverage Fields (Text Format)
Each insurance type has three fields:
- `{type}_main` - Main person's coverage details
- `{type}_partner` - Partner's coverage (if couple)
- `{type}_notes` - Additional notes

Types: `life_insurance`, `trauma_insurance`, `income_protection`, `health_insurance`, `accidental_injury`

#### Assets & Liabilities Fields
- `assets_list` - JSON array of assets
- `liabilities_list` - JSON array of liabilities
- `assets_table` - Formatted text table
- `liabilities_table` - Formatted text table
- `financial_summary` - Summary text
- `total_assets` - Total assets value
- `total_liabilities` - Total liabilities value
- `net_worth` - Calculated net worth

#### Insurance Quote Fields
- `quote_partners_life` - Partners Life quote URL
- `quote_fidelity_life` - Fidelity Life quote URL
- `quote_aia` - AIA quote URL
- `quote_asteron` - Asteron quote URL
- `quote_chubb` - Chubb quote URL
- `quote_nib` - NIB quote URL
- `quotes_count` - Number of quotes uploaded
- `has_quotes` - Boolean if any quotes exist

#### Metadata
- `timestamp` - ISO format timestamp
- `source` - Always "Insurance-SOA-System"
- `payload_version` - Current version (1.1)

### Zapier Webhook Configuration

1. **Webhook URL**: Configure in `config/zapier_webhook.json`
2. **Trigger**: Automatic when forms match with confidence >= 0.6
3. **Manual Trigger**: Use `manual_trigger.py` or `test_insurance_quotes.py`

### Testing Zapier Integration

```bash
# Test with specific client
python3 test_insurance_quotes.py "client@email.com"

# Manual trigger for existing forms
python3 manual_trigger.py "client@email.com"

# Check what would be sent without triggering
curl http://localhost:5001/test-zapier/client@email.com
```

---

## Support

For issues or questions:

1. Check server logs for error messages
2. Verify configuration files are correct
3. Ensure server has latest code (git pull)
4. Restart server to load new forms
5. Use manual trigger script for testing
6. Check Zapier task history for webhook catches

**Quick Fixes**:
- Forms not matching → Restart server
- Quotes not appearing → Check latest code deployed
- Data missing → Verify field mappings in extractors
- Old code running → Kill all processes, restart

---

## API Endpoints Reference

### Core Webhooks

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ff` | POST | Receive Fact Find form |
| `/webhook/fact-find` | POST | Alias for `/ff` |
| `/automation` | POST | Receive Automation form |
| `/webhook/automation-form` | POST | Alias for `/automation` |

### Status & Monitoring

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/status` | GET | Server status and statistics |
| `/matches` | GET | List all matched forms |
| `/health` | GET | Health check |

### Report Generation

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/generate/scope-of-advice` | POST | Generate scope of advice |
| `/generate/personal-information` | POST | Generate personal info |
| `/generate/combined-report` | POST | Generate full report |
| `/generate/life-insurance-fields` | POST | Generate life insurance |
| `/generate/trauma-insurance-fields` | POST | Generate trauma insurance |

---

**End of Documentation**

Version 2.0 - Updated November 18, 2025
Includes insurance quotes extraction, fixed assets/liabilities, and smart data merging.