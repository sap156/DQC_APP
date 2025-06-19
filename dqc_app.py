import streamlit as st
import pandas as pd
import csv
import io
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Data Quality Control Rules Manager",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'rows' not in st.session_state:
    st.session_state.rows = []

# Default values and field definitions
DEFAULT_VALUES = {
    "DATA_QC_ID": "23",
    "RULE_FREQ_CD": "DAILY",
    "RULE_SRC_ATTR_NM": "NA",
    "RULE_TRGT_ATTR_NM": "NA",
    "RULE_CDE_IND": "N",
    "RULE_EXP_DT": "9999-12-31",
    "ASSET_ID": "9999"
}

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

FIELDS = {
    "DATA_QC_ID": DEFAULT_VALUES["DATA_QC_ID"],
    "APPL_CD": "EMM_",
    "RULE_NM": "Enter a rule name (e.g. TABLE_NM_DL2_CNT_CHK)",
    "RULE_DSC_TXT": "Description of the rule",
    "RULE_FREQ_CD": DEFAULT_VALUES["RULE_FREQ_CD"],
    "RULE_VALID_CTGY_NM": ["POST", "PRE"],
    "RULE_VALID_METH_CD": ["CNT_CHK", "SUM_CHK", "DIFF_CNT_CHK", "DIFF_SUM_CHK", "DUP_CHK", "OVERLAP_CHK"],
    "RULE_ABORT_IND": ["N", "Y"],
    "RULE_SRC_DB_NM": ["DL2_CHIEF_FINANCIAL_OFFICE_RQ", "CFOPAYMENTSTG", "IPENTSTRIPEDB"],
    "RULE_SRC_SCHM_NM": ["ENTERPRISE", "APP_CFOPYMTS", "STRIPE", "PAYMENTS"],
    "RULE_SRC_OBJ_ID_TXT": "SOURCE_TABLE",
    "RULE_SRC_ATTR_NM": DEFAULT_VALUES["RULE_SRC_ATTR_NM"],
    "RULE_TRGT_DB_NM": ["CFOPAYMENTSDB", "CFOINFODMDB"],
    "RULE_TRGT_SCHM_NM": "APP_CFOPYMTS",
    "RULE_TRGT_OBJ_ID_TXT": "TARGET_TABLE",
    "RULE_TRGT_ATTR_NM": DEFAULT_VALUES["RULE_TRGT_ATTR_NM"],
    "RULE_ACPT_VARY_PCT": "",
    "RULE_MIN_THRESH_VALUE_TXT": "",
    "RULE_MAX_THRESH_VALUE_TXT": "",
    "RULE_TRGT_DATA_LAYER_NM": ["DL2", "DL3", "OnPrem_HOP1", "OnPrem_HOP2", "OnPrem_HOP3", "OnPrem"],
    "RULE_CDE_IND": DEFAULT_VALUES["RULE_CDE_IND"],
    "RULE_LOGIC_TXT": "Enter rule SQL statement here",
    "RULE_EFF_DT": datetime.today().strftime("%Y-%m-%d"),
    "RULE_EXP_DT": DEFAULT_VALUES["RULE_EXP_DT"],
    "RULE_ACTV_IND": ["Y", "N"],
    "RULE_RMRK_TXT": "",
    "CREA_PRTY_ID": "PL6P223",
    "CREA_TS": get_current_timestamp(),
    "UPDT_PRTY_ID": "",
    "UPDT_TS": "",
    "ETL_CREA_NR": "",
    "ETL_CREA_TS": "",
    "ETL_UPDT_NR": "",
    "ETL_UPDT_TS": "",
    "ASSET_ID": DEFAULT_VALUES["ASSET_ID"],
    "ASSET_NM": "",
    "RULE_SEQ_NR": [str(i) for i in range(1, 21)]
}

