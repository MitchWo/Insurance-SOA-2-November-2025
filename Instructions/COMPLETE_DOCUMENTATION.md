# Insurance Statement of Advice (SOA) System - Complete Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Data Flow](#data-flow)
4. [Directory Structure](#directory-structure)
5. [Core Components](#core-components)
6. [File-by-File Documentation](#file-by-file-documentation)
7. [Setup Instructions](#setup-instructions)
8. [Configuration](#configuration)
9. [API Endpoints](#api-endpoints)
10. [Data Processing Pipeline](#data-processing-pipeline)
11. [Zapier Integration](#zapier-integration)
12. [Troubleshooting](#troubleshooting)

---

## System Overview

The Insurance SOA System is a sophisticated webhook-based application that processes insurance fact-finding and automation forms from Gravity Forms (WordPress), performs intelligent matching, generates comprehensive insurance needs analysis, and automatically triggers Zapier workflows with complete insurance recommendations.

### Key Features
- **Dual Form Processing**: Handles both fact-find forms and automation forms
- **Intelligent Matching**: Automatically matches forms from the same client using email and fuzzy matching
- **Insurance Analysis**: Generates recommendations for Life, Trauma, Income Protection, Health, and Accidental Injury insurance
- **Automated Workflows**: Triggers Zapier webhooks automatically when forms match
- **Comprehensive Reporting**: Creates detailed Scope of Advice and Where Are You Now reports

---

## Architecture

```
┌─────────────────┐
│  Gravity Forms  │ (WordPress)
│   - Fact Find   │
│   - Automation  │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────┐
│     ngrok       │ (Public Tunnel)
│ Exposes local   │
│ webhook server  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      WEBHOOK SERVER (Flask)         │
│  ┌─────────────────────────────┐    │
│  │   Form Reception Layer      │    │
│  │  - /ff endpoint             │    │
│  │  - /automation endpoint     │    │
│  └──────────┬──────────────────┘    │
│             │                        │
│  ┌──────────▼──────────────────┐    │
│  │   Form Matching Engine      │    │
│  │  - Email matching           │    │
│  │  - Fuzzy logic matching     │    │
│  │  - Confidence scoring       │    │
│  └──────────┬──────────────────┘    │
│             │                        │
│  ┌──────────▼──────────────────┐    │
│  │  Insurance Processors       │    │
│  │  - Life Insurance           │    │
│  │  - Trauma Insurance         │    │
│  │  - Income Protection        │    │
│  │  - Health Insurance         │    │
│  │  - Accidental Injury        │    │
│  └──────────┬──────────────────┘    │
│             │                        │
│  ┌──────────▼──────────────────┐    │
│  │   Report Generators         │    │
│  │  - Scope of Advice          │    │
│  │  - Where Are You Now        │    │
│  │  - Combined Report          │    │
│  └──────────┬──────────────────┘    │
│             │                        │
│  ┌──────────▼──────────────────┐    │
│  │   Zapier Trigger            │    │
│  │  - Auto-trigger on match    │    │
│  │  - Retry logic              │    │
│  │  - Error handling           │    │
│  └──────────┬──────────────────┘    │
└─────────────┼───────────────────────┘
              │
              ▼
     ┌────────────────┐
     │     Zapier     │
     │   Workflows    │
     └────────────────┘
```

---

## Data Flow

### 1. Form Submission Flow
```
User fills WordPress form → Gravity Forms webhook → ngrok tunnel → Local webhook server
```

### 2. Form Processing Flow
```
Receive form data → Parse JSON → Extract email → Store in data/forms/ → Check for match
```

### 3. Matching Flow
```
Check email match → Calculate confidence score → If confident (>0.7) → Generate reports → Trigger Zapier
```

### 4. Report Generation Flow
```
Load both forms → Extract insurance fields → Calculate needs → Generate sections → Combine into report
```

---

## Directory Structure

```
Insurance-SOA-main/
│
├── src/                          # Source code directory
│   ├── webhook_server.py         # Main Flask server - handles all webhooks
│   ├── form_matcher.py           # Form matching logic with fuzzy matching
│   │
│   ├── models/                   # Data models
│   │   ├── fact_find_form.py    # Fact find form data model
│   │   └── automation_form.py    # Automation form data model
│   │
│   ├── processors/               # Data processors
│   │   ├── form_processor.py    # Base form processing logic
│   │   ├── fact_find_processor.py      # Fact find specific processing
│   │   ├── automation_processor.py      # Automation form processing
│   │   ├── combined_processor.py        # Combines both forms
│   │   ├── scope_of_advice_generator.py # Generates scope sections
│   │   ├── where_are_you_now_generator.py # Generates current situation
│   │   ├── zapier_trigger.py           # Handles Zapier webhooks
│   │   └── auto_matcher.py             # Automatic matching and triggering
│   │
│   └── generators/               # Insurance field extractors
│       ├── life_insurance_fields.py     # Life insurance calculator
│       ├── trauma_insurance_fields.py   # Trauma insurance calculator
│       ├── income_protection_fields.py  # Income protection calculator
│       ├── health_insurance_fields.py   # Health insurance analyzer
│       └── accidental_injury_fields.py  # ACC top-up analyzer
│
├── data/                         # Data storage
│   ├── forms/                    # Raw form submissions
│   │   ├── fact_find/           # Fact find forms (JSON)
│   │   └── automation/          # Automation forms (JSON)
│   ├── matches/                 # Matched form pairs
│   └── reports/                 # Generated reports
│
├── config/                      # Configuration files
│   └── zapier_config.json      # Zapier webhook configuration
│
├── tests/                       # Test files
│   ├── test_fact_find.py       # Test fact find processing
│   ├── test_automation.py      # Test automation processing
│   ├── test_combined.py        # Test combined processing
│   └── test_zapier.py          # Test Zapier integration
│
├── monitor_webhooks.sh          # Monitoring script
├── requirements.txt             # Python dependencies
├── combined_report.json        # Sample combined report
└── README.md                    # Basic readme
```

---

## Core Components

### 1. Webhook Server (`src/webhook_server.py`)
The heart of the system - a Flask application that:
- Runs on port 5001
- Receives form submissions from Gravity Forms
- Manages form storage and matching
- Provides REST API endpoints
- Triggers Zapier webhooks automatically

### 2. Form Matcher (`src/form_matcher.py`)
Intelligent matching system that:
- Matches forms by email address
- Uses fuzzy logic for partial matches
- Calculates confidence scores (0-1)
- Handles multiple form versions

### 3. Insurance Processors
Five specialized processors that extract and calculate insurance needs:
- **Life Insurance**: Calculates coverage needs based on debts, income replacement, education costs
- **Trauma Insurance**: Determines lump sum needs for critical illness
- **Income Protection**: Calculates monthly benefit requirements
- **Health Insurance**: Analyzes health coverage needs
- **Accidental Injury**: Assesses ACC top-up requirements

### 4. Report Generators
- **Scope of Advice**: Generates 10 sections including what's covered, limitations, next steps
- **Where Are You Now**: Creates current situation analysis with financial summaries
- **Combined Report**: Merges all data into comprehensive JSON for Zapier

### 5. Zapier Integration
- Automatic webhook triggering when forms match
- Retry logic (3 attempts with 5-second delays)
- Configurable via JSON file
- Sends complete insurance analysis data

---

## File-by-File Documentation

### `/src/webhook_server.py`
**Purpose**: Main Flask application server
**Key Functions**:
- `app = Flask(__name__)`: Initialize Flask app
- `@app.route('/ff', methods=['POST'])`: Fact find webhook endpoint
- `@app.route('/automation', methods=['POST'])`: Automation form webhook endpoint
- `@app.route('/status')`: Server health check
- `@app.route('/matches')`: View matched forms
- `@app.route('/generate/combined-report')`: Generate complete report
- `@app.route('/configure/zapier')`: Update Zapier settings

**Important Code Sections**:
```python
# Automatic Zapier triggering on form match
if match_result and match_result.is_confident_match(threshold=0.7):
    from processors.auto_matcher import check_and_trigger_match
    result = check_and_trigger_match(email, matcher, zapier_trigger)
```

### `/src/form_matcher.py`
**Purpose**: Matches fact find and automation forms
**Key Classes**:
- `MatchResult`: Stores match details and confidence
- `FormMatcher`: Main matching engine

**Matching Algorithm**:
1. Primary match: Email address
2. Secondary validation: Name similarity
3. Confidence calculation based on:
   - Email match (0.5 weight)
   - Name similarity (0.3 weight)
   - Time proximity (0.2 weight)

### `/src/processors/zapier_trigger.py`
**Purpose**: Handles Zapier webhook communication
**Key Features**:
- Configuration loading from JSON
- HTTP POST with retry logic
- Timeout handling (30 seconds default)
- Response validation

**Configuration Structure**:
```json
{
  "zapier_webhook_url": "https://hooks.zapier.com/...",
  "enabled": true,
  "retry_attempts": 3,
  "retry_delay_seconds": 5,
  "timeout_seconds": 30
}
```

### `/src/processors/auto_matcher.py`
**Purpose**: Orchestrates automatic matching and Zapier triggering
**Process Flow**:
1. Check for form match
2. Verify confidence threshold (>0.7)
3. Generate all insurance fields
4. Create combined report
5. Trigger Zapier webhook
6. Return status

### `/src/generators/life_insurance_fields.py`
**Purpose**: Calculates life insurance needs
**Calculations**:
- Total needs = Debt + Income replacement + Education + Final expenses + Other
- Net coverage = Total needs - Existing assets - KiwiSaver
- Returns individual field values for Zapier

**Field Mappings**:
- Field 380: Debt repayment
- Field 381: Replacement income years
- Field 382: Annual replacement income
- Field 383: Child education costs
- Field 384: Final expenses
- Field 504: Total life insurance needed

### `/src/generators/trauma_insurance_fields.py`
**Purpose**: Calculates trauma/critical illness coverage
**Components**:
- Medical bills and recovery costs
- Income support during recovery
- Home modifications
- Childcare assistance
- Debt repayment stress buffer

**Field Mappings**:
- Fields 402-418: Individual trauma components
- Field 506: Total trauma coverage needed

### `/src/generators/income_protection_fields.py`
**Purpose**: Determines income protection requirements
**Calculations**:
- Monthly benefit = 75% of gross income
- Wait period determination
- Benefit period (to age 65)
- ACC offset considerations

**Field Mappings**:
- Fields 420-444: Income protection parameters
- Field 508: Monthly benefit amount

### `/src/generators/health_insurance_fields.py`
**Purpose**: Analyzes health insurance needs
**Analysis Includes**:
- Coverage level (basic/moderate/comprehensive)
- Specialist and surgical coverage
- Non-Pharmac medications
- Excess preferences
- Family coverage needs

**Field Mappings**:
- Fields 449-461: Health insurance preferences
- Field 510: Recommended plan type

### `/src/generators/accidental_injury_fields.py`
**Purpose**: Assesses ACC top-up requirements
**Evaluates**:
- Income replacement gaps
- Lump sum benefit needs
- Rehabilitation costs
- Loss of income coverage

**Field Mappings**:
- Fields 446-447: ACC assessment

---

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- ngrok account and auth token
- Gravity Forms on WordPress
- Zapier account

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone [repository-url]
cd Insurance-SOA-main

# Install Python dependencies
pip3 install -r requirements.txt
```

### Step 2: Configure ngrok
```bash
# Install ngrok (if not already installed)
# On Mac:
brew install ngrok

# Configure auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Start ngrok tunnel
ngrok http 5001
```

### Step 3: Configure Zapier
Edit `config/zapier_config.json`:
```json
{
  "zapier_webhook_url": "YOUR_ZAPIER_WEBHOOK_URL",
  "enabled": true,
  "trigger_on_match": true
}
```

### Step 4: Start the Server
```bash
python3 src/webhook_server.py
```

### Step 5: Configure Gravity Forms
In WordPress Gravity Forms settings:
1. Go to Form Settings → Webhooks
2. Add webhook for Fact Find form:
   - URL: `https://YOUR_NGROK_URL.ngrok-free.dev/ff`
   - Method: POST
   - Format: JSON
3. Add webhook for Automation form:
   - URL: `https://YOUR_NGROK_URL.ngrok-free.dev/automation`
   - Method: POST
   - Format: JSON

---

## Configuration

### Zapier Configuration (`config/zapier_config.json`)
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

### Environment Variables
No environment variables required - all configuration is file-based.

---

## API Endpoints

### Form Reception Endpoints

#### POST `/ff` - Receive Fact Find Form
**Purpose**: Receives fact find form from Gravity Forms
**Request Body**: JSON with all form fields
**Response**:
```json
{
  "status": "success",
  "message": "Fact find form received",
  "form_id": "email_timestamp"
}
```

#### POST `/automation` - Receive Automation Form
**Purpose**: Receives automation form from Gravity Forms
**Request Body**: JSON with all form fields
**Response**:
```json
{
  "status": "success",
  "message": "Automation form received",
  "form_id": "email_timestamp",
  "match_found": true,
  "zapier_triggered": true
}
```

### Status Endpoints

#### GET `/status` - Server Status
**Response**:
```json
{
  "status": "running",
  "unmatched_fact_finds": 2,
  "unmatched_automation_forms": 1,
  "statistics": {
    "total_fact_finds": 10,
    "total_automation_forms": 8,
    "total_matches": 7,
    "confident_matches": 6,
    "average_confidence": 0.85
  }
}
```

#### GET `/matches` - View Matched Forms
**Response**:
```json
{
  "total_matches": 5,
  "confident_matches": 4,
  "matches": [
    {
      "email": "client@example.com",
      "confidence": 0.95,
      "fact_find_id": "...",
      "automation_form_id": "..."
    }
  ]
}
```

### Generator Endpoints

#### POST `/generate/combined-report` - Generate Full Report
**Request Body**:
```json
{
  "fact_find_id": "email_timestamp",
  "automation_form_id": "email_timestamp"
}
```
**Response**: Complete combined report with all insurance fields

#### POST `/generate/scope-of-advice` - Generate Scope Only
**Response**: Scope of advice sections only

#### POST `/generate/where-are-you-now` - Generate Current Situation
**Response**: Where are you now analysis only

### Configuration Endpoints

#### POST `/configure/zapier` - Update Zapier Settings
**Request Body**:
```json
{
  "zapier_webhook_url": "https://hooks.zapier.com/...",
  "enabled": true
}
```

---

## Data Processing Pipeline

### 1. Form Reception
```python
# Webhook receives form data
@app.route('/ff', methods=['POST'])
def receive_fact_find():
    data = request.json
    email = extract_email(data)
    save_form(data, 'fact_find')
    check_for_match(email)
```

### 2. Email Extraction
Forms use different field IDs for email:
- Fact Find: Field "6"
- Automation: Field "39"

### 3. Form Storage
Forms are saved as JSON files:
- Fact Find: `data/forms/fact_find/email_timestamp.json`
- Automation: `data/forms/automation/email_timestamp.json`

### 4. Matching Process
```python
def find_match(email):
    # Check for corresponding form
    fact_finds = load_fact_finds_for_email(email)
    automation_forms = load_automation_forms_for_email(email)

    # Calculate confidence
    confidence = calculate_match_confidence(fact_find, automation_form)

    if confidence > 0.7:
        return MatchResult(fact_find, automation_form, confidence)
```

### 5. Insurance Calculations

#### Life Insurance Calculation
```python
total_needs = (
    debt_repayment +
    (annual_income * years_replacement) +
    child_education +
    final_expenses +
    other_considerations
)
net_coverage = total_needs - existing_assets - kiwisaver
```

#### Trauma Insurance Calculation
```python
total_trauma = (
    medical_bills +
    recovery_income +
    home_modifications +
    childcare_assistance +
    debt_buffer
)
```

#### Income Protection Calculation
```python
monthly_benefit = gross_monthly_income * 0.75
annual_needs = monthly_benefit * 12 * years_to_65
```

### 6. Report Generation
Combined report includes:
- Client identification
- All 5 insurance type analyses
- Scope of advice (10 sections)
- Where are you now (10 sections)
- Validation metadata

### 7. Zapier Triggering
```python
def trigger_zapier(combined_data):
    payload = {
        'timestamp': datetime.now().isoformat(),
        'source': 'insurance-soa-system',
        'event': 'forms_matched_and_processed',
        'data': combined_data
    }

    response = requests.post(
        webhook_url,
        json=payload,
        timeout=30,
        headers={'Content-Type': 'application/json'}
    )
```

---

## Zapier Integration

### Webhook Payload Structure
```json
{
  "timestamp": "2025-10-29T15:30:24",
  "source": "insurance-soa-system",
  "event": "forms_matched_and_processed",
  "data": {
    "client_name": "John Smith",
    "email": "john@example.com",
    "is_couple": false,
    "match_confidence": 0.95,
    "life_insurance": {
      "main_needs_insurance": true,
      "main_total_needs": 500000,
      "main_net_coverage": 400000,
      "main_debt_repayment": 200000,
      "main_replacement_income": 150000,
      // ... all other fields
    },
    "trauma_insurance": {
      "main_needs_trauma": true,
      "main_total_trauma": 150000,
      // ... all other fields
    },
    "income_protection": {
      "main_needs_income_protection": true,
      "main_monthly_benefit": 5000,
      // ... all other fields
    },
    "health_insurance": {
      "main_needs_health_insurance": true,
      "main_plan_type": "comprehensive",
      // ... all other fields
    },
    "accidental_injury": {
      "acc_topup_recommended": true,
      // ... all other fields
    },
    "scope_of_advice": {
      "products_in_scope": [...],
      "products_out_of_scope": [...],
      "sections": {
        "summary": "...",
        "in_scope": "...",
        // ... 8 more sections
      }
    },
    "where_are_you_now": {
      "financial_summary": {...},
      "personal_summary": {...},
      "sections": {
        "personal_summary": "...",
        "employment_status": "...",
        // ... 8 more sections
      }
    },
    "validation": {
      "total_sections_generated": 20,
      "all_sections_valid": true,
      "includes_all_insurance_types": true
    }
  }
}
```

### Zapier Workflow Setup
1. Create a Webhook trigger in Zapier
2. Copy the webhook URL
3. Update `config/zapier_config.json` with the URL
4. Use the data fields in subsequent Zapier steps

### Available Fields for Zapier Actions
All fields are prefixed by insurance type:
- `life_insurance.main_*` - Life insurance fields
- `trauma_insurance.main_*` - Trauma fields
- `income_protection.main_*` - Income protection fields
- `health_insurance.main_*` - Health insurance fields
- `accidental_injury.*` - ACC top-up fields

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Webhook Server Won't Start
**Error**: `ModuleNotFoundError: No module named 'flask'`
**Solution**:
```bash
pip3 install flask requests
```

#### 2. ngrok Tunnel Not Working
**Error**: Connection refused
**Solution**:
```bash
# Ensure server is running first
python3 src/webhook_server.py

# Then start ngrok in separate terminal
ngrok http 5001
```

#### 3. Forms Not Matching
**Issue**: Forms submitted but no match detected
**Check**:
- Email fields are identical
- Confidence threshold (default 0.7)
- Check logs for confidence scores

#### 4. Zapier Not Triggering
**Check**:
- `enabled: true` in config
- Correct webhook URL
- Network connectivity
- Check server logs for trigger attempts

#### 5. Missing Form Fields
**Issue**: Some insurance calculations returning 0
**Check**:
- Form field mappings in Gravity Forms
- Field IDs match expected values
- Data type conversions (string to float)

### Debug Mode
Enable detailed logging:
```python
# In webhook_server.py
app.debug = True
app.logger.setLevel(logging.DEBUG)
```

### Monitoring
Use the monitoring script:
```bash
./monitor_webhooks.sh
```
This polls the `/status` endpoint every 2 seconds.

### Log Files
Check Flask output for:
- Form reception confirmations
- Matching attempts and confidence scores
- Zapier trigger attempts
- Any Python exceptions

---

## Testing

### Manual Testing

#### Test Form Reception
```bash
# Test fact find endpoint
curl -X POST http://localhost:5001/ff \
  -H "Content-Type: application/json" \
  -d @tests/sample_fact_find.json

# Test automation endpoint
curl -X POST http://localhost:5001/automation \
  -H "Content-Type: application/json" \
  -d @tests/sample_automation.json
```

#### Test Report Generation
```bash
curl -X POST http://localhost:5001/generate/combined-report \
  -H "Content-Type: application/json" \
  -d '{"fact_find_id": "test@test.com_20251029_145520", "automation_form_id": "test@test.com_20251029_144607"}'
```

#### Test Zapier Webhook
```python
python3 -c "from src.processors.zapier_trigger import test_zapier_trigger; test_zapier_trigger()"
```

### Automated Testing
```bash
# Run all tests
python3 -m pytest tests/

# Run specific test
python3 -m pytest tests/test_zapier.py
```

---

## Security Considerations

### Data Protection
- Forms contain PII (Personally Identifiable Information)
- Store data securely
- Use HTTPS for all webhooks
- Implement access controls

### Webhook Security
- Validate webhook signatures (if available)
- Implement rate limiting
- Use webhook secret tokens
- Monitor for unusual activity

### Zapier Security
- Use HTTPS webhook URLs only
- Rotate webhook URLs periodically
- Monitor Zapier logs
- Implement webhook authentication

---

## Performance Optimization

### Caching
- Form data cached in memory during session
- Match results cached to avoid recalculation

### Async Processing
Consider implementing:
- Background job queue for heavy processing
- Async Zapier triggers
- Database instead of file storage for scale

### Monitoring Metrics
- Form processing time
- Match confidence distribution
- Zapier trigger success rate
- System resource usage

---

## Maintenance

### Regular Tasks
1. Clear old form data (>90 days)
2. Archive generated reports
3. Review match confidence thresholds
4. Update Zapier webhook URLs
5. Monitor error logs

### Backup Strategy
```bash
# Backup forms and reports
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Backup configuration
cp -r config/ config_backup_$(date +%Y%m%d)/
```

### Updates
1. Test updates in development environment
2. Backup data before updates
3. Update during low-traffic periods
4. Monitor after updates

---

## Support and Contact

For issues or questions about the Insurance SOA System:
1. Check this documentation first
2. Review error logs
3. Test with sample data
4. Contact system administrator

---

## Appendix

### A. Field Mappings Reference
Complete list of all Gravity Forms field IDs and their meanings:

#### Fact Find Form Fields
- Field 6: Email address
- Field 8: Client type (single/couple)
- Field 10: First name
- Field 14: Last name
- Field 380-400: Life insurance fields
- Field 402-418: Trauma insurance fields
- Field 420-444: Income protection fields
- Field 446-447: ACC fields
- Field 449-461: Health insurance fields

#### Automation Form Fields
- Field 39: Email address
- Field 40: Client type
- Field 42: First name
- Field 45: Last name
- Complete field mappings in form models

### B. Sample Configurations

#### Minimal Configuration
```json
{
  "zapier_webhook_url": "https://hooks.zapier.com/...",
  "enabled": true
}
```

#### Full Configuration
```json
{
  "zapier_webhook_url": "https://hooks.zapier.com/...",
  "enabled": true,
  "trigger_on_match": true,
  "include_all_fields": true,
  "retry_attempts": 3,
  "retry_delay_seconds": 5,
  "timeout_seconds": 30,
  "headers": {
    "Content-Type": "application/json",
    "X-Source": "Insurance-SOA-System",
    "Authorization": "Bearer YOUR_TOKEN"
  }
}
```

### C. Glossary
- **SOA**: Statement of Advice
- **PII**: Personally Identifiable Information
- **ACC**: Accident Compensation Corporation (New Zealand)
- **TPD**: Total Permanent Disability
- **Pharmac**: Pharmaceutical Management Agency (New Zealand)

---

*End of Documentation - Version 1.0 - October 2025*