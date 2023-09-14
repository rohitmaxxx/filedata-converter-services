from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import json, csv
import os, glob



def feedbackInPages(label, feedbacks, max_size=2000):
    feedbacks_with_page = []
    current_fb = label
    for fb in feedbacks:
      if len(current_fb) <= max_size:
          current_fb += f'<br/><br/>{fb}'
      else:
          feedbacks_with_page.append(current_fb)
          current_fb = label + f'<br/><br/>{fb}'
    
    feedbacks_with_page.append(current_fb)
    print(">>>>>>>>>>>> feedback : ", feedbacks_with_page, feedbacks)
    return feedbacks_with_page
        
    

def createFeedback(data, bank_name):
    label = data.get('label', '')
    columns = data.get('columns', [])
    values = data.get('values', [])
    col_len = len(columns)

    feedbacks = []
    for i in range(col_len):
      for j in range(i+1, col_len):
        cols = [columns[i], columns[j]]
        new_values = [[val[i], val[j]] for val in values]
        # Feedback for 2 columns
        # Format: If {h1} is {row1} then {h2} will be {row2} in {bank_name} bank
        for val in values:
            # feedback = f"If '{columns[i]}' is '{val[i]}' then '{columns[j]}' will be '{val[j]}' in {bank_name} bank."
            feedback = f"'{val[i]}' of '{columns[i]}' is '{val[j]}' for '{columns[j]}' in {bank_name} bank."
            feedbacks.append(feedback)
            
        table = {
            'label':  label,
            'columns': cols,
            'values': new_values
        }


    arranges_fb = feedbackInPages(label, feedbacks)
    return arranges_fb


def createFeedback2(data, bank_name):
    label = data.get('label', '')
    columns = data.get('columns', [])
    values = data.get('values', [])
    col_len = len(columns)

    feedbacks = []
    for i in range(1, col_len):
      # Feedback for 2 columns
      # Format: If {h1} is {row1} then {h2} will be {row2} in {bank_name} bank
      for val in values:
          # feedback = f"If '{columns[i]}' is '{val[i]}' then '{columns[j]}' will be '{val[j]}' in {bank_name} bank."
          # feedback = f"If '{columns[0]}' is '{val[0]}' then '{columns[i]}' will be '{val[i]}' in {bank_name} bank."
          feedback = f"'{val[0]}' of '{columns[0]}' is '{val[i]}' for '{columns[i]}' in {bank_name} bank."
          feedbacks.append(feedback)
          

    arranges_fb = feedbackInPages(label, feedbacks)
    print(">>>>>>>>> feedbacks", arranges_fb)
    return arranges_fb



def createTableCombinations(data):
    label = data.get('label', '')
    columns = data.get('columns', [])
    values = data.get('values', [])
    col_len = len(columns)
    tables = []
    c = 1
    for i in range(col_len):
        for j in range(i+1, col_len):
            cols = [columns[i], columns[j]]
            new_values = [[val[i], val[j]] for val in values]

            table = {
                'label':  label,
                'columns': cols,
                'values': new_values
            }
            c += 1
            splitted_jsons = split_json(table)
            tables.extend(splitted_jsons)
            # tables.append(table)

    return tables


def split_json(data, max_size=4000):        
    label = data.get('label', '')
    columns = data.get('columns', [])
    values = data.get('values', [])

    new_values = []
    current_row = []

    for row in values:
        row_str = json.dumps(row)
        # print("========== : ro: ", row)
        json_size = len(json.dumps({'label': label, 'columns': columns, 'values': current_row}, ensure_ascii=False, separators=(',', ':'))) + len(row_str)
        # print("========== : size: ", json_size, max_size)
        if json_size <= max_size:
            current_row.append(row)
        else:
            new_values.append(current_row)
            current_row = [row]

    if current_row:
        new_values.append(current_row)

    if not new_values:
        return []

    new_jsons = []
    for i, rows in enumerate(new_values):
        new_json = {'label': label, 'columns': columns, 'values': rows}
        # new_json_str = json.dumps(new_json, ensure_ascii=False, separators=(',', ':'))
        new_jsons.append(new_json)

    return new_jsons



def write_pdf(filename, text_list, is_json=True):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    story = []  # List to hold the content for each page

    for text in text_list:
      # print("================== text: ", text)
      if is_json:
        label = text.pop('label')
        text = f'{label} \nTable: <br/> {str(text)}'
      # text = text.replace("'values':", "<br/><br/>'values':")
      paragraph = Paragraph(text, style=styles["Normal"])
      story.append(paragraph)
      story.append(PageBreak())  # Add a page break after each paragraph

    # Build the PDF with the content for each page
    doc.build(story)



