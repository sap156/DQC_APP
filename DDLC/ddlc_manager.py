import streamlit as st
import pandas as pd
import io
from datetime import datetime
import xlsxwriter
from collections import defaultdict
import re

# Page configuration
st.set_page_config(
    page_title="DDLC Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mappings' not in st.session_state:
    st.session_state.mappings = []
if 'project_info' not in st.session_state:
    st.session_state.project_info = {}

def main():
    st.markdown('<h1 class="main-header">🏗️ DDLC Manager</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Data Definition Language Changes Manager for Medallion Architecture</div>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page:", [
        "Project Setup", 
        "DL2 → Foundation Mapping", 
        "Foundation → Information Mapping",
        "Generate Reports"
    ])
    
    if page == "Project Setup":
        project_setup_page()
    elif page == "DL2 → Foundation Mapping":
        dl2_foundation_mapping_page()
    elif page == "Foundation → Information Mapping":
        foundation_information_mapping_page()
    elif page == "Generate Reports":
        generate_reports_page()

def project_setup_page():
    st.markdown('<h2 class="section-header">📋 Project Information</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project Name", value=st.session_state.project_info.get('project_name', ''))
        version = st.text_input("Version", value=st.session_state.project_info.get('version', 'v1'))
        author = st.text_input("Author", value=st.session_state.project_info.get('author', ''))
        
    with col2:
        classification = st.selectbox("Classification", 
                                    ["USAA INTERNAL", "PUBLIC", "CONFIDENTIAL"],
                                    index=0 if st.session_state.project_info.get('classification') == 'USAA INTERNAL' else 0)
        update_date = st.date_input("Update Date", value=datetime.now().date())
        description = st.text_area("Project Description", 
                                 value=st.session_state.project_info.get('description', ''))
    
    if st.button("Save Project Information"):
        st.session_state.project_info = {
            'project_name': project_name,
            'version': version,
            'author': author,
            'classification': classification,
            'update_date': update_date,
            'description': description
        }
        st.success("Project information saved!")

def dl2_foundation_mapping_page():
    st.markdown('<h2 class="section-header">🔄 DL2 → Foundation Layer Mapping</h2>', unsafe_allow_html=True)
    
    with st.form("dl2_foundation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Source (DL2) Details")
            source_database = st.text_input("Source Database", value="PROD_DL2_CHIEF_FINANCIAL_OFFICE_RQ")
            source_schema = st.text_input("Source Schema", value="ENTERPRISE")
            source_table = st.text_input("Source Table Name", placeholder="e.g., EWJ_DW_AUTOMATIC_PAYMENT_PLAN")
        
        with col2:
            st.subheader("📝 Target (Foundation) Details")
            target_database = st.text_input("Foundation Database", value="PCFOPAYMENTSDBI")
            target_schema = st.text_input("Foundation Schema", value="APP_CFOPYMT5")
            target_table = st.text_input("Foundation Table Name", placeholder="e.g., APP_AUTOMATIC_PAYMENT_PLAN")
        
        st.subheader("🔧 Foundation Table DDL Script")
        ddl_script = st.text_area(
            "Paste your CREATE TABLE DDL script here:",
            placeholder="""create or replace TRANSIENT TABLE OCFOPAYMENTSDBI.APP_CFOPYMTS.API1_API_INVOICE_STATUS_ACTION (
    KAFKA_HEADERS VARCHAR(16777216),
    KAFKA_META VARCHAR(16777216),
    MFP_ASSET_NM VARCHAR(16777216),
    MFP_FILE_ID VARCHAR(16777216),
    MFP_LOAD_TS VARCHAR(16777216),
    ...
);""",
            height=300
        )
        
        submitted = st.form_submit_button("🚀 Parse DDL and Generate Mappings")
        
        if submitted and target_table and ddl_script and source_table:
            try:
                # Parse DDL script to extract columns
                columns = parse_ddl_script(ddl_script)
                
                if columns:
                    # Generate mappings for each column
                    mappings_added = 0
                    for column_name, data_type in columns:
                        mapping = {
                            'layer_transition': 'DL2_to_Foundation',
                            'source_database': source_database,
                            'source_schema': source_schema,
                            'source_table': source_table,
                            'source_field': '',  # To be filled by user
                            'target_database': target_database,
                            'target_schema': target_schema,
                            'target_table': target_table,
                            'target_field': column_name,
                            'target_data_type': data_type,
                            'transformation_logic': '',  # To be filled by user
                            'change_type': 'New Field Added',
                            'timestamp': datetime.now()
                        }
                        st.session_state.mappings.append(mapping)
                        mappings_added += 1
                    
                    st.success(f"🎉 Successfully parsed DDL script and added {mappings_added} field mappings for {target_table}!")
                    st.info("📝 Note: Source field names and transformation logic are left empty for you to fill in later.")
                    st.rerun()
                else:
                    st.error("❌ Could not parse any columns from the DDL script. Please check the format.")
            except Exception as e:
                st.error(f"❌ Error parsing DDL script: {str(e)}")
    
    # Add overview of all tables at the bottom
    st.markdown('<h3 class="section-header">📊 All DL2 → Foundation Tables Overview</h3>', unsafe_allow_html=True)
    display_current_mappings("DL2_to_Foundation")

def foundation_information_mapping_page():
    st.markdown('<h2 class="section-header">🔄 Foundation → Information Layer Mapping</h2>', unsafe_allow_html=True)
    st.info("Note: Only Foundation → Information Final mappings are supported in DDLC")
    
    with st.form("foundation_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Source (Foundation) Details")
            source_database = st.text_input("Source Database", value="PCFOPAYMENTSDBI")
            source_schema = st.text_input("Source Schema", value="APP_CFOPYMT5")
            source_table = st.text_input("Source Table Name", placeholder="e.g., APP_AUTOMATIC_PAYMENT_PLAN")
        
        with col2:
            st.subheader("📝 Target (Information) Details")
            target_database = st.text_input("Information Database", value="PCFOINFOMDBI")
            target_schema = st.text_input("Information Schema", value="APP_CFOPYMT5")
            target_table = st.text_input("Information Table Name", placeholder="e.g., AMATIC_PMT_PLAN")
        
        st.subheader("🔧 DBT Transformation Logic")
        dbt_script = st.text_area(
            "Paste your DBT SELECT statement here:",
            placeholder="""{{ handle_empty_or_null_value(chk_type='VARCHAR', length=36, first_val='ABA_ROUTING_NR') }} AS ABA_ROUTE_NR,
{{ handle_empty_or_null_value(chk_type='VARCHAR', length=150, first_val='ACCOUNT_HOLDER_FULL_NM') }} AS ACCT_HOLD_FULL_NM,
{{ handle_empty_or_null_value(chk_type='NUMBER', is_string=true, length=3, precision=0, first_val='RETRY_ATTEMPT_NR') }} AS RETRY_ATMPT_CNT,
{{ handle_empty_or_null_value(chk_type='TIMESTAMP', is_string=true, empty_val='', default_val='1800-01-02 00:00:00.000000', format='YYYY-MM-DD HH:MI:SS.FF6', first_val='AUTH_START_GMTS') }} AS AUTH_START_TS,
...""",
            height=300
        )
        
        submitted = st.form_submit_button("🚀 Parse DBT and Generate Mappings")
        
        if submitted and target_table and dbt_script and source_table:
            try:
                # Parse DBT script to extract field mappings
                field_mappings = parse_dbt_script(dbt_script)
                
                if field_mappings:
                    # Generate mappings for each field
                    mappings_added = 0
                    for source_field, target_field, transformation in field_mappings:
                        mapping = {
                            'layer_transition': 'Foundation_to_Information',
                            'source_database': source_database,
                            'source_schema': source_schema,
                            'source_table': source_table,
                            'source_field': source_field,
                            'target_database': target_database,
                            'target_schema': target_schema,
                            'target_table': target_table,
                            'target_field': target_field,
                            'transformation_logic': transformation,
                            'change_type': 'New Field Added',
                            'timestamp': datetime.now()
                        }
                        st.session_state.mappings.append(mapping)
                        mappings_added += 1
                    
                    st.success(f"🎉 Successfully parsed DBT script and added {mappings_added} field mappings for {target_table}!")
                    st.info("📝 Note: Review the parsed transformation logic for accuracy.")
                    st.rerun()
                else:
                    st.error("❌ Could not parse any field mappings from the DBT script. Please check the format.")
            except Exception as e:
                st.error(f"❌ Error parsing DBT script: {str(e)}")
    
    # Add overview of all tables at the bottom
    st.markdown('<h3 class="section-header">📊 All Foundation → Information Tables Overview</h3>', unsafe_allow_html=True)
    display_current_mappings("Foundation_to_Information")

def display_current_mappings(layer_type):
    st.markdown(f'<h3 class="section-header">📊 All {layer_type.replace("_", " → ")} Tables Overview</h3>', unsafe_allow_html=True)
    
    filtered_mappings = [m for m in st.session_state.mappings if m['layer_transition'] == layer_type]
    
    if filtered_mappings:
        # Group by target table
        tables = defaultdict(list)
        for mapping in filtered_mappings:
            tables[mapping['target_table']].append(mapping)
        
        # Display summary for each table
        for table_name, table_mappings in tables.items():
            with st.expander(f"📊 {table_name} ({len(table_mappings)} mappings)", expanded=False):
                df = pd.DataFrame(table_mappings)
                display_columns = ['source_table', 'source_field', 'target_field', 'transformation_logic', 'change_type']
                if 'target_data_type' in df.columns:
                    display_columns.insert(3, 'target_data_type')
                st.dataframe(df[display_columns], use_container_width=True)
                
                col1, col2 = st.columns([2, 1])
                with col2:
                    if st.button(f"🗑️ Delete {table_name}", key=f"delete_{layer_type}_{table_name}"):
                        st.session_state.mappings = [m for m in st.session_state.mappings 
                                                   if not (m['layer_transition'] == layer_type and m['target_table'] == table_name)]
                        st.success(f"Deleted all mappings for {table_name}")
                        st.rerun()
        
        # Overall summary
        st.markdown("### 📈 Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Tables", len(tables))
        col2.metric("Total Mappings", len(filtered_mappings))
        
        # Option to clear all mappings
        if st.button(f"🗑️ Clear ALL {layer_type} Mappings", key=f"clear_all_{layer_type}"):
            st.session_state.mappings = [m for m in st.session_state.mappings if m['layer_transition'] != layer_type]
            st.success(f"Cleared all {layer_type} mappings")
            st.rerun()
    else:
        st.info("No mappings added yet.")

def parse_ddl_script(ddl_script):
    """Parse DDL script to extract column names and data types."""
    columns = []
    
    # Clean the script and extract the part between parentheses
    ddl_script = ddl_script.strip()
    
    # Find the table definition part (between parentheses)
    start_paren = ddl_script.find('(')
    end_paren = ddl_script.rfind(')')
    
    if start_paren == -1 or end_paren == -1:
        return columns
    
    table_def = ddl_script[start_paren+1:end_paren]
    
    # Split by lines and process each line
    lines = table_def.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('--') or line.startswith('/*'):
            continue
            
        # Remove trailing comma and clean up
        line = line.rstrip(',').strip()
        
        # Skip constraint definitions
        if any(keyword in line.upper() for keyword in ['PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', 'INDEX', 'KEY']):
            continue
            
        # Match column definition pattern: COLUMN_NAME DATA_TYPE(size)
        # Handle various patterns like VARCHAR(16777216), NUMBER(38,0), etc.
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z]+(?:\([^)]+\))?)', line)
        
        if match:
            column_name = match.group(1)
            data_type = match.group(2)
            columns.append((column_name, data_type))
    
    return columns

