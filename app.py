from flask import Flask, render_template, request, jsonify, send_file
import csv
import io
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import atexit
import shutil

# Initialize the Flask application
app = Flask(__name__)

# Define the folder to store uploaded files
UPLOAD_FOLDER = "uploads"

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure the Flask app to use the upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to get the current timestamp in a specific format
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d 00:00:00:00")[:-3]

DEFAULT_VALUES = {
    "DATA_QC_ID": "23",
    "RULE_FREQ_CD": "DAILY",
    "RULE_SRC_ATTR_NM": "NA",
    "RULE_TRGT_ATTR_NM": "NA",
    "RULE_CDE_IND": "N",
    "RULE_EXP_DT": "9999–12–31",
    "ASSET_ID": "9999"
}

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

rows = []

@app.route('/')
def index():
    global rows
    rows = []
    return render_template('form.html', fields=FIELDS, rows=rows)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    global rows
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f, delimiter="~")
            rows = [dict((key, row.get(key, "")) for key in FIELDS.keys()) for row in csv_reader]
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return jsonify({"error": "Error reading CSV file"}), 500

    return jsonify(rows)

@app.route('/add_row', methods=['POST'])
def add_row():
    if request.is_json:
        form_data = request.json
    else:
        form_data = {field: request.form.get(field, "") for field in FIELDS.keys()}

    form_data["DATA_QC_ID"] = DEFAULT_VALUES["DATA_QC_ID"]
    form_data["RULE_FREQ_CD"] = DEFAULT_VALUES["RULE_FREQ_CD"]
    form_data["RULE_SRC_ATTR_NM"] = DEFAULT_VALUES["RULE_SRC_ATTR_NM"]
    form_data["RULE_CDE_IND"] = DEFAULT_VALUES["RULE_CDE_IND"]
    form_data["RULE_EXP_DT"] = DEFAULT_VALUES["RULE_EXP_DT"]
    form_data["RULE_EFF_DT"] = datetime.today().strftime("%Y-%m-%d")
    form_data["ASSET_ID"] = DEFAULT_VALUES["ASSET_ID"]
    form_data["ASSET_NM"] = form_data.get("APPL_CD", "")
    form_data["CREA_TS"] = get_current_timestamp()

    rows.append(form_data)
    return jsonify(rows)

@app.route('/update_row', methods=['POST'])
def update_row():
    data = request.json
    index = data.get("index")
    updated_row = data.get("updatedRow")

    if index is not None and 0 <= index < len(rows):
        rows[index] = updated_row

    return jsonify(rows)

@app.route('/delete_row', methods=['POST'])
def delete_row():
    data = request.json
    index = data.get("index")

    if index is not None and 0 <= index < len(rows):
        del rows[index]

    return jsonify(rows)

@app.route('/generate_csv')
def generate_csv():
    if not rows:
        return "No data available", 400

    appl_cd = rows[0]["APPL_CD"].replace(" ", "_")
    filename = f"DATA_QC_RULE_INFO_{appl_cd}.csv"

    output = io.StringIO()
    csv_writer = csv.writer(output, delimiter='~')

    csv_writer.writerow(FIELDS.keys())
    for row in rows:
        csv_writer.writerow([row[field] for field in FIELDS.keys()])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

# Cleanup function to truncate the uploads folder
def cleanup_upload_folder():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Reason: {e}")

atexit.register(cleanup_upload_folder)

if __name__ == '__main__':
    app.run(debug=True)