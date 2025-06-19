import re

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