def parse_dbt_script(dbt_script):
    """Parse DBT script to extract field mappings and transformations with detailed logic."""
    field_mappings = []
    
    # Split by lines and process each line
    lines = dbt_script.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('--') or line.startswith('/*'):
            continue
            
        # Remove trailing comma
        line = line.rstrip(',').strip()
        
        # Pattern 1: {{ handle_empty_or_null_value(...) }} AS target_field
        dbt_function_match = re.search(r'\{\{\s*handle_empty_or_null_value\(([^}]+)\)\s*\}\}\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)', line, re.IGNORECASE)
        
        if dbt_function_match:
            function_params = dbt_function_match.group(1).strip()
            target_field = dbt_function_match.group(2).strip()
            
            # Parse the function parameters
            source_field, transformation_description = parse_handle_empty_or_null_value(function_params)
            
            field_mappings.append((source_field, target_field, transformation_description))
            continue
        
        # Pattern 2: Other {{ function(...) }} AS target_field
        other_dbt_function_match = re.search(r'\{\{\s*([^}]+)\s*\}\}\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)', line, re.IGNORECASE)
        
        if other_dbt_function_match:
            transformation = other_dbt_function_match.group(1).strip()
            target_field = other_dbt_function_match.group(2).strip()
            
            # Try to extract source field from transformation
            source_field = extract_source_field_from_transformation(transformation)
            
            field_mappings.append((source_field, target_field, f"{{{{ {transformation} }}}}"))
            continue
        
        # Pattern 3: source_field AS target_field
        simple_alias_match = re.search(r'^([A-Za-z_][A-Za-z0-9_]*)\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)', line, re.IGNORECASE)
        
        if simple_alias_match:
            source_field = simple_alias_match.group(1).strip()
            target_field = simple_alias_match.group(2).strip()
            field_mappings.append((source_field, target_field, "Direct mapping"))
            continue
        
        # Pattern 4: CASE statements, functions, etc.
        case_match = re.search(r'(CASE\s+.+?END)\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)', line, re.IGNORECASE | re.DOTALL)
        
        if case_match:
            transformation = case_match.group(1).strip()
            target_field = case_match.group(2).strip()
            source_field = extract_source_field_from_transformation(transformation)
            field_mappings.append((source_field, target_field, transformation))
    
    return field_mappings

