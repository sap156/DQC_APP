def generate_rule_name(rule_trgt_obj_id_txt, rule_valid_meth_cd, rule_trgt_db_nm, rule_trgt_data_layer_nm):
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
    if not rule_nm or rule_nm == "Enter a rule name (e.g. TABLE_NM_DL2_CNT_CHK)":
        return "Rule description will be auto-generated based on rule name"
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
    description = ""
    if "_OP_HOP3_CNT_CHK" in rule_nm or "_OP_HOP3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} on OnPrem Source Records (HOP3) table {rule_trgt_obj_id_txt}."
    elif "_OP_HOP2_CNT_CHK" in rule_nm or "_OP_HOP2_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} on OnPrem DS Records (HOP2) table {rule_trgt_obj_id_txt}."
    elif "_OP_HOP1_CNT_CHK" in rule_nm or "_OP_HOP1_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} on OnPrem CSV Records (HOP1) table {rule_trgt_obj_id_txt}."
    elif "_DL2_CNT_CHK" in rule_nm or "_DL2_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} on DL2 table {rule_trgt_obj_id_txt}."
    elif "_FND_DL3_CNT_CHK" in rule_nm or "_FND_DL3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} on foundation table {rule_trgt_obj_id_txt}."
    elif "_STG_DL3_CNT_CHK" in rule_nm or "_STG_DL3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} on staging DL3 table {rule_trgt_obj_id_txt}."
    elif "_INFO_DL3_CNT_CHK" in rule_nm or "_INFO_DL3_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} on information DL3 table {rule_trgt_obj_id_txt}."
    elif "_OP_HOP3_HOP2_DIFF_CNT_CHK" in rule_nm or "_OP_HOP3_HOP2_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between OnPrem Source Records (HOP3) and OnPrem DS Records (HOP2)"
    elif "_OP_HOP2_HOP1_DIFF_CNT_CHK" in rule_nm or "_OP_HOP2_HOP1_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between OnPrem DS Records (HOP2) and OnPrem CSV Records (HOP1)"
    elif "_OP_HOP1_DL2_DIFF_CNT_CHK" in rule_nm or "_OP_HOP1_DL2_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between OnPrem CSV Records (HOP1) and DL2 table"
    elif "_DL2_FND_DIFF_CNT_CHK" in rule_nm or "_DL2_FND_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between DL2 and foundation table {rule_trgt_obj_id_txt}."
    elif "_STG_INFO_DIFF_CNT_CHK" in rule_nm or "_STG_INFO_DIFF_SUM_CHK" in rule_nm:
        description = f"Performs {check_type} between staging table and information DL3 table {rule_trgt_obj_id_txt}."
    elif "_INFO_DL3_DUP_CHK" in rule_nm:
        description = f"Performs Duplicate check on information DL3 table {rule_trgt_obj_id_txt}."
    elif "_INFO_DL3_OVERLAP_CHK" in rule_nm:
        description = f"Performs Overlap check on information DL3 table {rule_trgt_obj_id_txt}."
    else:
        if rule_trgt_obj_id_txt and rule_trgt_obj_id_txt != "TARGET_TABLE":
            description = f"Performs {check_type} on table {rule_trgt_obj_id_txt}."
        else:
            description = f"Performs {check_type}."
    if description and not description[0].isupper():
        description = description[0].upper() + description[1:]
    return description

def update_all_auto_fields(st):
    abort_ind_values = ["DIFF_CNT_CHK", "DIFF_SUM_CHK", "DUP_CHK", "OVERLAP_CHK"]
    st.session_state.form_rule_abort_ind = "Y" if st.session_state.form_rule_valid_meth_cd in abort_ind_values else "N"
    if st.session_state.form_rule_valid_meth_cd in ["SUM_CHK", "DIFF_SUM_CHK"]:
        if st.session_state.form_rule_trgt_attr_nm == "NA":
            st.session_state.form_rule_trgt_attr_nm = ""
    else:
        st.session_state.form_rule_trgt_attr_nm = "NA"
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
    st.session_state.form_rule_dsc_txt = generate_rule_description(
        st.session_state.form_rule_nm,
        st.session_state.form_rule_valid_meth_cd,
        st.session_state.form_rule_trgt_attr_nm,
        st.session_state.form_rule_trgt_obj_id_txt
    )

def update_rule_name_only(st):
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
    st.session_state.form_rule_dsc_txt = generate_rule_description(
        st.session_state.form_rule_nm,
        st.session_state.form_rule_valid_meth_cd,
        st.session_state.form_rule_trgt_attr_nm,
        st.session_state.form_rule_trgt_obj_id_txt
    )

def update_database_based_on_layer(st):
    data_layer = st.session_state.form_rule_trgt_data_layer_nm
    if any(hop in data_layer for hop in ["HOP1", "HOP2", "HOP3", "OnPrem"]):
        st.session_state.form_rule_trgt_db_nm = "CFOPAYMENTSDB"
    update_rule_name_only(st)

def update_description_only(st):
    st.session_state.form_rule_dsc_txt = generate_rule_description(
        st.session_state.form_rule_nm,
        st.session_state.form_rule_valid_meth_cd,
        st.session_state.form_rule_trgt_attr_nm,
        st.session_state.form_rule_trgt_obj_id_txt
    )