def read_csv_tables(filename):
    tables = []
    current_table = None
    curent_tbl_col_count = 0
    current_idx = 0
    current_label = ''
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not any(row):
                current_idx += 1
                if current_table is not None:
                    splitted_jsons = split_json(current_table)
                    # splitted_jsons = createTableCombinations(current_table)
                    tables.extend(splitted_jsons)
                    current_table = None
            elif 'page' in (row[0]).lower():
                current_label = row[0]
            else:
                if current_table is None:
                    current_idx = 0
                    cols = [_ for _ in row if _]
                    curent_tbl_col_count = len(cols)
                    current_table = { 'label': current_label, 'columns': cols, 'values': []}
                    current_label = ''
                else:
                    current_table['values'].append(row[:curent_tbl_col_count])
        if current_table is not None:
            splitted_jsons = split_json(current_table)
            tables.extend(splitted_jsons)
    return tables


def creatFeedbackPdfFronJson(json_data, bank_name, out_filename):
    feedbackInPages_all = []
    for data in json_data:
      feedbackInPages = createFeedback2(data, bank_name)
      feedbackInPages_all.extend(feedbackInPages)
      # print("==========:1", len(feedbackInPages_all))
    # print("==========: ", feedbackInPages_all, len(feedbackInPages_all))
    write_pdf('feedback_' + out_filename, feedbackInPages_all, is_json=False)


def gereratePdfs():
  csv_folder_path = 'tables_csv'
  json_folder_path = 'tables_json'
  files = glob.glob(f'{csv_folder_path}/*.csv')
  for file in files:
      out_filename = file.split('/')[1].replace('.csv', '.pdf')
      out_filename = f'{json_folder_path}/json_{out_filename}'
      extracted_tables = read_csv_tables(file)
      write_pdf(out_filename, extracted_tables)
      print('Pdf done for: ', out_filename)


def gererateSinglePdfs(filepath):
    out_filename = filepath.replace('.csv', '_json.pdf')
    extracted_tables = read_csv_tables(filepath)
    write_pdf(out_filename, extracted_tables)
    print('Pdf done for: ', out_filename)

    return out_filename


# gereratePdfs()
# Example usage
# csv_filename = 'westpack.csv'
# bank_name = 'cba'
# csv_filename = f'{bank_name}.csv'
# extracted_tables = read_csv_tables(csv_filename)


# write_pdf(out_filename, extracted_tables, is_json=True)
# creatFeedbackPdfFronJson(extracted_tables, bank_name, out_filename)

example_json = {
    "label": "Page 17",
    "columns": [
      "Purpose\n (Yes- Evidence Required\n No-No Evidence is Required)",
      "Cash out amount less than\n $50,000 (PAYG Applicants)",
      "Cash out amount more than\n $50,000 (PAYG Applicants)",
      "Increase is more than\n $50,000 and customer had prior cash out in past 12 months (PAYG Applicants)",
      "Cash out amount less than\n $50,000 (Self-Employed Applicants)",
      "Cash out amount more than\n $50,000 (Self-Employed Applicants)",
      "Increase is more than\n $50,000 and customer\n had prior cash out in past 12 months (Self-Employed Applicants)"
    ],
    "values": [
      [
        "ANZLMI applications",
        "No",
        "Yes",
        "Yes",
        "Yes",
        "Yes",
        "Yes"
      ],
      [
        "Personal investment (share purchase)",
        "No",
        "No",
        "Yes",
        "No",
        "Yes",
        "Yes"
      ],
      [
        "Renovations/home  improvements",
        "No",
        "No",
        "Yes",
        "No",
        "Yes",
        "Yes"
      ],
      [
        "Personal use (travel, wedding, etc)",
        "No",
        "No",
        "Yes",
        "No",
        "Yes",
        "Yes"
      ],
      [
        "Motor Vehicle",
        "No",
        "No",
        "Yes",
        "No",
        "Yes",
        "Yes"
      ],
      [
        "Deposit on Property",
        "No",
        "No",
        "Yes",
        "No",
        "Yes",
        "Yes"
      ],
      [
        "Purchase of Property",
        "No",
        "No",
        "Yes",
        "No",
        "Yes",
        "Yes"
      ]
    ]
  }

# createTableCombinations(example_json)