def parse_handle_empty_or_null_value(params_str):
    """Parse handle_empty_or_null_value function parameters and generate transformation description."""
    
    # Extract parameters using regex
    chk_type_match = re.search(r"chk_type=['\"]([^'\"]+)['\"]", params_str)
    first_val_match = re.search(r"first_val=['\"]([^'\"]+)['\"]", params_str)
    length_match = re.search(r"length=(\d+)", params_str)
    precision_match = re.search(r"precision=(\d+)", params_str)
    default_val_match = re.search(r"default_val=['\"]([^'\"]+)['\"]", params_str)
    empty_val_match = re.search(r"empty_val=['\"]([^'\"]*)['\"]", params_str)
    format_match = re.search(r"format=['\"]([^'\"]+)['\"]", params_str)
    is_string_match = re.search(r"is_string=(\w+)", params_str)
    
    # Extract values
    chk_type = chk_type_match.group(1) if chk_type_match else ""
    source_field = first_val_match.group(1) if first_val_match else ""
    length = int(length_match.group(1)) if length_match else 0
    precision = int(precision_match.group(1)) if precision_match else 0
    default_val = default_val_match.group(1) if default_val_match else ""
    empty_val = empty_val_match.group(1) if empty_val_match else ""
    format_val = format_match.group(1) if format_match else ""
    is_string = is_string_match.group(1).lower() == 'true' if is_string_match else False
    
    # Generate transformation description based on data type and parameters
    transformation_parts = []
    
    if chk_type.upper() == 'VARCHAR':
        transformation_parts.append(f"Transform {source_field} to VARCHAR({length})")
        transformation_parts.append("Replace NULL values with '!'")
    
    elif chk_type.upper() == 'NUMBER':
        if precision == 0:
            transformation_parts.append(f"Transform {source_field} to NUMBER({length},{precision})")
            transformation_parts.append("Replace NULL values with '-1'")
        else:
            transformation_parts.append(f"Transform {source_field} to NUMBER({length},{precision})")
            transformation_parts.append("NULL values remain NULL (precision > 0)")
    
    elif chk_type.upper() == 'TIMESTAMP':
        transformation_parts.append(f"Transform {source_field} to TIMESTAMP")
        if default_val:
            transformation_parts.append(f"Set default value to '{default_val}' if empty")
        if format_val:
            transformation_parts.append(f"Format: {format_val}")
    
    elif chk_type.upper() == 'DATE':
        transformation_parts.append(f"Transform {source_field} to DATE")
        if default_val:
            transformation_parts.append(f"Set default value to '{default_val}' if empty")
        if format_val:
            transformation_parts.append(f"Format: {format_val}")
        if empty_val:
            transformation_parts.append(f"Empty value representation: '{empty_val}'")
    
    else:
        # Generic handling for other types
        transformation_parts.append(f"Transform {source_field} to {chk_type}")
        if default_val:
            transformation_parts.append(f"Default value: '{default_val}'")
    
    # Add string conversion note if applicable
    if is_string:
        transformation_parts.append("Convert to string representation")
    
    transformation_description = "; ".join(transformation_parts)
    
    return source_field, transformation_description

