import streamlit as st
import pandas as pd
import csv
import io
from datetime import datetime
from config import DEFAULT_VALUES, FIELDS, get_current_timestamp
from validation import (
    validate_single_row,
    validate_rule_abort_ind,
    validate_rule_trgt_attr_nm,
    validate_appl_cd,
    validate_rule_sequence_number,
    validate_rule_name_is_unique,
    validate_rule_name_matches_standards
)
from rule_generation import (
    generate_rule_name,
    generate_rule_description,
    update_all_auto_fields,
    update_rule_name_only,
    update_database_based_on_layer,
    update_description_only
)

# Page configuration
st.set_page_config(
    page_title="Data Quality Control Rules Manager",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'rows' not in st.session_state:
    st.session_state.rows = []

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

3. **View, edit, validate and export rules**
   - View all rules in table format
   - Edit individual rules inline
   - Validate all rules at once
   - Download processed rules

4. **Individual rule management**
   - Delete unwanted rules
   - Real-time validation feedback
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
    st.session_state.form_rule_trgt_schm_nm = FIELDS["RULE_TRGT_SCHM_NM"][0]
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
    update_all_auto_fields(st)

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
                     help="Enter complete application code (e.g., EMM_ORACLE, EMM_SAP)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_area("RULE_DSC_TXT", key="form_rule_dsc_txt", height=80, disabled=True,
                    help="Auto-generated description based on rule configuration")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.selectbox("RULE_VALID_CTGY_NM", FIELDS["RULE_VALID_CTGY_NM"], key="form_rule_valid_ctgy_nm")
    
    # RULE_VALID_METH_CD - triggers all auto-updates
    st.selectbox("RULE_VALID_METH_CD", FIELDS["RULE_VALID_METH_CD"], 
                key="form_rule_valid_meth_cd", on_change=update_all_auto_fields, args=(st,))
    
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
                key="form_rule_trgt_db_nm", on_change=update_rule_name_only, args=(st,))
    
    # RULE_TRGT_SCHM_NM - Fixed: Now uses selectbox with list options
    st.selectbox("RULE_TRGT_SCHM_NM", FIELDS["RULE_TRGT_SCHM_NM"], key="form_rule_trgt_schm_nm")
    
    # RULE_TRGT_OBJ_ID_TXT - triggers rule name update
    with st.container():
        st.markdown('<div class="uppercase-input">', unsafe_allow_html=True)
        st.text_input("RULE_TRGT_OBJ_ID_TXT", key="form_rule_trgt_obj_id_txt", 
                     on_change=update_rule_name_only, args=(st,))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # RULE_TRGT_DATA_LAYER_NM - triggers database and rule name update
    st.selectbox("RULE_TRGT_DATA_LAYER_NM", FIELDS["RULE_TRGT_DATA_LAYER_NM"], 
                key="form_rule_trgt_data_layer_nm", on_change=update_database_based_on_layer, args=(st,))
    
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
        st.text_input("RULE_NM", key="form_rule_nm", on_change=update_description_only, args=(st,),
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
                 help="Specify the attribute/column name to sum", on_change=update_description_only, args=(st,))
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

