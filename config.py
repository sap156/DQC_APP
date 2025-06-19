from datetime import datetime

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
    "RULE_TRGT_SCHM_NM": ["APP_CFOPYMTS", "ENTERPRISE", "STRIPE", "PAYMENTS"],
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