# CSS for styling and instant uppercase conversion
st.markdown("""
<style>
    /* Instant uppercase conversion for text inputs */
    .uppercase-input input {
        text-transform: uppercase !important;
    }
    .uppercase-input textarea {
        text-transform: uppercase !important;
    }
    
    /* Error message styling */
    .validation-error {
        background-color: #ffebee;
        border: 1px solid #f44336;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Section dividers */
    .section-divider {
        border-top: 3px solid #ff4b4b;
        margin: 2rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Validation functions
def validate_rule_abort_ind(row):
    errors = []
    rule_valid_meth_cd = row.get("RULE_VALID_METH_CD", "")
    rule_abort_ind = row.get("RULE_ABORT_IND", "")
    
    if rule_valid_meth_cd in ["CNT_CHK", "SUM_CHK"] and rule_abort_ind == "Y":
        errors.append("RULE_ABORT_IND must be 'N' for CNT_CHK or SUM_CHK.")
    
    if rule_valid_meth_cd not in ["CNT_CHK", "SUM_CHK"] and rule_abort_ind == "N":
        errors.append("RULE_ABORT_IND must be 'Y' for RULE_VALID_METH_CD values other than CNT_CHK or SUM_CHK.")
    
    return errors

def validate_rule_trgt_attr_nm(row):
    errors = []
    meth = row.get("RULE_VALID_METH_CD", "")
    attr = row.get("RULE_TRGT_ATTR_NM", "")
    
    if meth in ["SUM_CHK", "DIFF_SUM_CHK"] and (not attr or attr.strip() == "" or attr == "NA"):
        errors.append("RULE_TRGT_ATTR_NM cannot be blank or 'NA' when RULE_VALID_METH_CD is SUM_CHK or DIFF_SUM_CHK. Please specify the attribute/column name to sum.")
    
    return errors

def validate_appl_cd(row):
    errors = []
    appl_cd = row.get("APPL_CD", "").strip()
    
    if not appl_cd or appl_cd == "EMM_" or appl_cd.endswith("_"):
        errors.append("APPL_CD must be completed. Please provide a full application code (e.g., EMM_PAYMENTS, EMM_FINANCE, etc.).")
    
    if appl_cd and len(appl_cd) < 4:
        errors.append("APPL_CD appears to be too short. Please provide a meaningful application code.")
    
    return errors

def validate_rule_sequence_number(row, all_rows, is_new_row=True):
    errors = []
    allowed_duplicate_count = 0 if is_new_row else 1
    
    sequence_number_duplicates = [
        r for r in all_rows 
        if (r.get("RULE_TRGT_OBJ_ID_TXT") == row.get("RULE_TRGT_OBJ_ID_TXT") and
            r.get("RULE_VALID_CTGY_NM") == row.get("RULE_VALID_CTGY_NM") and
            r.get("RULE_SEQ_NR") == row.get("RULE_SEQ_NR"))
    ]
    
    if len(sequence_number_duplicates) > allowed_duplicate_count:
        errors.append("Duplicate RULE_TRGT_OBJ_ID_TXT with same RULE_VALID_CTGY_NM and RULE_SEQ_NR.")
    
    return errors

def validate_rule_name_is_unique(row, all_rows, is_new_row=True):
    errors = []
    allowed_duplicate_count = 0 if is_new_row else 1
    
    rule_name_duplicates = [r for r in all_rows if r.get("RULE_NM") == row.get("RULE_NM")]
    
    if len(rule_name_duplicates) > allowed_duplicate_count:
        errors.append("RULE_NM already exists.")
    
    return errors

def validate_rule_name_matches_standards(row):
    errors = []
    rule_name_patterns = [
        r"^[A-Z0-9_]+OP_HOP3_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+OP_HOP2_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+OP_HOP1_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+DL2_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+FND_DL3_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+STG_DL3_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+INFO_DL3_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+OP_HOP3_HOP2_DIFF_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+OP_HOP2_HOP1_DIFF_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+OP_HOP1_DL2_DIFF_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+DL2_FND_DIFF_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+STG_INFO_DIFF_(CNT|SUM)_CHK$",
        r"^[A-Z0-9_]+INFO_DL3_DUP_CHK$",
        r"^[A-Z0-9_]+INFO_DL3_OVERLAP_CHK$"
    ]
    
    rule_name = row.get("RULE_NM", "")
    if not any(re.match(pattern, rule_name) for pattern in rule_name_patterns):
        errors.append("RULE_NM does not match any of the specified patterns")
    
    return errors

def validate_single_row(row, all_rows, is_new_row=True):
    errors = []
    errors.extend(validate_appl_cd(row))
    errors.extend(validate_rule_abort_ind(row))
    errors.extend(validate_rule_trgt_attr_nm(row))
    errors.extend(validate_rule_sequence_number(row, all_rows, is_new_row))
    errors.extend(validate_rule_name_is_unique(row, all_rows, is_new_row))
    errors.extend(validate_rule_name_matches_standards(row))
    return errors

def generate_rule_name(rule_trgt_obj_id_txt, rule_valid_meth_cd, rule_trgt_db_nm, rule_trgt_data_layer_nm):
    """Generate rule name based on input parameters - matches original JavaScript logic exactly"""
    if not all([rule_trgt_obj_id_txt, rule_valid_meth_cd, rule_trgt_db_nm, rule_trgt_data_layer_nm]):
        return "Enter a rule name (e.g. TABLE_NM_DL2_CNT_CHK)"
    
    rule_target_component = ""
    
    if rule_trgt_db_nm == "CFOPAYMENTSDB":
        if rule_valid_meth_cd in ["CNT_CHK", "SUM_CHK"]:
            if rule_trgt_data_layer_nm == "OnPrem_HOP3":
                rule_target_component = "OP_HOP3"
            elif rule_trgt_data_layer_nm == "OnPrem_HOP2":
                rule_target_component = "OP_HOP2"
            elif rule_trgt_data_layer_nm == "OnPrem_HOP1":
                rule_target_component = "OP_HOP1"
            elif rule_trgt_data_layer_nm == "DL2":
                rule_target_component = "DL2"
            elif rule_trgt_data_layer_nm == "DL3":
                rule_target_component = "FND_DL3"
            else:
                rule_target_component = "UNKNOWN"
        elif rule_valid_meth_cd in ["DIFF_CNT_CHK", "DIFF_SUM_CHK"]:
            if rule_trgt_data_layer_nm == "OnPrem":
                rule_target_component = "OP_(HOP3_HOP2|HOP2_HOP1)"
            elif rule_trgt_data_layer_nm == "DL2":
                rule_target_component = "OP_HOP1_DL2"
            elif rule_trgt_data_layer_nm == "DL3":
                rule_target_component = "DL2_FND"
            else:
                rule_target_component = "UNKNOWN"
        elif rule_valid_meth_cd in ["DUP_CHK", "OVERLAP_CHK"]:
            if rule_trgt_data_layer_nm == "DL3":
                rule_target_component = "FND_DL3"
            else:
                rule_target_component = "UNKNOWN"
        else:
            rule_target_component = "UNKNOWN"
    elif rule_trgt_db_nm == "CFOINFODMDB":
        if rule_valid_meth_cd in ["CNT_CHK", "SUM_CHK"]:
            rule_target_component = "(STG|INFO)_DL3"
        elif rule_valid_meth_cd in ["DIFF_CNT_CHK", "DIFF_SUM_CHK"]:
            rule_target_component = "STG_INFO"
        elif rule_valid_meth_cd in ["DUP_CHK", "OVERLAP_CHK"]:
            rule_target_component = "INFO_DL3"
        else:
            rule_target_component = "UNKNOWN"
    else:
        rule_target_component = "UNKNOWN"
    
    return f"{rule_trgt_obj_id_txt}_{rule_target_component}_{rule_valid_meth_cd}"

def generate_rule_description(rule_nm, rule_valid_meth_cd, rule_trgt_attr_nm, rule_trgt_obj_id_txt):
    """Generate a descriptive text for the rule based on its components"""
    if not rule_nm or rule_nm == "Enter a rule name (e.g. TABLE_NM_DL2_CNT_CHK)":
        return "Rule description will be auto-generated based on rule name"
    
    # Determine the check type with attribute for SUM checks
    if "CNT_CHK" in rule_valid_meth_cd:
        if "DIFF_CNT_CHK" in rule_valid_meth_cd:
            check_type = "difference count check"
        else:
            check_type = "count check"
    elif "SUM_CHK" in rule_valid_meth_cd:
        if "DIFF_SUM_CHK" in rule_valid_meth_cd:
            check_type = f"difference sum check on {rule_trgt_attr_nm}" if rule_trgt_attr_nm and rule_trgt_attr_nm != "NA" else "difference sum check"
        else:
            check_type = f"sum check on {rule_trgt_attr_nm}" if rule_trgt_attr_nm and rule_trgt_attr_nm != "NA" else "sum check"
    elif "DUP_CHK" in rule_valid_meth_cd:
        check_type = "duplicate check"
    elif "OVERLAP_CHK" in rule_valid_meth_cd:
        check_type = "overlap check"
    else:
        check_type = "data quality check"
    
    # Parse the rule name to determine the description pattern
    description = ""
    
    # Single layer checks
    if "_OP_HOP3_CNT_CHK" in rule_nm or "_OP_HOP3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} for OnPrem Source Records (HOP3) on table {rule_trgt_obj_id_txt}."
    elif "_OP_HOP2_CNT_CHK" in rule_nm or "_OP_HOP2_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} for OnPrem DS Records (HOP2) on table {rule_trgt_obj_id_txt}."
    elif "_OP_HOP1_CNT_CHK" in rule_nm or "_OP_HOP1_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} for OnPrem CSV Records (HOP1) on table {rule_trgt_obj_id_txt}."
    elif "_DL2_CNT_CHK" in rule_nm or "_DL2_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} for DL2 layer on table {rule_trgt_obj_id_txt}."
    elif "_FND_DL3_CNT_CHK" in rule_nm or "_FND_DL3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} for foundation DL3 table on table {rule_trgt_obj_id_txt}."
    elif "_STG_DL3_CNT_CHK" in rule_nm or "_STG_DL3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} for staging DL3 table on table {rule_trgt_obj_id_txt}."
    elif "_INFO_DL3_CNT_CHK" in rule_nm or "_INFO_DL3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} for information DL3 table on table {rule_trgt_obj_id_txt}."
    
    # Difference checks between layers
    elif "_OP_HOP3_HOP2_DIFF_CNT_CHK" in rule_nm or "_OP_HOP3_HOP2_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between OnPrem Source Records (HOP3) and OnPrem DS Records (HOP2) on table {rule_trgt_obj_id_txt}."
    elif "_OP_HOP2_HOP1_DIFF_CNT_CHK" in rule_nm or "_OP_HOP2_HOP1_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between OnPrem DS Records (HOP2) and OnPrem CSV Records (HOP1) on table {rule_trgt_obj_id_txt}."
    elif "_OP_HOP1_DL2_DIFF_CNT_CHK" in rule_nm or "_OP_HOP1_DL2_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between OnPrem CSV Records (HOP1) and DL2 layer on table {rule_trgt_obj_id_txt}."
    elif "_DL2_FND_DIFF_CNT_CHK" in rule_nm or "_DL2_FND_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between DL2 layer and foundation DL3 table on table {rule_trgt_obj_id_txt}."
    elif "_STG_INFO_DIFF_CNT_CHK" in rule_nm or "_STG_INFO_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between staging DL3 table and information DL3 table on table {rule_trgt_obj_id_txt}."
    
    # Duplicate and overlap checks
    elif "_INFO_DL3_DUP_CHK" in rule_nm:
        description = f"Performs duplicate check for information DL3 table on table {rule_trgt_obj_id_txt}."
    elif "_INFO_DL3_OVERLAP_CHK" in rule_nm:
        description = f"Performs overlap check for information DL3 table on table {rule_trgt_obj_id_txt}."
    
    # Fallback for unrecognized patterns
    else:
        if rule_trgt_obj_id_txt and rule_trgt_obj_id_txt != "TARGET_TABLE":
            description = f"Performs {check_type} on table {rule_trgt_obj_id_txt}."
        else:
            description = f"Performs {check_type}."
    
    # Capitalize first letter if not already
    if description and not description[0].isupper():
        description = description[0].upper() + description[1:]
    
    return description

# Helper functions for auto-updates
def update_all_auto_fields():
    """Update all auto-populated fields when key fields change"""
    # Update RULE_ABORT_IND
    abort_ind_values = ["DIFF_CNT_CHK", "DIFF_SUM_CHK", "DUP_CHK", "OVERLAP_CHK"]
    st.session_state.form_rule_abort_ind = "Y" if st.session_state.form_rule_valid_meth_cd in abort_ind_values else "N"
    
    # Update RULE_TRGT_ATTR_NM
    if st.session_state.form_rule_valid_meth_cd in ["SUM_CHK", "DIFF_SUM_CHK"]:
        if st.session_state.form_rule_trgt_attr_nm == "NA":
            st.session_state.form_rule_trgt_attr_nm = ""
    else:
        st.session_state.form_rule_trgt_attr_nm = "NA"
    
    # Update RULE_NM
    if (st.session_state.form_rule_trgt_obj_id_txt and 
        st.session_state.form_rule_valid_meth_cd and 
        st.session_state.form_rule_trgt_db_nm and 
        st.session_state.form_rule_trgt_data_layer_nm):
        
        st.session_state.form_rule_nm = generate_rule_name(
            st.session_state.form_rule_trgt_obj_id_txt,
            st.session_state.form_rule_valid_meth_cd, 
            st.session_state.form_rule_trgt_db_nm,
            st.session_state.form_rule_trgt_data_layer_nm
        )
    else:
        st.session_state.form_rule_nm = "Enter a rule name (e.g. TABLE_NM_DL2_CNT_CHK)"
    
    # Update RULE_DSC_TXT
    st.session_state.form_rule_dsc_txt = generate_rule_description(
        st.session_state.form_rule_nm,
        st.session_state.form_rule_valid_meth_cd,
        st.session_state.form_rule_trgt_attr_nm,
        st.session_state.form_rule_trgt_obj_id_txt
    )

def update_rule_name_only():
    """Update only rule name when target table changes"""
    if (st.session_state.form_rule_trgt_obj_id_txt and 
        st.session_state.form_rule_valid_meth_cd and 
        st.session_state.form_rule_trgt_db_nm and 
        st.session_state.form_rule_trgt_data_layer_nm):
        
        st.session_state.form_rule_nm = generate_rule_name(
            st.session_state.form_rule_trgt_obj_id_txt,
            st.session_state.form_rule_valid_meth_cd, 
            st.session_state.form_rule_trgt_db_nm,
            st.session_state.form_rule_trgt_data_layer_nm
        )
    else:
        st.session_state.form_rule_nm = "Enter a rule name (e.g. TABLE_NM_DL2_CNT_CHK)"
    
    # Update RULE_DSC_TXT
    st.session_state.form_rule_dsc_txt = generate_rule_description(
        st.session_state.form_rule_nm,
        st.session_state.form_rule_valid_meth_cd,
        st.session_state.form_rule_trgt_attr_nm,
        st.session_state.form_rule_trgt_obj_id_txt
    )

def update_database_based_on_layer():
    """Update RULE_TRGT_DB_NM when data layer contains HOP values"""
    data_layer = st.session_state.form_rule_trgt_data_layer_nm
    if any(hop in data_layer for hop in ["HOP1", "HOP2", "HOP3", "OnPrem"]):
        st.session_state.form_rule_trgt_db_nm = "CFOPAYMENTSDB"
    
    # Then update rule name and description
    update_rule_name_only()

def update_description_only():
    """Update only rule description when attribute changes"""
    st.session_state.form_rule_dsc_txt = generate_rule_description(
        st.session_state.form_rule_nm,
        st.session_state.form_rule_valid_meth_cd,
        st.session_state.form_rule_trgt_attr_nm,
        st.session_state.form_rule_trgt_obj_id_txt
    )

# Sidebar with instructions
st.sidebar.title("DQC Rules Manager")
st.sidebar.markdown("**This application helps you manage Data Quality Control rules.**")

st.sidebar.markdown("### How to Use:")
st.sidebar.markdown("""
1. **Upload existing rules in CSV format**
   - Files must use tilde (~) delimiter
   - Limit 200MB per file

2. **Add new rules with validation**
   - Auto-populates rule names based on selections
   - Validates against business rules

3. **Edit or delete existing rules**
   - View all rules in table format
   - Individual rule management

4. **Export rules to CSV**
   - Download processed rules
   - Ready for system import
""")

# Main title
st.title("Data Quality Control Rules Manager")

# ============================================================================
# SECTION 1: UPLOAD EXISTING RULES
# ============================================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.header("📂 Upload Existing Rules")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv", help="Limit 200MB per file • CSV with tilde (~) delimiter")

if uploaded_file is not None:
    try:
        # Read CSV with tilde delimiter
        df = pd.read_csv(uploaded_file, delimiter='~')
        
        # Convert to list of dictionaries and ensure uppercase
        uploaded_rows = []
        for _, row in df.iterrows():
            rule_dict = {}
            for field in FIELDS.keys():
                value = str(row.get(field, "")) if pd.notna(row.get(field, "")) else ""
                # Convert text fields to uppercase
                if field in ["APPL_CD", "RULE_NM", "RULE_DSC_TXT", "RULE_SRC_OBJ_ID_TXT", 
                             "RULE_TRGT_SCHM_NM", "RULE_TRGT_OBJ_ID_TXT", "RULE_TRGT_ATTR_NM", "RULE_LOGIC_TXT"]:
                    value = value.upper()
                rule_dict[field] = value
            uploaded_rows.append(rule_dict)

        st.session_state.rows = uploaded_rows
        st.success(f"✅ Successfully uploaded {len(uploaded_rows)} records")

    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")

# ============================================================================
# SECTION 2: ADD NEW RULE
# ============================================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.header("➕ Add New Rule")

# Initialize session state for form fields if not exists
if 'form_appl_cd' not in st.session_state:
    st.session_state.form_appl_cd = "EMM_"
if 'form_rule_dsc_txt' not in st.session_state:
    st.session_state.form_rule_dsc_txt = "Rule description will be auto-generated based on rule name"
if 'form_rule_valid_ctgy_nm' not in st.session_state:
    st.session_state.form_rule_valid_ctgy_nm = FIELDS["RULE_VALID_CTGY_NM"][0]
if 'form_rule_valid_meth_cd' not in st.session_state:
    st.session_state.form_rule_valid_meth_cd = FIELDS["RULE_VALID_METH_CD"][0]
if 'form_rule_src_db_nm' not in st.session_state:
    st.session_state.form_rule_src_db_nm = FIELDS["RULE_SRC_DB_NM"][0]
if 'form_rule_src_schm_nm' not in st.session_state:
    st.session_state.form_rule_src_schm_nm = FIELDS["RULE_SRC_SCHM_NM"][0]
if 'form_rule_src_obj_id_txt' not in st.session_state:
    st.session_state.form_rule_src_obj_id_txt = "SOURCE_TABLE"
if 'form_rule_seq_nr' not in st.session_state:
    st.session_state.form_rule_seq_nr = FIELDS["RULE_SEQ_NR"][0]
if 'form_rule_trgt_db_nm' not in st.session_state:
    st.session_state.form_rule_trgt_db_nm = FIELDS["RULE_TRGT_DB_NM"][0]
if 'form_rule_trgt_schm_nm' not in st.session_state:
    st.session_state.form_rule_trgt_schm_nm = "APP_CFOPYMTS"
if 'form_rule_trgt_obj_id_txt' not in st.session_state:
    st.session_state.form_rule_trgt_obj_id_txt = "TARGET_TABLE"
if 'form_rule_trgt_data_layer_nm' not in st.session_state:
    st.session_state.form_rule_trgt_data_layer_nm = FIELDS["RULE_TRGT_DATA_LAYER_NM"][0]
if 'form_rule_actv_ind' not in st.session_state:
    st.session_state.form_rule_actv_ind = FIELDS["RULE_ACTV_IND"][0]
if 'form_rule_logic_txt' not in st.session_state:
    st.session_state.form_rule_logic_txt = "Enter rule SQL statement here"
if 'form_rule_abort_ind' not in st.session_state:
    st.session_state.form_rule_abort_ind = "N"
if 'form_rule_trgt_attr_nm' not in st.session_state:
    st.session_state.form_rule_trgt_attr_nm = "NA"

# Initialize rule name and auto-fields if not exists
if 'form_rule_nm' not in st.session_state:
    update_all_auto_fields()

# Auto-convert text inputs to uppercase immediately after user types
text_fields = ['form_appl_cd', 'form_rule_src_obj_id_txt', 
               'form_rule_trgt_schm_nm', 'form_rule_trgt_obj_id_txt', 
               'form_rule_nm', 'form_rule_trgt_attr_nm', 'form_rule_logic_txt']

for field in text_fields:
    if field in st.session_state and isinstance(st.session_state[field], str):
        if st.session_state[field] != st.session_state[field].upper():
            st.session_state[field] = st.session_state[field].upper()

# Form layout in columns
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_input("APPL_CD", key="form_appl_cd", 
                     help="Enter complete application code (e.g., EMM_PAYMENTS, EMM_FINANCE)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_area("RULE_DSC_TXT", key="form_rule_dsc_txt", height=80, disabled=True,
                    help="Auto-generated description based on rule configuration")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.selectbox("RULE_VALID_CTGY_NM", FIELDS["RULE_VALID_CTGY_NM"], key="form_rule_valid_ctgy_nm")
    
    # RULE_VALID_METH_CD - triggers all auto-updates
    st.selectbox("RULE_VALID_METH_CD", FIELDS["RULE_VALID_METH_CD"], 
                key="form_rule_valid_meth_cd", on_change=update_all_auto_fields)
    
    st.selectbox("RULE_SRC_DB_NM", FIELDS["RULE_SRC_DB_NM"], key="form_rule_src_db_nm")
    st.selectbox("RULE_SRC_SCHM_NM", FIELDS["RULE_SRC_SCHM_NM"], key="form_rule_src_schm_nm")
    
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_input("RULE_SRC_OBJ_ID_TXT", key="form_rule_src_obj_id_txt")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.selectbox("RULE_SEQ_NR", FIELDS["RULE_SEQ_NR"], key="form_rule_seq_nr")

with col2:
    # RULE_TRGT_DB_NM - triggers rule name update
    st.selectbox("RULE_TRGT_DB_NM", FIELDS["RULE_TRGT_DB_NM"], 
                key="form_rule_trgt_db_nm", on_change=update_rule_name_only)
    
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_input("RULE_TRGT_SCHM_NM", key="form_rule_trgt_schm_nm")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # RULE_TRGT_OBJ_ID_TXT - triggers rule name update
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_input("RULE_TRGT_OBJ_ID_TXT", key="form_rule_trgt_obj_id_txt", 
                     on_change=update_rule_name_only)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # RULE_TRGT_DATA_LAYER_NM - triggers database and rule name update
    st.selectbox("RULE_TRGT_DATA_LAYER_NM", FIELDS["RULE_TRGT_DATA_LAYER_NM"], 
                key="form_rule_trgt_data_layer_nm", on_change=update_database_based_on_layer)
    
    st.selectbox("RULE_ACTV_IND", FIELDS["RULE_ACTV_IND"], key="form_rule_actv_ind")
    
    # RULE_ABORT_IND - auto-populated and disabled
    st.text_input("RULE_ABORT_IND", value=st.session_state.form_rule_abort_ind, disabled=True, 
                 help="Auto-populated based on RULE_VALID_METH_CD")

# Rule name and attribute section
col_name, col_attr = st.columns([2, 1])

with col_name:
    # Display the auto-generated rule name (editable but auto-populated)
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_input("RULE_NM", key="form_rule_nm", on_change=update_description_only,
                     help="Rule name will be auto-populated based on selections above")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show generation info if rule contains special patterns
    if (st.session_state.form_rule_nm and 
        st.session_state.form_rule_nm != "Enter a rule name (e.g. TABLE_NM_DL2_CNT_CHK)"):
        if "(STG|INFO)" in st.session_state.form_rule_nm:
            st.warning("**Note:** Rule name contains **(STG|INFO)** - you must manually choose either **STG** or **INFO** in the rule name.")
        elif "(HOP3_HOP2|HOP2_HOP1)" in st.session_state.form_rule_nm:
            st.warning("**Note:** Rule name contains **(HOP3_HOP2|HOP2_HOP1)** - you must manually choose either **HOP3_HOP2** or **HOP2_HOP1** in the rule name.")

with col_attr:
    # RULE_TRGT_ATTR_NM - conditional editability based on method
    if st.session_state.form_rule_valid_meth_cd in ["SUM_CHK", "DIFF_SUM_CHK"]:
        # For SUM checks, field should be editable so user can specify the attribute to sum
        with st.container():
            st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
            st.text_input("RULE_TRGT_ATTR_NM", key="form_rule_trgt_attr_nm",
                         help="Specify the attribute/column name to sum", on_change=update_description_only)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # For other methods, auto-populate with "NA" and make it disabled
        st.text_input("RULE_TRGT_ATTR_NM", value="NA", 
                     key="form_rule_trgt_attr_nm_display", disabled=True,
                     help="Auto-populated as 'NA' for non-SUM methods")

# Rule logic
with st.container():
    st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
    st.text_area("RULE_LOGIC_TXT", key="form_rule_logic_txt", height=100)
    st.markdown('</div>', unsafe_allow_html=True)

# Action buttons section
col_add_btn, col_validate, col_download = st.columns(3)

with col_add_btn:
    # Add Rule button
    if st.button("➕ Add Rule", use_container_width=True, type="primary"):
        # Collect form data from session state
        form_data = {
            "DATA_QC_ID": DEFAULT_VALUES["DATA_QC_ID"],
            "APPL_CD": st.session_state.form_appl_cd,
            "RULE_NM": st.session_state.form_rule_nm,
            "RULE_DSC_TXT": st.session_state.form_rule_dsc_txt,
            "RULE_FREQ_CD": DEFAULT_VALUES["RULE_FREQ_CD"],
            "RULE_VALID_CTGY_NM": st.session_state.form_rule_valid_ctgy_nm,
            "RULE_VALID_METH_CD": st.session_state.form_rule_valid_meth_cd,
            "RULE_ABORT_IND": st.session_state.form_rule_abort_ind,
            "RULE_SRC_DB_NM": st.session_state.form_rule_src_db_nm,
            "RULE_SRC_SCHM_NM": st.session_state.form_rule_src_schm_nm,
            "RULE_SRC_OBJ_ID_TXT": st.session_state.form_rule_src_obj_id_txt,
            "RULE_SRC_ATTR_NM": DEFAULT_VALUES["RULE_SRC_ATTR_NM"],
            "RULE_TRGT_DB_NM": st.session_state.form_rule_trgt_db_nm,
            "RULE_TRGT_SCHM_NM": st.session_state.form_rule_trgt_schm_nm,
            "RULE_TRGT_OBJ_ID_TXT": st.session_state.form_rule_trgt_obj_id_txt,
            "RULE_TRGT_ATTR_NM": st.session_state.get("form_rule_trgt_attr_nm", st.session_state.form_rule_trgt_attr_nm) if st.session_state.form_rule_valid_meth_cd in ["SUM_CHK", "DIFF_SUM_CHK"] else "NA",
            "RULE_ACPT_VARY_PCT": "",
            "RULE_MIN_THRESH_VALUE_TXT": "",
            "RULE_MAX_THRESH_VALUE_TXT": "",
            "RULE_TRGT_DATA_LAYER_NM": st.session_state.form_rule_trgt_data_layer_nm,
            "RULE_CDE_IND": DEFAULT_VALUES["RULE_CDE_IND"],
            "RULE_LOGIC_TXT": st.session_state.form_rule_logic_txt,
            "RULE_EFF_DT": datetime.today().strftime("%Y-%m-%d"),
            "RULE_EXP_DT": DEFAULT_VALUES["RULE_EXP_DT"],
            "RULE_ACTV_IND": st.session_state.form_rule_actv_ind,
            "RULE_RMRK_TXT": "",
            "CREA_PRTY_ID": "PL6P223",
            "CREA_TS": get_current_timestamp(),
            "UPDT_PRTY_ID": "",
            "UPDT_TS": "",
            "ETL_CREA_NR": "",
            "ETL_CREA_TS": "",
            "ETL_UPDT_NR": "",
            "ETL_UPDT_TS": "",
            "ASSET_ID": DEFAULT_VALUES["ASSET_ID"],
            "ASSET_NM": st.session_state.form_appl_cd,
            "RULE_SEQ_NR": st.session_state.form_rule_seq_nr
        }

        # Validate the rule
        validation_errors = validate_single_row(form_data, st.session_state.rows, is_new_row=True)
        
        if validation_errors:
            # Store validation errors in session state for display
            st.session_state.validation_errors = validation_errors
        else:
            st.session_state.rows.append(form_data)
            st.success("✅ Rule added successfully!")
            # Clear any previous validation errors
            if 'validation_errors' in st.session_state:
                del st.session_state.validation_errors
            st.rerun()

with col_validate:
    if st.button("🔍 Validate All Rules", use_container_width=True):
        if not st.session_state.rows:
            st.warning("No rules to validate. Please upload or add rules first.")
        else:
            all_errors = []
            for i, row in enumerate(st.session_state.rows):
                errors = validate_single_row(row, st.session_state.rows, is_new_row=False)
                if errors:
                    all_errors.extend([f"Row {i+1}: {error}" for error in errors])
            
            if all_errors:
                # Store validation errors in session state for display
                st.session_state.all_validation_errors = all_errors
            else:
                st.success("✅ All rules are valid!")
                # Clear any previous validation errors
                if 'all_validation_errors' in st.session_state:
                    del st.session_state.all_validation_errors

with col_download:
    # Generate CSV download
    if st.session_state.rows:
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output, delimiter='~')
        
        # Write header
        writer.writerow(FIELDS.keys())
        
        # Write data
        for row in st.session_state.rows:
            writer.writerow([row.get(field, "") for field in FIELDS.keys()])
        
        csv_content = output.getvalue()
        
        # Generate filename
        appl_cd = st.session_state.rows[0].get("APPL_CD", "EMM").replace(" ", "_")
        filename = f"DATA_QC_RULE_INFO_{appl_cd}.csv"
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_content,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.button("📥 Download CSV", disabled=True, use_container_width=True, help="No rules available to download")

# Display validation errors in a prominent horizontal section
if 'validation_errors' in st.session_state:
    st.markdown('<div class="validation-error">', unsafe_allow_html=True)
    st.error("**❌ Validation Errors:**")
    for error in st.session_state.validation_errors:
        st.error(f"• {error}")
    st.markdown('</div>', unsafe_allow_html=True)

if 'all_validation_errors' in st.session_state:
    st.markdown('<div class="validation-error">', unsafe_allow_html=True)
    st.error("**❌ Validation Errors Found:**")
    for error in st.session_state.all_validation_errors:
        st.error(f"• {error}")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# SECTION 3: VIEW & EDIT RULES
# ============================================================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.header("📋 View & Edit Rules")

if not st.session_state.rows:
    st.info("🔍 No rules available. Please upload a CSV file or add new rules above.")
else:
    # Summary statistics
    total_rules = len(st.session_state.rows)
    active_rules = len([r for r in st.session_state.rows if r.get("RULE_ACTV_IND") == "Y"])
    
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("Total Rules", total_rules)
    with col_stats2:
        st.metric("Active Rules", active_rules)
    with col_stats3:
        st.metric("Inactive Rules", total_rules - active_rules)
    
    # Display rules summary table
    st.subheader("📊 Rules Overview")
    df = pd.DataFrame(st.session_state.rows)
    display_columns = ["APPL_CD", "RULE_NM", "RULE_VALID_METH_CD", "RULE_TRGT_OBJ_ID_TXT", "RULE_ACTV_IND"]
    available_columns = [col for col in display_columns if col in df.columns]
    
    if available_columns:
        st.dataframe(df[available_columns], use_container_width=True, height=300)
    else:
        st.dataframe(df, use_container_width=True, height=300)
    
    # Individual rule management with editing capability
    st.subheader("🔧 Individual Rule Management")
    for i, row in enumerate(st.session_state.rows):
        with st.expander(f"Rule {i+1}: {row.get('RULE_NM', 'Unnamed Rule')}", expanded=False):
            
            # Edit mode toggle
            edit_key = f"edit_mode_{i}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
            
            col_edit_toggle, col_actions = st.columns([4, 1])
            
            with col_edit_toggle:
                if st.button(f"✏️ {'Save Changes' if st.session_state[edit_key] else 'Edit Rule'}", key=f"edit_toggle_{i}"):
                    if st.session_state[edit_key]:
                        # Save mode - collect all edited values and update the row
                        updated_row = {}
                        for field in FIELDS.keys():
                            edit_field_key = f"edit_{field}_{i}"
                            if edit_field_key in st.session_state:
                                updated_row[field] = st.session_state[edit_field_key]
                            else:
                                updated_row[field] = row.get(field, "")
                        
                        # Validate the updated row
                        validation_errors = validate_single_row(updated_row, st.session_state.rows, is_new_row=False)
                        
                        if validation_errors:
                            st.error("**Validation Errors:**")
                            for error in validation_errors:
                                st.error(f"• {error}")
                        else:
                            st.session_state.rows[i] = updated_row
                            st.session_state[edit_key] = False
                            st.success("✅ Rule updated successfully!")
                            st.rerun()
                    else:
                        # Enter edit mode
                        st.session_state[edit_key] = True
                        st.rerun()
            
            with col_actions:
                if st.button(f"🗑️ Delete", key=f"delete_{i}", use_container_width=True):
                    st.session_state.rows.pop(i)
                    st.success("Rule deleted successfully!")
                    st.rerun()
            
            st.markdown("---")
            
            if st.session_state[edit_key]:
                # Edit mode - show editable fields
                st.markdown("**✏️ Editing Mode - Modify values below:**")
                
                # Core identification fields
                col_id1, col_id2, col_id3 = st.columns(3)
                with col_id1:
                    st.text_input("DATA_QC_ID", value=row.get('DATA_QC_ID', ''), key=f"edit_DATA_QC_ID_{i}")
                    st.text_input("APPL_CD", value=row.get('APPL_CD', ''), key=f"edit_APPL_CD_{i}")
                    st.text_input("RULE_NM", value=row.get('RULE_NM', ''), key=f"edit_RULE_NM_{i}")
                with col_id2:
                    st.text_input("RULE_FREQ_CD", value=row.get('RULE_FREQ_CD', ''), key=f"edit_RULE_FREQ_CD_{i}")
                    st.selectbox("RULE_VALID_CTGY_NM", FIELDS["RULE_VALID_CTGY_NM"], 
                               index=FIELDS["RULE_VALID_CTGY_NM"].index(row.get('RULE_VALID_CTGY_NM', FIELDS["RULE_VALID_CTGY_NM"][0])) if row.get('RULE_VALID_CTGY_NM') in FIELDS["RULE_VALID_CTGY_NM"] else 0,
                               key=f"edit_RULE_VALID_CTGY_NM_{i}")
                    st.selectbox("RULE_VALID_METH_CD", FIELDS["RULE_VALID_METH_CD"],
                               index=FIELDS["RULE_VALID_METH_CD"].index(row.get('RULE_VALID_METH_CD', FIELDS["RULE_VALID_METH_CD"][0])) if row.get('RULE_VALID_METH_CD') in FIELDS["RULE_VALID_METH_CD"] else 0,
                               key=f"edit_RULE_VALID_METH_CD_{i}")
                with col_id3:
                    st.selectbox("RULE_ABORT_IND", FIELDS["RULE_ABORT_IND"],
                               index=FIELDS["RULE_ABORT_IND"].index(row.get('RULE_ABORT_IND', FIELDS["RULE_ABORT_IND"][0])) if row.get('RULE_ABORT_IND') in FIELDS["RULE_ABORT_IND"] else 0,
                               key=f"edit_RULE_ABORT_IND_{i}")
                    st.selectbox("RULE_ACTV_IND", FIELDS["RULE_ACTV_IND"],
                               index=FIELDS["RULE_ACTV_IND"].index(row.get('RULE_ACTV_IND', FIELDS["RULE_ACTV_IND"][0])) if row.get('RULE_ACTV_IND') in FIELDS["RULE_ACTV_IND"] else 0,
                               key=f"edit_RULE_ACTV_IND_{i}")
                    st.selectbox("RULE_SEQ_NR", FIELDS["RULE_SEQ_NR"],
                               index=FIELDS["RULE_SEQ_NR"].index(row.get('RULE_SEQ_NR', FIELDS["RULE_SEQ_NR"][0])) if row.get('RULE_SEQ_NR') in FIELDS["RULE_SEQ_NR"] else 0,
                               key=f"edit_RULE_SEQ_NR_{i}")
                
                # Description
                st.text_area("RULE_DSC_TXT", value=row.get('RULE_DSC_TXT', ''), key=f"edit_RULE_DSC_TXT_{i}")
                
                # Source details
                st.markdown("**📤 Source Configuration**")
                col_src1, col_src2, col_src3 = st.columns(3)
                with col_src1:
                    st.selectbox("RULE_SRC_DB_NM", FIELDS["RULE_SRC_DB_NM"],
                               index=FIELDS["RULE_SRC_DB_NM"].index(row.get('RULE_SRC_DB_NM', FIELDS["RULE_SRC_DB_NM"][0])) if row.get('RULE_SRC_DB_NM') in FIELDS["RULE_SRC_DB_NM"] else 0,
                               key=f"edit_RULE_SRC_DB_NM_{i}")
                with col_src2:
                    st.selectbox("RULE_SRC_SCHM_NM", FIELDS["RULE_SRC_SCHM_NM"],
                               index=FIELDS["RULE_SRC_SCHM_NM"].index(row.get('RULE_SRC_SCHM_NM', FIELDS["RULE_SRC_SCHM_NM"][0])) if row.get('RULE_SRC_SCHM_NM') in FIELDS["RULE_SRC_SCHM_NM"] else 0,
                               key=f"edit_RULE_SRC_SCHM_NM_{i}")
                with col_src3:
                    st.text_input("RULE_SRC_OBJ_ID_TXT", value=row.get('RULE_SRC_OBJ_ID_TXT', ''), key=f"edit_RULE_SRC_OBJ_ID_TXT_{i}")
                st.text_input("RULE_SRC_ATTR_NM", value=row.get('RULE_SRC_ATTR_NM', ''), key=f"edit_RULE_SRC_ATTR_NM_{i}")
                
                # Target details
                st.markdown("**📥 Target Configuration**")
                col_tgt1, col_tgt2, col_tgt3 = st.columns(3)
                with col_tgt1:
                    st.selectbox("RULE_TRGT_DB_NM", FIELDS["RULE_TRGT_DB_NM"],
                               index=FIELDS["RULE_TRGT_DB_NM"].index(row.get('RULE_TRGT_DB_NM', FIELDS["RULE_TRGT_DB_NM"][0])) if row.get('RULE_TRGT_DB_NM') in FIELDS["RULE_TRGT_DB_NM"] else 0,
                               key=f"edit_RULE_TRGT_DB_NM_{i}")
                with col_tgt2:
                    st.text_input("RULE_TRGT_SCHM_NM", value=row.get('RULE_TRGT_SCHM_NM', ''), key=f"edit_RULE_TRGT_SCHM_NM_{i}")
                with col_tgt3:
                    st.text_input("RULE_TRGT_OBJ_ID_TXT", value=row.get('RULE_TRGT_OBJ_ID_TXT', ''), key=f"edit_RULE_TRGT_OBJ_ID_TXT_{i}")
                
                col_tgt4, col_tgt5 = st.columns(2)
                with col_tgt4:
                    st.text_input("RULE_TRGT_ATTR_NM", value=row.get('RULE_TRGT_ATTR_NM', ''), key=f"edit_RULE_TRGT_ATTR_NM_{i}")
                with col_tgt5:
                    st.selectbox("RULE_TRGT_DATA_LAYER_NM", FIELDS["RULE_TRGT_DATA_LAYER_NM"],
                               index=FIELDS["RULE_TRGT_DATA_LAYER_NM"].index(row.get('RULE_TRGT_DATA_LAYER_NM', FIELDS["RULE_TRGT_DATA_LAYER_NM"][0])) if row.get('RULE_TRGT_DATA_LAYER_NM') in FIELDS["RULE_TRGT_DATA_LAYER_NM"] else 0,
                               key=f"edit_RULE_TRGT_DATA_LAYER_NM_{i}")
                
                # Threshold values
                st.markdown("**⚖️ Threshold Configuration**")
                col_thresh1, col_thresh2, col_thresh3 = st.columns(3)
                with col_thresh1:
                    st.text_input("RULE_ACPT_VARY_PCT", value=row.get('RULE_ACPT_VARY_PCT', ''), key=f"edit_RULE_ACPT_VARY_PCT_{i}")
                with col_thresh2:
                    st.text_input("RULE_MIN_THRESH_VALUE_TXT", value=row.get('RULE_MIN_THRESH_VALUE_TXT', ''), key=f"edit_RULE_MIN_THRESH_VALUE_TXT_{i}")
                with col_thresh3:
                    st.text_input("RULE_MAX_THRESH_VALUE_TXT", value=row.get('RULE_MAX_THRESH_VALUE_TXT', ''), key=f"edit_RULE_MAX_THRESH_VALUE_TXT_{i}")
                
                # Logic and dates
                st.markdown("**🔧 Logic & Dates**")
                st.text_area("RULE_LOGIC_TXT", value=row.get('RULE_LOGIC_TXT', ''), key=f"edit_RULE_LOGIC_TXT_{i}")
                
                col_dates1, col_dates2, col_dates3 = st.columns(3)
                with col_dates1:
                    st.text_input("RULE_EFF_DT", value=row.get('RULE_EFF_DT', ''), key=f"edit_RULE_EFF_DT_{i}")
                with col_dates2:
                    st.text_input("RULE_EXP_DT", value=row.get('RULE_EXP_DT', ''), key=f"edit_RULE_EXP_DT_{i}")
                with col_dates3:
                    st.text_input("RULE_CDE_IND", value=row.get('RULE_CDE_IND', ''), key=f"edit_RULE_CDE_IND_{i}")
                
                #