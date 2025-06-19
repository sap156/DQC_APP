# Data Quality Control Rules Manager - User Guide

A comprehensive Streamlit application for managing Data Quality Control (DQC) rules with automated rule name generation, validation, and CSV export capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Step-by-Step User Guide](#step-by-step-user-guide)
  - [1. Uploading Existing Rules](#1-uploading-existing-rules)
  - [2. Adding New Rules](#2-adding-new-rules)
  - [3. Viewing and Editing Rules](#3-viewing-and-editing-rules)
  - [4. Validating Rules](#4-validating-rules)
  - [5. Exporting Rules](#5-exporting-rules)
- [Field Descriptions](#field-descriptions)
- [Validation Rules](#validation-rules)
- [Rule Name Generation](#rule-name-generation)
- [Rule Description Generation](#rule-description-generation)
- [File Format Requirements](#file-format-requirements)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

## Overview

The Data Quality Control Rules Manager is designed to streamline the creation, management, and validation of DQC rules. It provides automated rule name generation based on business standards, comprehensive validation, and seamless CSV import/export functionality.

## Features

- **📂 CSV Import/Export**: Upload existing rules and download processed rules with tilde (~) delimiter
- **➕ Automated Rule Creation**: Auto-generates rule names and descriptions based on configuration
- **✏️ Rule Editing**: Full inline editing capabilities for all rule fields
- **🔍 Comprehensive Validation**: Built-in validation against business rules and naming standards
- **📊 Rule Management**: View, edit, delete, and organize rules with summary statistics
- **🎯 Real-time Feedback**: Instant validation feedback and auto-uppercase conversion

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dqc-rules-manager
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit pandas
   ```

3. **Run the application**
   ```bash
   streamlit run dqc_app.py
   ```

4. **Access the application**
   - Open your web browser and navigate to `http://localhost:8501`

## Getting Started

The application is divided into three main sections:

1. **📂 Upload Existing Rules** - Import rules from CSV files
2. **➕ Add New Rule** - Create new rules with automated assistance
3. **📋 View & Edit Rules** - Manage, validate, and export your rules

## Step-by-Step User Guide

### 1. Uploading Existing Rules

#### Process:
1. Navigate to the "📂 Upload Existing Rules" section
2. Click "Choose a CSV file" button
3. Select a CSV file with tilde (~) delimiter
4. Wait for upload confirmation

#### Requirements:
- **File Format**: CSV with tilde (~) delimiter
- **File Size**: Maximum 200MB
- **Headers**: Must match the expected field names (see [Field Descriptions](#field-descriptions))

#### What Happens:
- File is parsed and validated
- Text fields are automatically converted to uppercase
- Rules are loaded into the application memory
- Success message displays the number of imported records

### 2. Adding New Rules

#### Step-by-Step Process:

1. **Configure Core Settings** (Left Column):
   - **APPL_CD**: Enter complete application code (e.g., `EMM_PAYMENTS`, `EMM_FINANCE`)
   - **RULE_VALID_CTGY_NM**: Select validation category (`POST` or `PRE`)
   - **RULE_VALID_METH_CD**: Select validation method (triggers auto-generation)
   - **Source Database Settings**: Choose source database, schema, and table

2. **Configure Target Settings** (Right Column):
   - **RULE_TRGT_DB_NM**: Select target database
   - **RULE_TRGT_SCHM_NM**: Select target schema
   - **RULE_TRGT_OBJ_ID_TXT**: Enter target table name
   - **RULE_TRGT_DATA_LAYER_NM**: Select data layer (auto-updates database)
   - **RULE_ACTV_IND**: Set rule as active (`Y`) or inactive (`N`)

3. **Review Auto-Generated Fields**:
   - **RULE_NM**: Auto-generated based on your selections
   - **RULE_DSC_TXT**: Auto-generated description
   - **RULE_ABORT_IND**: Auto-populated based on method
   - **RULE_TRGT_ATTR_NM**: Editable for SUM checks, auto-set to "NA" for others

4. **Enter Rule Logic**:
   - **RULE_LOGIC_TXT**: Enter your SQL statement for the rule

5. **Add the Rule**:
   - Click "➕ Add Rule" button
   - Review any validation errors
   - Rule is added to the collection upon successful validation

#### Important Notes:
- Text fields are automatically converted to uppercase
- Rule names are auto-generated following business standards
- Some fields may require manual selection when placeholders like `(STG|INFO)` appear

### 3. Viewing and Editing Rules

#### Overview Section:
- **Summary Statistics**: View total rules, active rules, and inactive rules
- **Complete Rules Table**: Full dataframe showing all fields and rules

#### Individual Rule Management:

1. **Locate the Rule**: Find the rule in the expandable list
2. **Edit Fields**: 
   - Modify any editable field in the form
   - System fields (timestamps, IDs) are read-only
   - Text fields automatically convert to uppercase

3. **Save Changes**:
   - Click "💾 Save Changes" to apply edits
   - Validation runs automatically
   - Success confirmation or error messages displayed

4. **Delete Rules**:
   - Click "🗑️ Delete Rule" to remove a rule
   - Immediate confirmation and list refresh

#### Editable Field Categories:
- **Core Information**: Application code, rule name, description, validation settings
- **Source Configuration**: Database, schema, table, and attribute information
- **Target Configuration**: Target database settings and data layer
- **Threshold Configuration**: Acceptance variance and threshold values
- **Additional Information**: Remarks and asset information
- **Rule Logic**: SQL statement for the rule

### 4. Validating Rules

#### Validation Options:

1. **Real-time Validation**: Automatic validation when adding or editing rules
2. **Bulk Validation**: Click "🔍 Validate All Rules" to check all rules

#### Validation Process:
- Each rule is checked against all validation criteria
- Errors are displayed with specific field references
- Row numbers are provided for bulk validation errors

### 5. Exporting Rules

#### Export Process:
1. Navigate to the "📋 View & Edit Rules" section
2. Click "📥 Download CSV" button
3. File downloads automatically with naming convention: `DATA_QC_RULE_INFO_[APPL_CD].csv`

#### Export Features:
- Tilde (~) delimiter format
- All fields included in standard order
- Ready for system import
- Filename includes application code for organization

## Field Descriptions

### Core Fields
| Field | Description | Auto-Generated | Editable |
|-------|-------------|----------------|----------|
| `DATA_QC_ID` | Data Quality Control ID | ✅ | ❌ |
| `APPL_CD` | Application Code | ❌ | ✅ |
| `RULE_NM` | Rule Name | ✅ | ✅ |
| `RULE_DSC_TXT` | Rule Description | ✅ | ✅ |
| `RULE_FREQ_CD` | Rule Frequency Code | ✅ | ❌ |

### Validation Fields
| Field | Description | Options |
|-------|-------------|---------|
| `RULE_VALID_CTGY_NM` | Validation Category | `POST`, `PRE` |
| `RULE_VALID_METH_CD` | Validation Method | `CNT_CHK`, `SUM_CHK`, `DIFF_CNT_CHK`, `DIFF_SUM_CHK`, `DUP_CHK`, `OVERLAP_CHK` |
| `RULE_ABORT_IND` | Abort Indicator | `Y`, `N` (Auto-populated) |
| `RULE_ACTV_IND` | Active Indicator | `Y`, `N` |

### Source Configuration
| Field | Description | Options |
|-------|-------------|---------|
| `RULE_SRC_DB_NM` | Source Database | `DL2_CHIEF_FINANCIAL_OFFICE_RQ`, `CFOPAYMENTSTG`, `IPENTSTRIPEDB` |
| `RULE_SRC_SCHM_NM` | Source Schema | `ENTERPRISE`, `APP_CFOPYMTS`, `STRIPE`, `PAYMENTS` |
| `RULE_SRC_OBJ_ID_TXT` | Source Table | User-defined |
| `RULE_SRC_ATTR_NM` | Source Attribute | Auto-set to "NA" |

### Target Configuration
| Field | Description | Options |
|-------|-------------|---------|
| `RULE_TRGT_DB_NM` | Target Database | `CFOPAYMENTSDB`, `CFOINFODMDB` |
| `RULE_TRGT_SCHM_NM` | Target Schema | `APP_CFOPYMTS`, `ENTERPRISE`, `STRIPE`, `PAYMENTS` |
| `RULE_TRGT_OBJ_ID_TXT` | Target Table | User-defined |
| `RULE_TRGT_ATTR_NM` | Target Attribute | Required for SUM checks |
| `RULE_TRGT_DATA_LAYER_NM` | Data Layer | `DL2`, `DL3`, `OnPrem_HOP1`, `OnPrem_HOP2`, `OnPrem_HOP3`, `OnPrem` |

### System Fields
| Field | Description | Auto-Managed |
|-------|-------------|--------------|
| `CREA_PRTY_ID` | Creator Party ID | ✅ |
| `CREA_TS` | Creation Timestamp | ✅ |
| `UPDT_PRTY_ID` | Updater Party ID | ✅ |
| `UPDT_TS` | Update Timestamp | ✅ |
| `ASSET_ID` | Asset ID | ✅ |
| `RULE_EFF_DT` | Rule Effective Date | ✅ |
| `RULE_EXP_DT` | Rule Expiration Date | ✅ |

## Validation Rules

The application performs comprehensive validation to ensure data quality and business rule compliance:

### 1. Application Code Validation
- **Rule**: `APPL_CD` must be completed and meaningful
- **Checks**:
  - Cannot be blank or just "EMM_"
  - Cannot end with underscore only
  - Must be at least 4 characters long
- **Error Messages**:
  - "APPL_CD must be completed. Please provide a full application code"
  - "APPL_CD appears to be too short. Please provide a meaningful application code"

### 2. Rule Abort Indicator Validation
- **Rule**: `RULE_ABORT_IND` must align with `RULE_VALID_METH_CD`
- **Logic**:
  - For `CNT_CHK` or `SUM_CHK`: `RULE_ABORT_IND` must be "N"
  - For all other methods: `RULE_ABORT_IND` must be "Y"
- **Error Messages**:
  - "RULE_ABORT_IND must be 'N' for CNT_CHK or SUM_CHK"
  - "RULE_ABORT_IND must be 'Y' for RULE_VALID_METH_CD values other than CNT_CHK or SUM_CHK"

### 3. Target Attribute Validation
- **Rule**: `RULE_TRGT_ATTR_NM` requirements based on method
- **Logic**:
  - For `SUM_CHK` or `DIFF_SUM_CHK`: Cannot be blank or "NA"
  - Must specify the column/attribute name to sum
- **Error Message**:
  - "RULE_TRGT_ATTR_NM cannot be blank or 'NA' when RULE_VALID_METH_CD is SUM_CHK or DIFF_SUM_CHK"

### 4. Rule Sequence Number Validation
- **Rule**: Prevent duplicate sequence numbers for same table and category
- **Logic**:
  - Combination of `RULE_TRGT_OBJ_ID_TXT`, `RULE_VALID_CTGY_NM`, and `RULE_SEQ_NR` must be unique
- **Error Message**:
  - "Duplicate RULE_TRGT_OBJ_ID_TXT with same RULE_VALID_CTGY_NM and RULE_SEQ_NR"

### 5. Rule Name Uniqueness Validation
- **Rule**: Rule names must be unique across all rules
- **Logic**: No two rules can have identical `RULE_NM`
- **Error Message**:
  - "RULE_NM already exists"

### 6. Rule Name Pattern Validation
- **Rule**: Rule names must follow established naming standards
- **Patterns Supported**:
  - `^[A-Z0-9_]+OP_HOP3_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+OP_HOP2_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+OP_HOP1_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+DL2_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+FND_DL3_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+STG_DL3_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+INFO_DL3_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+OP_HOP3_HOP2_DIFF_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+OP_HOP2_HOP1_DIFF_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+OP_HOP1_DL2_DIFF_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+DL2_FND_DIFF_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+STG_INFO_DIFF_(CNT|SUM)_CHK$`
  - `^[A-Z0-9_]+INFO_DL3_DUP_CHK$`
  - `^[A-Z0-9_]+INFO_DL3_OVERLAP_CHK$`
- **Error Message**:
  - "RULE_NM does not match any of the specified patterns"

## Rule Name Generation

The application automatically generates rule names following business standards:

### Generation Logic

#### For CFOPAYMENTSDB Target Database:

**Count/Sum Checks (`CNT_CHK`, `SUM_CHK`)**:
- `OnPrem_HOP3` → `{TABLE}_OP_HOP3_{METHOD}`
- `OnPrem_HOP2` → `{TABLE}_OP_HOP2_{METHOD}`
- `OnPrem_HOP1` → `{TABLE}_OP_HOP1_{METHOD}`
- `DL2` → `{TABLE}_DL2_{METHOD}`
- `DL3` → `{TABLE}_FND_DL3_{METHOD}`

**Difference Checks (`DIFF_CNT_CHK`, `DIFF_SUM_CHK`)**:
- `OnPrem` → `{TABLE}_OP_(HOP3_HOP2|HOP2_HOP1)_{METHOD}`
- `DL2` → `{TABLE}_OP_HOP1_DL2_{METHOD}`
- `DL3` → `{TABLE}_DL2_FND_{METHOD}`

**Duplicate/Overlap Checks (`DUP_CHK`, `OVERLAP_CHK`)**:
- `DL3` → `{TABLE}_FND_DL3_{METHOD}`

#### For CFOINFODMDB Target Database:

**Count/Sum Checks**:
- Any layer → `{TABLE}_(STG|INFO)_DL3_{METHOD}`

**Difference Checks**:
- Any layer → `{TABLE}_STG_INFO_{METHOD}`

**Duplicate/Overlap Checks**:
- Any layer → `{TABLE}_INFO_DL3_{METHOD}`

### Manual Selection Required

When rule names contain placeholders, manual editing is required:
- **(STG|INFO)**: Choose either "STG" or "INFO"
- **(HOP3_HOP2|HOP2_HOP1)**: Choose either "HOP3_HOP2" or "HOP2_HOP1"

## Rule Description Generation

Descriptions are automatically generated based on the rule name pattern and method:

### Description Templates

**Count Checks**:
- Single layer: "Performs count check on {layer} table {table_name}"
- Difference: "Performs difference count check between {source_layer} and {target_layer}"

**Sum Checks**:
- Single layer: "Performs sum check on {attribute} on {layer} table {table_name}"
- Difference: "Performs difference sum check on {attribute} between {source_layer} and {target_layer}"

**Duplicate Checks**:
- "Performs duplicate check on {layer} table {table_name}"

**Overlap Checks**:
- "Performs overlap check on {layer} table {table_name}"

### Layer Descriptions
- `OP_HOP3`: "OnPrem Source Records (HOP3)"
- `OP_HOP2`: "OnPrem DS Records (HOP2)"
- `OP_HOP1`: "OnPrem CSV Records (HOP1)"
- `DL2`: "DL2"
- `FND_DL3`: "foundation"
- `STG_DL3`: "staging DL3"
- `INFO_DL3`: "information DL3"

## File Format Requirements

### CSV Import Format
- **Delimiter**: Tilde (~)
- **Encoding**: UTF-8
- **Headers**: Must match field names exactly
- **Size Limit**: 200MB maximum

### Example CSV Structure
```
DATA_QC_ID~APPL_CD~RULE_NM~RULE_DSC_TXT~...
23~EMM_PAYMENTS~PAYMENT_TBL_DL2_CNT_CHK~Performs count check on DL2 table PAYMENT_TBL~...
```

### CSV Export Format
- **Delimiter**: Tilde (~)
- **All Fields**: Complete field set in standard order
- **Filename**: `DATA_QC_RULE_INFO_{APPL_CD}.csv`

## Troubleshooting

### Common Issues and Solutions

#### 1. Upload Errors
**Problem**: "Error reading CSV file"
- **Solution**: Verify file uses tilde (~) delimiter
- **Solution**: Check file encoding is UTF-8
- **Solution**: Ensure file size is under 200MB

#### 2. Validation Errors
**Problem**: Rule fails validation
- **Solution**: Review specific error messages
- **Solution**: Check field requirements in [Validation Rules](#validation-rules)
- **Solution**: Verify rule name follows naming patterns

#### 3. Auto-Generation Issues
**Problem**: Rule name contains placeholders
- **Solution**: Manually edit rule name to remove placeholders
- **Solution**: Choose specific values from options like (STG|INFO)

#### 4. Save Failures
**Problem**: Cannot save rule changes
- **Solution**: Address all validation errors first
- **Solution**: Ensure required fields are completed
- **Solution**: Check for duplicate rule names

### Getting Help

1. **Check Error Messages**: Validation errors provide specific guidance
2. **Review Field Requirements**: See [Field Descriptions](#field-descriptions)
3. **Verify Business Rules**: Ensure compliance with [Validation Rules](#validation-rules)
4. **Check Naming Standards**: Follow [Rule Name Generation](#rule-name-generation) patterns

## Technical Details

### Architecture
- **Frontend**: Streamlit web application
- **Data Storage**: In-memory session state
- **File Processing**: Pandas for CSV operations
- **Validation**: Custom validation engine

### File Structure
```
dqc-rules-manager/
├── dqc_app.py              # Main application file
├── config.py               # Configuration and field definitions
├── validation.py           # Validation rule implementations
├── rule_generation.py      # Rule name and description generation
└── README.md              # This user guide
```

### Dependencies
- `streamlit`: Web application framework
- `pandas`: Data manipulation and CSV processing
- `csv`: CSV file operations
- `io`: Input/output operations
- `datetime`: Date and time handling
- `re`: Regular expression operations

### Session State Management
The application uses Streamlit's session state to maintain:
- Rule collections (`st.session_state.rows`)
- Form field values (`st.session_state.form_*`)
- Validation error states
- Upload status and feedback

---

For additional support or feature requests, please refer to the project documentation or contact the development team.