# Display validation errors for new rule addition
if 'validation_errors' in st.session_state:
    st.markdown('<div class="validation-error">', unsafe_allow_html=True)
    st.error("**❌ Validation Errors:**")
    for error in st.session_state.validation_errors:
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
    
    # Action buttons section - moved here
    col_validate, col_download = st.columns(2)

    with col_validate:
        if st.button("🔍 Validate All Rules", use_container_width=True):
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

    # Display validation errors for all rules validation
    if 'all_validation_errors' in st.session_state:
        st.markdown('<div class="validation-error">', unsafe_allow_html=True)
        st.error("**❌ Validation Errors Found:**")
        for error in st.session_state.all_validation_errors:
            st.error(f"• {error}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display complete rules table with all fields
    st.subheader("📊 Complete Rules Overview")
    df = pd.DataFrame(st.session_state.rows)
    st.dataframe(df, use_container_width=True, height=400)
    
    # Individual rule management with editing capability
    st.subheader("🔧 Individual Rule Management")
    for i, row in enumerate(st.session_state.rows):
        with st.expander(f"Rule {i+1}: {row.get('RULE_NM', 'Unnamed Rule')}", expanded=False):
            
            # Create editable form for each rule
            st.markdown("**✏️ Edit Rule Details**")
            
            # Use columns for better layout
            col_edit1, col_edit2 = st.columns(2)
            
            with col_edit1:
                # Core identification fields
                st.markdown("**📋 Core Information**")
                edit_appl_cd = st.text_input("APPL_CD", value=row.get('APPL_CD', ''), key=f"edit_appl_cd_{i}")
                edit_rule_nm = st.text_input("RULE_NM", value=row.get('RULE_NM', ''), key=f"edit_rule_nm_{i}")
                edit_rule_dsc_txt = st.text_area("RULE_DSC_TXT", value=row.get('RULE_DSC_TXT', ''), key=f"edit_rule_dsc_txt_{i}", height=100)
                
                edit_rule_valid_ctgy_nm = st.selectbox("RULE_VALID_CTGY_NM", 
                                                     FIELDS["RULE_VALID_CTGY_NM"], 
                                                     index=FIELDS["RULE_VALID_CTGY_NM"].index(row.get('RULE_VALID_CTGY_NM', FIELDS["RULE_VALID_CTGY_NM"][0])) if row.get('RULE_VALID_CTGY_NM') in FIELDS["RULE_VALID_CTGY_NM"] else 0,
                                                     key=f"edit_rule_valid_ctgy_nm_{i}")
                
                edit_rule_valid_meth_cd = st.selectbox("RULE_VALID_METH_CD", 
                                                     FIELDS["RULE_VALID_METH_CD"], 
                                                     index=FIELDS["RULE_VALID_METH_CD"].index(row.get('RULE_VALID_METH_CD', FIELDS["RULE_VALID_METH_CD"][0])) if row.get('RULE_VALID_METH_CD') in FIELDS["RULE_VALID_METH_CD"] else 0,
                                                     key=f"edit_rule_valid_meth_cd_{i}")
                
                edit_rule_abort_ind = st.selectbox("RULE_ABORT_IND", 
                                                 FIELDS["RULE_ABORT_IND"], 
                                                 index=FIELDS["RULE_ABORT_IND"].index(row.get('RULE_ABORT_IND', FIELDS["RULE_ABORT_IND"][0])) if row.get('RULE_ABORT_IND') in FIELDS["RULE_ABORT_IND"] else 0,
                                                 key=f"edit_rule_abort_ind_{i}")
                
                edit_rule_actv_ind = st.selectbox("RULE_ACTV_IND", 
                                                FIELDS["RULE_ACTV_IND"], 
                                                index=FIELDS["RULE_ACTV_IND"].index(row.get('RULE_ACTV_IND', FIELDS["RULE_ACTV_IND"][0])) if row.get('RULE_ACTV_IND') in FIELDS["RULE_ACTV_IND"] else 0,
                                                key=f"edit_rule_actv_ind_{i}")
                
                edit_rule_seq_nr = st.selectbox("RULE_SEQ_NR", 
                                               FIELDS["RULE_SEQ_NR"], 
                                               index=FIELDS["RULE_SEQ_NR"].index(row.get('RULE_SEQ_NR', FIELDS["RULE_SEQ_NR"][0])) if row.get('RULE_SEQ_NR') in FIELDS["RULE_SEQ_NR"] else 0,
                                               key=f"edit_rule_seq_nr_{i}")
                
                # Source details
                st.markdown("**📤 Source Configuration**")
                edit_rule_src_db_nm = st.selectbox("RULE_SRC_DB_NM", 
                                                 FIELDS["RULE_SRC_DB_NM"], 
                                                 index=FIELDS["RULE_SRC_DB_NM"].index(row.get('RULE_SRC_DB_NM', FIELDS["RULE_SRC_DB_NM"][0])) if row.get('RULE_SRC_DB_NM') in FIELDS["RULE_SRC_DB_NM"] else 0,
                                                 key=f"edit_rule_src_db_nm_{i}")
                
                edit_rule_src_schm_nm = st.selectbox("RULE_SRC_SCHM_NM", 
                                                   FIELDS["RULE_SRC_SCHM_NM"], 
                                                   index=FIELDS["RULE_SRC_SCHM_NM"].index(row.get('RULE_SRC_SCHM_NM', FIELDS["RULE_SRC_SCHM_NM"][0])) if row.get('RULE_SRC_SCHM_NM') in FIELDS["RULE_SRC_SCHM_NM"] else 0,
                                                   key=f"edit_rule_src_schm_nm_{i}")
                
                edit_rule_src_obj_id_txt = st.text_input("RULE_SRC_OBJ_ID_TXT", value=row.get('RULE_SRC_OBJ_ID_TXT', ''), key=f"edit_rule_src_obj_id_txt_{i}")
                edit_rule_src_attr_nm = st.text_input("RULE_SRC_ATTR_NM", value=row.get('RULE_SRC_ATTR_NM', ''), key=f"edit_rule_src_attr_nm_{i}")

            with col_edit2:
                # Target details
                st.markdown("**📥 Target Configuration**")
                edit_rule_trgt_db_nm = st.selectbox("RULE_TRGT_DB_NM", 
                                                  FIELDS["RULE_TRGT_DB_NM"], 
                                                  index=FIELDS["RULE_TRGT_DB_NM"].index(row.get('RULE_TRGT_DB_NM', FIELDS["RULE_TRGT_DB_NM"][0])) if row.get('RULE_TRGT_DB_NM') in FIELDS["RULE_TRGT_DB_NM"] else 0,
                                                  key=f"edit_rule_trgt_db_nm_{i}")
                
                edit_rule_trgt_schm_nm = st.selectbox("RULE_TRGT_SCHM_NM", 
                                                    FIELDS["RULE_TRGT_SCHM_NM"], 
                                                    index=FIELDS["RULE_TRGT_SCHM_NM"].index(row.get('RULE_TRGT_SCHM_NM', FIELDS["RULE_TRGT_SCHM_NM"][0])) if row.get('RULE_TRGT_SCHM_NM') in FIELDS["RULE_TRGT_SCHM_NM"] else 0,
                                                    key=f"edit_rule_trgt_schm_nm_{i}")
                
                edit_rule_trgt_obj_id_txt = st.text_input("RULE_TRGT_OBJ_ID_TXT", value=row.get('RULE_TRGT_OBJ_ID_TXT', ''), key=f"edit_rule_trgt_obj_id_txt_{i}")
                edit_rule_trgt_attr_nm = st.text_input("RULE_TRGT_ATTR_NM", value=row.get('RULE_TRGT_ATTR_NM', ''), key=f"edit_rule_trgt_attr_nm_{i}")
                
                edit_rule_trgt_data_layer_nm = st.selectbox("RULE_TRGT_DATA_LAYER_NM", 
                                                          FIELDS["RULE_TRGT_DATA_LAYER_NM"], 
                                                          index=FIELDS["RULE_TRGT_DATA_LAYER_NM"].index(row.get('RULE_TRGT_DATA_LAYER_NM', FIELDS["RULE_TRGT_DATA_LAYER_NM"][0])) if row.get('RULE_TRGT_DATA_LAYER_NM') in FIELDS["RULE_TRGT_DATA_LAYER_NM"] else 0,
                                                          key=f"edit_rule_trgt_data_layer_nm_{i}")
                
                # Threshold values
                st.markdown("**⚖️ Threshold Configuration**")
                edit_rule_acpt_vary_pct = st.text_input("RULE_ACPT_VARY_PCT", value=row.get('RULE_ACPT_VARY_PCT', ''), key=f"edit_rule_acpt_vary_pct_{i}")
                edit_rule_min_thresh_value_txt = st.text_input("RULE_MIN_THRESH_VALUE_TXT", value=row.get('RULE_MIN_THRESH_VALUE_TXT', ''), key=f"edit_rule_min_thresh_value_txt_{i}")
                edit_rule_max_thresh_value_txt = st.text_input("RULE_MAX_THRESH_VALUE_TXT", value=row.get('RULE_MAX_THRESH_VALUE_TXT', ''), key=f"edit_rule_max_thresh_value_txt_{i}")
                
                # Additional fields
                st.markdown("**📝 Additional Information**")
                edit_rule_rmrk_txt = st.text_area("RULE_RMRK_TXT", value=row.get('RULE_RMRK_TXT', ''), key=f"edit_rule_rmrk_txt_{i}")
                edit_asset_nm = st.text_input("ASSET_NM", value=row.get('ASSET_NM', ''), key=f"edit_asset_nm_{i}")
            
            # Rule logic - full width
            st.markdown("**🔧 Rule Logic**")
            edit_rule_logic_txt = st.text_area("RULE_LOGIC_TXT", value=row.get('RULE_LOGIC_TXT', ''), key=f"edit_rule_logic_txt_{i}", height=100)
            
            # Display read-only fields
            st.markdown("**🕒 System Information (Read-Only)**")
            col_ro1, col_ro2, col_ro3 = st.columns(3)
            with col_ro1:
                st.text_input("DATA_QC_ID", value=row.get('DATA_QC_ID', ''), disabled=True, key=f"ro_data_qc_id_{i}")
                st.text_input("RULE_FREQ_CD", value=row.get('RULE_FREQ_CD', ''), disabled=True, key=f"ro_rule_freq_cd_{i}")
                st.text_input("RULE_CDE_IND", value=row.get('RULE_CDE_IND', ''), disabled=True, key=f"ro_rule_cde_ind_{i}")
            with col_ro2:
                st.text_input("RULE_EFF_DT", value=row.get('RULE_EFF_DT', ''), disabled=True, key=f"ro_rule_eff_dt_{i}")
                st.text_input("RULE_EXP_DT", value=row.get('RULE_EXP_DT', ''), disabled=True, key=f"ro_rule_exp_dt_{i}")
                st.text_input("ASSET_ID", value=row.get('ASSET_ID', ''), disabled=True, key=f"ro_asset_id_{i}")
            with col_ro3:
                st.text_input("CREA_PRTY_ID", value=row.get('CREA_PRTY_ID', ''), disabled=True, key=f"ro_crea_prty_id_{i}")
                st.text_input("CREA_TS", value=row.get('CREA_TS', ''), disabled=True, key=f"ro_crea_ts_{i}")
                st.text_input("UPDT_PRTY_ID", value=row.get('UPDT_PRTY_ID', ''), disabled=True, key=f"ro_updt_prty_id_{i}")
            
            # Action buttons
            st.markdown("---")
            col_save, col_delete = st.columns(2)
            
            with col_save:
                if st.button(f"💾 Save Changes", key=f"save_{i}", use_container_width=True, type="primary"):
                    # Update the row with edited values
                    updated_row = {
                        "DATA_QC_ID": row.get('DATA_QC_ID', DEFAULT_VALUES["DATA_QC_ID"]),
                        "APPL_CD": edit_appl_cd.upper(),
                        "RULE_NM": edit_rule_nm.upper(),
                        "RULE_DSC_TXT": edit_rule_dsc_txt.upper(),
                        "RULE_FREQ_CD": row.get('RULE_FREQ_CD', DEFAULT_VALUES["RULE_FREQ_CD"]),
                        "RULE_VALID_CTGY_NM": edit_rule_valid_ctgy_nm,
                        "RULE_VALID_METH_CD": edit_rule_valid_meth_cd,
                        "RULE_ABORT_IND": edit_rule_abort_ind,
                        "RULE_SRC_DB_NM": edit_rule_src_db_nm,
                        "RULE_SRC_SCHM_NM": edit_rule_src_schm_nm,
                        "RULE_SRC_OBJ_ID_TXT": edit_rule_src_obj_id_txt.upper(),
                        "RULE_SRC_ATTR_NM": edit_rule_src_attr_nm.upper(),
                        "RULE_TRGT_DB_NM": edit_rule_trgt_db_nm,
                        "RULE_TRGT_SCHM_NM": edit_rule_trgt_schm_nm,
                        "RULE_TRGT_OBJ_ID_TXT": edit_rule_trgt_obj_id_txt.upper(),
                        "RULE_TRGT_ATTR_NM": edit_rule_trgt_attr_nm.upper(),
                        "RULE_ACPT_VARY_PCT": edit_rule_acpt_vary_pct,
                        "RULE_MIN_THRESH_VALUE_TXT": edit_rule_min_thresh_value_txt,
                        "RULE_MAX_THRESH_VALUE_TXT": edit_rule_max_thresh_value_txt,
                        "RULE_TRGT_DATA_LAYER_NM": edit_rule_trgt_data_layer_nm,
                        "RULE_CDE_IND": row.get('RULE_CDE_IND', DEFAULT_VALUES["RULE_CDE_IND"]),
                        "RULE_LOGIC_TXT": edit_rule_logic_txt.upper(),
                        "RULE_EFF_DT": row.get('RULE_EFF_DT', datetime.today().strftime("%Y-%m-%d")),
                        "RULE_EXP_DT": row.get('RULE_EXP_DT', DEFAULT_VALUES["RULE_EXP_DT"]),
                        "RULE_ACTV_IND": edit_rule_actv_ind,
                        "RULE_RMRK_TXT": edit_rule_rmrk_txt.upper(),
                        "CREA_PRTY_ID": row.get('CREA_PRTY_ID', "PL6P223"),
                        "CREA_TS": row.get('CREA_TS', get_current_timestamp()),
                        "UPDT_PRTY_ID": "PL6P223",
                        "UPDT_TS": get_current_timestamp(),
                        "ETL_CREA_NR": row.get('ETL_CREA_NR', ""),
                        "ETL_CREA_TS": row.get('ETL_CREA_TS', ""),
                        "ETL_UPDT_NR": row.get('ETL_UPDT_NR', ""),
                        "ETL_UPDT_TS": row.get('ETL_UPDT_TS', ""),
                        "ASSET_ID": row.get('ASSET_ID', DEFAULT_VALUES["ASSET_ID"]),
                        "ASSET_NM": edit_asset_nm.upper(),
                        "RULE_SEQ_NR": edit_rule_seq_nr
                    }
                    
                    # Validate the updated rule
                    temp_rows = st.session_state.rows.copy()
                    temp_rows[i] = updated_row
                    validation_errors = validate_single_row(updated_row, temp_rows, is_new_row=False)
                    
                    if validation_errors:
                        st.error("**❌ Validation Errors:**")
                        for error in validation_errors:
                            st.error(f"• {error}")
                    else:
                        st.session_state.rows[i] = updated_row
                        st.success("✅ Rule updated successfully!")
                        st.rerun()
            
            with col_delete:
                if st.button(f"🗑️ Delete Rule", key=f"delete_{i}", use_container_width=True):
                    st.session_state.rows.pop(i)
                    st.success("✅ Rule deleted successfully!")
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("**Data Quality Control Rules Manager** - Streamlit Version")
st.markdown("For DQC Rule Naming Standards, refer to the [documentation](https://wiki.usaa.com/display/EMM/Data+Control+Framework#Architecture-DQCRuleNamingStandards)")