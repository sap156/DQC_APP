# 🏗️ DDLC Manager

**Data Definition Language Changes Manager for Medallion Architecture**

A comprehensive Streamlit application designed to automate and manage data mapping between DL2 (Data Lake Layer 2), Foundation, and Information layers in a medallion architecture. The app automatically parses DDL scripts and DBT transformations to generate detailed field mappings and Excel reports.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Installation](#-installation)
- [Setup & Usage](#-setup--usage)
- [Supported Patterns](#-supported-patterns)
- [Mandatory Audit Columns](#-mandatory-audit-columns)
- [Excel Report Structure](#-excel-report-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## ✨ Features

### 🔄 **Automated Layer Mapping**
- **DL2 → Foundation**: Parse DDL scripts to extract columns and data types
- **Foundation → Information**: Parse DBT transformations with intelligent logic interpretation

### 🧠 **Smart Parsing**
- **DDL Parser**: Extracts column names, data types from CREATE TABLE statements
- **DBT Parser**: Recognizes `handle_empty_or_null_value` functions and transformation patterns
- **UNKNOWN Pattern Handling**: Marks unrecognized patterns for manual input

### 📊 **Mandatory Audit Columns**
- **Foundation Layer**: Automatically adds 3 mandatory audit columns
- **Information Layer**: Supports TYPE 1 (9 columns) and TYPE 2 (12 columns) tables
- **Smart Mapping**: Pre-maps foundation audit columns to information layer

### 📈 **Professional Reports**
- **Excel Generation**: Separate files for Foundation and Information layers
- **Color-Coded Sections**: Visual distinction between Source, Transformation, and Target
- **Multiple Worksheets**: One sheet per table with detailed mappings

### 🎯 **User-Friendly Interface**
- **Tab Navigation**: Clean, intuitive interface with 4 main sections
- **Project Management**: Track project details for consistent file naming
- **Real-time Validation**: Immediate feedback on parsing results

## 🏛️ Architecture Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│     DL2     │───▶│ Foundation  │───▶│ Information │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                                      │
       │                                      │
Input DDL Scripts                     Input DBT Scripts

```

### **Supported Layer Transitions:**
1. **DL2 → Foundation**: Raw data lake to structured foundation layer
2. **Foundation → Information**: Foundation layer to business-ready information layer

## 🚀 Installation

### **Prerequisites**
- Python 3.7 or higher
- pip package manager

### **Step 1: Clone or Download**
```bash
# Clone the repository (if using git)
git clone <repository-url>
cd ddlc-manager

# Or download and extract the files to a directory
```

### **Step 2: Install Dependencies**
```bash
# Install required packages
pip install -r requirements.txt
```

### **Step 3: Run the Application**
```bash
# Start the Streamlit app
streamlit run ddlc_manager.py
```

### **Step 4: Access the Application**
- Open your browser and navigate to: `http://localhost:8501`
- The DDLC Manager interface will load automatically

## 📖 Setup & Usage

### **1. Project Setup**

#### **Navigate to Project Setup Tab**
1. Click on the **📋 Project Setup** tab
2. Fill in the required project information:
   - **Project Name**: Your project identifier (e.g., "PaymentSystem")
   - **Version**: Project version (e.g., "v1.0", "v2.1")
   - **Author**: Your name or team name

#### **Save Project Information**
3. Click **"Save Project Information"**
4. Verify the preview of how your Excel files will be named

**Example Output:**
```
Excel files will be named: PaymentSystem_v1.0_Foundation_Layer_DDLC.xlsx
```

---

### **2. DL2 → Foundation Mapping**

#### **Navigate to DL2 → Foundation Tab**
1. Click on the **🔄 DL2 → Foundation** tab

#### **Configure Source and Target Details**
2. **Source (DL2) Details:**
   - **Source Database**: `PROD_DL2_CHIEF_FINANCIAL_OFFICE_RQ` (default)
   - **Source Schema**: `ENTERPRISE` (default)
   - **Source Table Name**: Enter your DL2 table name

3. **Target (Foundation) Details:**
   - **Foundation Database**: `PCFOPAYMENTSDBI` (default)
   - **Foundation Schema**: `APP_CFOPYMT5` (default)
   - **Foundation Table Name**: Enter your Foundation table name

#### **Paste DDL Script**
4. **Foundation Table DDL Script:**
   ```sql
   create or replace TRANSIENT TABLE PCFOPAYMENTSDBI.APP_CFOPYMT5.APP_AUTOMATIC_PAYMENT_PLAN (
       KAFKA_HEADERS VARCHAR(16777216),
       KAFKA_META VARCHAR(16777216),
       ACCOUNT_ID VARCHAR(36),
       PAYMENT_AMOUNT NUMBER(15,2),
       STATUS_CODE VARCHAR(10),
       CREATED_DATE TIMESTAMP_NTZ(9)
   );
   ```

#### **Generate Mappings**
5. Click **"🚀 Parse DDL and Generate Mappings"**
6. The app will:
   - Extract all columns from the DDL script
   - Add 3 mandatory Foundation audit columns
   - Set default transformation logic to "Straight Move"
   - Mark audit columns as "ETL-generated"

#### **Review Results**
7. Check the **"All DL2 → Foundation Tables Overview"** section
8. Verify all columns are correctly parsed
9. Note that **source field names** are left empty for manual completion

---

### **3. Foundation → Information Mapping**

#### **Navigate to Foundation → Information Tab**
1. Click on the **🔄 Foundation → Information** tab

#### **Configure Source and Target Details**
2. **Source (Foundation) Details:**
   - **Source Database**: `PCFOPAYMENTSDBI` (default)
   - **Source Schema**: `APP_CFOPYMT5` (default)
   - **Source Table Name**: Enter your Foundation table name

3. **Target (Information) Details:**
   - **Information Database**: `PCFOINFOMDBI` (default)
   - **Information Schema**: `APP_CFOPYMT5` (default)
   - **Information Table Name**: Enter your Information table name

#### **Select Table Type**
4. **Information Layer Configuration:**
   - Choose **TYPE 1** or **TYPE 2** from the dropdown
   - **TYPE 1**: Standard audit columns (9 mandatory)
   - **TYPE 2**: Includes SCD support (12 mandatory)

#### **Paste DBT Script**
5. **DBT Transformation Logic:**
   ```sql
   {{ handle_empty_or_null_value(chk_type='VARCHAR', length=36, first_val='ACCOUNT_ID') }} AS ACCT_ID,
   {{ handle_empty_or_null_value(chk_type='NUMBER', length=15, precision=2, first_val='PAYMENT_AMOUNT') }} AS PMT_AMT,
   {{ handle_empty_or_null_value(chk_type='VARCHAR', length=10, first_val='STATUS_CODE') }} AS STAT_CD,
   {{ handle_empty_or_null_value(chk_type='TIMESTAMP', first_val='CREATED_DATE') }} AS CREA_DT
   ```

#### **Generate Mappings**
6. Click **"🚀 Parse DBT and Generate Mappings"**
7. The app will:
   - Parse `handle_empty_or_null_value` functions
   - Extract source field names from `first_val` parameters
   - Generate detailed transformation descriptions
   - Add mandatory audit columns based on TYPE 1/2 selection
   - Mark unrecognized patterns as "UNKNOWN"

#### **Review Results**
8. Check the parsing breakdown showing business vs audit columns
9. Review the **"All Foundation → Information Tables Overview"** section
10. Verify transformation logic accuracy

---

### **4. Generate Reports**

#### **Navigate to Generate Reports Tab**
1. Click on the **📊 Generate Reports** tab

#### **Verify Project Information**
2. Confirm your project details are displayed correctly
3. If missing, return to Project Setup tab to configure

#### **Generate Excel Files**
4. **Foundation Layer Reports:**
   - Click **"📋 Generate Foundation Layer Excel"**
   - Download the generated Excel file
   - Filename format: `{ProjectName}_{Version}_Foundation_Layer_DDLC_{timestamp}.xlsx`

5. **Information Layer Reports:**
   - Click **"📋 Generate Information Layer Excel"**
   - Download the generated Excel file
   - Filename format: `{ProjectName}_{Version}_Information_Layer_DDLC_{timestamp}.xlsx`

#### **Review Summary Statistics**
6. Check the summary metrics:
   - Total mappings per layer
   - Number of tables processed
   - TYPE 1 vs TYPE 2 breakdown (for Information layer)

## 🎯 Supported Patterns

### **DDL Script Patterns**
```sql
-- Supported column definitions
COLUMN_NAME VARCHAR(16777216),
FIELD_ID NUMBER(19,0),
TIMESTAMP_FIELD TIMESTAMP_LTZ(9),
DATE_FIELD DATE,
BOOLEAN_FLAG BOOLEAN
```

### **DBT Transformation Patterns**

#### **✅ Fully Supported: `handle_empty_or_null_value`**
```sql
-- VARCHAR transformations
{{ handle_empty_or_null_value(chk_type='VARCHAR', length=150, first_val='ACCOUNT_HOLDER_FULL_NM') }} AS ACCT_HOLD_FULL_NM

-- NUMBER transformations (precision = 0)
{{ handle_empty_or_null_value(chk_type='NUMBER', is_string=true, length=3, precision=0, first_val='RETRY_ATTEMPT_NR') }} AS RETRY_ATMPT_CNT

-- NUMBER transformations (precision > 0)
{{ handle_empty_or_null_value(chk_type='NUMBER', length=17, precision=3, first_val='TOTAL_ATTEMPT_NR') }} AS TOT_ATMPT_CNT

-- TIMESTAMP transformations
{{ handle_empty_or_null_value(chk_type='TIMESTAMP', default_val='1800-01-02 00:00:00.000000', format='YYYY-MM-DD HH:MI:SS.FF6', first_val='AUTH_START_GMTS') }} AS AUTH_START_TS

-- DATE transformations
{{ handle_empty_or_null_value(chk_type='DATE', empty_val='00000000', default_val='1800-01-02', format='YYYY-MM-DD', first_val='CARD_EXPIRATION_DT') }} AS CARD_EXP_DT
```

#### **✅ Supported: Direct Mapping**
```sql
-- Simple field aliases
ACCOUNT_ID AS ACCT_ID,
CUSTOMER_NAME AS CUST_NM
```

#### **❓ Marked as UNKNOWN: Complex Patterns**
```sql
-- Custom functions (marked for manual input)
{{ custom_transformation(param='value') }} AS CUSTOM_FIELD,

-- CASE statements (marked for manual input)
CASE WHEN condition THEN value ELSE other_value END AS COMPLEX_FIELD,

-- Complex expressions (marked for manual input)
CONCAT(field1, '_', field2) AS COMBINED_FIELD
```

### **Transformation Logic Interpretation**

| Data Type | Precision | NULL Handling | Example |
|-----------|-----------|---------------|---------|
| VARCHAR | N/A | Replace with '!' | `Transform ACCOUNT_HOLDER_FULL_NM to VARCHAR(150); Replace NULL values with '!'` |
| NUMBER | 0 | Replace with '-1' | `Transform RETRY_ATTEMPT_NR to NUMBER(3,0); Replace NULL values with '-1'` |
| NUMBER | > 0 | Remain NULL | `Transform TOTAL_ATTEMPT_NR to NUMBER(17,3); NULL values remain NULL (precision > 0)` |
| TIMESTAMP | N/A | Use default_val | `Transform AUTH_START_GMTS to TIMESTAMP; Set default value to '1800-01-02 00:00:00.000000' if empty` |
| DATE | N/A | Use default_val | `Transform CARD_EXPIRATION_DT to DATE; Set default value to '1800-01-02' if empty` |

## 🔧 Mandatory Audit Columns

### **Foundation Layer (3 columns)**
```sql
LOAD_TS TIMESTAMP_LTZ(9),      -- ETL load timestamp
LOAD_DT VARCHAR(10),           -- ETL load date
ETL_CREA_NR NUMBER(19,0)       -- ETL creation number
```

### **Information Layer TYPE 1 (9 columns)**
```sql
CREA_PRTY_ID VARCHAR(36) NOT NULL,        -- Creation party ID
CREA_TS TIMESTAMP_LTZ(6) NOT NULL,        -- Creation timestamp
UPDT_PRTY_ID VARCHAR(36),                 -- Update party ID
UPDT_TS TIMESTAMP_LTZ(6),                 -- Update timestamp
ETL_CREA_TS TIMESTAMP_LTZ(6) NOT NULL,    -- ETL creation timestamp
ETL_CREA_NR NUMBER(19,0) NOT NULL,        -- Maps to Foundation ETL_CREA_NR
ETL_UPDT_TS TIMESTAMP_LTZ(6),             -- ETL update timestamp
ETL_UPDT_NR NUMBER(19,0),                 -- ETL update number
FNDN_LOAD_TS TIMESTAMP_LTZ(6) NOT NULL    -- Maps to Foundation LOAD_TS
```

### **Information Layer TYPE 2 (12 columns)**
```sql
-- TYPE 2 SCD-specific columns
CURR_REC_IND VARCHAR(1) NOT NULL,         -- Current record indicator
SRC_SYS_REC_EFF_TS TIMESTAMP_LTZ(6) NOT NULL,  -- Record effective timestamp
SRC_SYS_REC_EXP_TS TIMESTAMP_LTZ(6) NOT NULL,  -- Record expiration timestamp

-- Plus all 9 TYPE 1 audit columns listed above
```

### **Audit Column Mappings**
| Source Layer | Source Column | Target Layer | Target Column | Purpose |
|--------------|---------------|--------------|---------------|---------|
| Foundation | LOAD_TS | Information | FNDN_LOAD_TS | Foundation load timestamp reference |
| Foundation | ETL_CREA_NR | Information | ETL_CREA_NR | ETL creation number reference |
| N/A | N/A | Foundation | LOAD_TS, LOAD_DT, ETL_CREA_NR | ETL-generated |
| N/A | N/A | Information | All other audit columns | ETL-generated |

## 📊 Excel Report Structure

### **Foundation Layer Excel**
```
📁 {ProjectName}_{Version}_Foundation_Layer_DDLC_{timestamp}.xlsx
   📄 Sheet per Foundation table
      📋 Table: {TableName}
         🟢 SOURCE (DL2)     🔵 TRANSFORMATION     🟣 TARGET (Foundation)
         Database            Logic                 Database
         Schema              Description           Schema  
         Table                                     Table
         Field                                     Column
```

### **Information Layer Excel**
```
📁 {ProjectName}_{Version}_Information_Layer_DDLC_{timestamp}.xlsx
   📄 Sheet per Information table
      📋 Table: {TableName} (TYPE 1/2)
         🟢 SOURCE (Foundation)  🔵 TRANSFORMATION     🟣 TARGET (Information)
         Database                Logic                 Database
         Schema                  Description           Schema
         Table                                         Table
         Field                                         Column
```

### **Color Coding**
- 🟢 **Green**: Source layer information
- 🔵 **Blue**: Transformation logic and rules
- 🟣 **Purple**: Target layer information
- **Headers**: Bold with colored backgrounds for easy identification

## 🔧 Troubleshooting

### **Common Issues**

#### **1. DDL Parsing Errors**
**Problem**: "Could not parse any columns from the DDL script"
**Solutions**:
- Ensure DDL script includes column definitions within parentheses
- Check for proper column syntax: `COLUMN_NAME DATA_TYPE(size)`
- Remove any constraint definitions (PRIMARY KEY, FOREIGN KEY, etc.)
- Verify the script is a valid CREATE TABLE statement

#### **2. DBT Parsing Issues**
**Problem**: "Could not parse any field mappings from the DBT script"
**Solutions**:
- Ensure each line ends with `AS target_field_name`
- Check that `handle_empty_or_null_value` functions are properly formatted
- Verify `first_val='FIELD_NAME'` parameters are correctly quoted
- Remove any incomplete or commented lines

#### **3. UNKNOWN Fields**
**Problem**: Too many fields marked as UNKNOWN
**Solutions**:
- Review DBT script formatting
- Ensure `handle_empty_or_null_value` functions are complete
- Check for typos in function names
- Consider manually updating UNKNOWN fields after import

#### **4. Missing Project Information**
**Problem**: "Files will use default naming"
**Solutions**:
- Go to Project Setup tab
- Fill in Project Name, Version, and Author
- Click "Save Project Information"
- Return to Generate Reports tab

#### **5. Excel Generation Fails**
**Problem**: Download buttons don't appear or fail
**Solutions**:
- Ensure you have mappings created
- Check that tables have been processed successfully
- Verify project information is saved
- Try refreshing the page and regenerating

### **Performance Tips**

1. **Large DDL Scripts**: Break very large scripts into smaller chunks
2. **Complex DBT Logic**: Use UNKNOWN marking for complex transformations, then manually update
3. **Multiple Tables**: Process one table at a time for better control
4. **Browser Memory**: Refresh the page if working with many large tables

### **Data Validation**

1. **Always review parsed results** before generating Excel files
2. **Verify audit column mappings** are correct
3. **Check transformation logic** for business rule accuracy
4. **Validate source field mappings** for UNKNOWN entries