def extract_source_field_from_transformation(transformation):
    """Extract source field name from transformation logic."""
    # Look for field names in quotes or as parameters
    
    # Pattern 1: first_val='FIELD_NAME'
    first_val_match = re.search(r"first_val=['\"]([^'\"]+)['\"]", transformation)
    if first_val_match:
        return first_val_match.group(1)
    
    # Pattern 2: Look for field names (assume uppercase with underscores)
    field_match = re.search(r'\b([A-Z][A-Z0-9_]*)\b', transformation)
    if field_match:
        return field_match.group(1)
    
    # If no source field found, return empty string
    return ""

def generate_reports_page():
    st.markdown('<h2 class="section-header">📊 Generate Reports</h2>', unsafe_allow_html=True)
    
    if not st.session_state.mappings:
        st.warning("No mappings found. Please add some mappings first.")
        return
    
    # Separate mappings by layer
    foundation_mappings = [m for m in st.session_state.mappings if m['layer_transition'] == 'DL2_to_Foundation']
    information_mappings = [m for m in st.session_state.mappings if m['layer_transition'] == 'Foundation_to_Information']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Foundation Layer Reports")
        if foundation_mappings:
            if st.button("📋 Generate Foundation Layer Excel", use_container_width=True):
                excel_buffer = generate_foundation_excel_report(foundation_mappings)
                st.download_button(
                    label="Download Foundation Layer Excel",
                    data=excel_buffer,
                    file_name=f"Foundation_Layer_DDLC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No Foundation layer mappings available")
    
    with col2:
        st.markdown("### Information Layer Reports")
        if information_mappings:
            if st.button("📋 Generate Information Layer Excel", use_container_width=True):
                excel_buffer = generate_information_excel_report(information_mappings)
                st.download_button(
                    label="Download Information Layer Excel",
                    data=excel_buffer,
                    file_name=f"Information_Layer_DDLC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No Information layer mappings available")
    
    # Display summary statistics
    st.markdown('<h3 class="section-header">📈 Summary Statistics</h3>', unsafe_allow_html=True)
    
    # Get unique tables for each layer
    foundation_tables = set()
    information_tables = set()
    
    for mapping in foundation_mappings:
        foundation_tables.add(mapping['target_table'])
    
    for mapping in information_mappings:
        information_tables.add(mapping['target_table'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Foundation Mappings", len(foundation_mappings))
    col2.metric("Information Mappings", len(information_mappings))
    col3.metric("Foundation Tables", len(foundation_tables))
    col4.metric("Information Tables", len(information_tables))

def generate_foundation_excel_report(mappings):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'fg_color': '#4472C4',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    source_format = workbook.add_format({
        'fg_color': '#D5E4BC',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    transform_format = workbook.add_format({
        'fg_color': '#9BC2E6',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    target_format = workbook.add_format({
        'fg_color': '#D1C4E9',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    # Group mappings by target table
    tables = defaultdict(list)
    for mapping in mappings:
        tables[mapping['target_table']].append(mapping)
    
    # Create a worksheet for each table
    for table_name, table_mappings in tables.items():
        # Clean table name for sheet name (Excel has restrictions)
        sheet_name = table_name[:31]  # Excel sheet names max 31 chars
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Headers
        headers = ['Database', 'Schema', 'Table Name', 'Field Name', 'Transformation Logic', 
                  'Database', 'Schema', 'Table Name', 'Column Name']
        
        # Add table info at the top
        worksheet.merge_range('A1:I1', f'Foundation Layer - {table_name}', header_format)
        worksheet.write('A2', f'Total Fields: {len(table_mappings)}', header_format)
        
        # Write section headers
        worksheet.merge_range('A3:D3', 'SOURCE (DL2)', header_format)
        worksheet.merge_range('E3:E3', 'TRANSFORMATION', header_format) 
        worksheet.merge_range('F3:I3', 'TARGET (Foundation)', header_format)
        
        # Write column headers
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)
        
        # Write data
        for row, mapping in enumerate(table_mappings, start=4):
            # Source columns (DL2)
            worksheet.write(row, 0, mapping.get('source_database', ''), source_format)
            worksheet.write(row, 1, mapping.get('source_schema', ''), source_format)
            worksheet.write(row, 2, mapping.get('source_table', ''), source_format)
            worksheet.write(row, 3, mapping.get('source_field', ''), source_format)
            
            # Transformation
            worksheet.write(row, 4, mapping.get('transformation_logic', ''), transform_format)
            
            # Target columns (Foundation)
            worksheet.write(row, 5, mapping.get('target_database', ''), target_format)
            worksheet.write(row, 6, mapping.get('target_schema', ''), target_format)
            worksheet.write(row, 7, mapping.get('target_table', ''), target_format)
            worksheet.write(row, 8, mapping.get('target_field', ''), target_format)
        
        # Adjust column widths
        for col in range(9):
            worksheet.set_column(col, col, 20)
    
    workbook.close()
    output.seek(0)
    return output.getvalue()

def generate_information_excel_report(mappings):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'fg_color': '#4472C4',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    source_format = workbook.add_format({
        'fg_color': '#D5E4BC',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    transform_format = workbook.add_format({
        'fg_color': '#9BC2E6',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    target_format = workbook.add_format({
        'fg_color': '#D1C4E9',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    # Group mappings by target table
    tables = defaultdict(list)
    for mapping in mappings:
        tables[mapping['target_table']].append(mapping)
    
    # Create a worksheet for each table
    for table_name, table_mappings in tables.items():
        # Clean table name for sheet name (Excel has restrictions)
        sheet_name = table_name[:31]  # Excel sheet names max 31 chars
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Headers
        headers = ['Database', 'Schema', 'Table Name', 'Field Name', 'Transformation Logic', 
                  'Database', 'Schema', 'Table Name', 'Column Name']
        
        # Add table info at the top
        worksheet.merge_range('A1:I1', f'Information Layer - {table_name}', header_format)
        worksheet.write('A2', f'Total Fields: {len(table_mappings)}', header_format)
        
        # Write section headers
        worksheet.merge_range('A3:D3', 'SOURCE (Foundation)', header_format)
        worksheet.merge_range('E3:E3', 'TRANSFORMATION', header_format) 
        worksheet.merge_range('F3:I3', 'TARGET (Information)', header_format)
        
        # Write column headers
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, header_format)
        
        # Write data
        for row, mapping in enumerate(table_mappings, start=4):
            # Source columns (Foundation)
            worksheet.write(row, 0, mapping.get('source_database', ''), source_format)
            worksheet.write(row, 1, mapping.get('source_schema', ''), source_format)
            worksheet.write(row, 2, mapping.get('source_table', ''), source_format)
            worksheet.write(row, 3, mapping.get('source_field', ''), source_format)
            
            # Transformation
            worksheet.write(row, 4, mapping.get('transformation_logic', ''), transform_format)
            
            # Target columns (Information)
            worksheet.write(row, 5, mapping.get('target_database', ''), target_format)
            worksheet.write(row, 6, mapping.get('target_schema', ''), target_format)
            worksheet.write(row, 7, mapping.get('target_table', ''), target_format)
            worksheet.write(row, 8, mapping.get('target_field', ''), target_format)
        
        # Adjust column widths
        for col in range(9):
            worksheet.set_column(col, col, 20)
    
    workbook.close()
    output.seek(0)
    return output.getvalue()

if __name__ == "__main__":
    main()