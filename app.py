import os
import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF

# --- Helper Functions ---
def calculate_amount(quantity, rate):
    try:
        return float(quantity) * float(rate)
    except (ValueError, TypeError):
        return 0.0

def calculate_grand_total(invoice_items_df):
    if invoice_items_df is None or invoice_items_df.empty:
        return 0.0
    try:
        return float(invoice_items_df['Amount'].astype(float).sum())
    except Exception:
        total = 0.0
        for v in invoice_items_df.get('Amount', []):
            try:
                total += float(v)
            except Exception:
                continue
        return total

# --- PDF Generation Function ---
def create_invoice_pdf(company_details, customer_details, bank_details, invoice_items_df, grand_total):
    class PDFWithBackground(FPDF):
        def header(self):
            bg_path = company_details.get("_background_path", "pdfbg6.jpg")
            logo_path = company_details.get("_logo_path", None)

            # Apply background image if exists
            if bg_path and os.path.exists(bg_path):
                try:
                    self.image(bg_path, x=0, y=0, w=210, h=297)
                except Exception:
                    pass

            # Add company logo (top-left corner)
            if logo_path and os.path.exists(logo_path):
                try:
                    self.image(logo_path, x=10, y=8, w=30)
                except Exception:
                    pass

    pdf = PDFWithBackground()
    pdf.add_page()

    LIGHT_GREEN = (220, 240, 220)
    DARK_GREEN = (34, 139, 34)
    BLACK = (0, 0, 0)

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*BLACK)

    # Company Details
    pdf.set_fill_color(*LIGHT_GREEN)
    pdf.set_text_color(*DARK_GREEN)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, str(company_details.get('name', '') or ""), ln=True, align="R", fill=True)

    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    address = company_details.get('address', '') or ""
    if address:
        pdf.multi_cell(0, 5, address, align="R")
    if company_details.get('phone'):
        pdf.cell(0, 5, f"Phone: {company_details.get('phone')}", ln=True, align="R")
    if company_details.get('email'):
        pdf.cell(0, 5, f"Email: {company_details.get('email')}", ln=True, align="R")
    if company_details.get('gstin'):
        pdf.cell(0, 5, f"GSTIN: {company_details.get('gstin')}", ln=True, align="R")
    pdf.ln(6)

    # Title
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(0, 15, "QUOTATION / BILL", ln=True, align="C")
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.1)
    y_after_title = pdf.get_y()
    pdf.line(10, y_after_title, 200, y_after_title)
    pdf.ln(6)

    # Date
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"Date: {date.today().strftime('%Y-%m-%d')}", ln=True, align="R")
    pdf.ln(4)

    # Customer Details
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(0, 8, "Bill To:", ln=True)
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    if customer_details.get('name'):
        pdf.cell(0, 5, customer_details.get('name'), ln=True)
    if customer_details.get('address'):
        pdf.multi_cell(0, 5, customer_details.get('address'))
    if customer_details.get('phone'):
        pdf.cell(0, 5, f"Phone: {customer_details.get('phone')}", ln=True)
    if customer_details.get('email'):
        pdf.cell(0, 5, f"Email: {customer_details.get('email')}", ln=True)
    if customer_details.get('gstin'):
        pdf.cell(0, 5, f"GSTIN: {customer_details.get('gstin')}", ln=True)
    pdf.ln(8)

    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(*BLACK)
    pdf.set_fill_color(*LIGHT_GREEN)
    col_widths = [15, 95, 20, 30, 30]
    headers = ["Sr No.", "Description", "Qty", "Rate", "Amount"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 10, h, 1, 0, 'C', fill=True)
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", size=10)
    if not invoice_items_df.empty:
        for idx, row in invoice_items_df.iterrows():
            pdf.set_fill_color(245, 255, 245) if idx % 2 == 0 else pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_widths[0], 10, str(row["Sr No."]), 1, 0, 'C', fill=True)
            pdf.cell(col_widths[1], 10, str(row["Description"]), 1, 0, 'L', fill=True)
            pdf.cell(col_widths[2], 10, str(row["Quantity"]), 1, 0, 'C', fill=True)
            pdf.cell(col_widths[3], 10, f"{row['Rate']:,.2f}", 1, 0, 'R', fill=True)
            pdf.cell(col_widths[4], 10, f"{row['Amount']:,.2f}", 1, 1, 'R', fill=True)
    else:
        pdf.cell(sum(col_widths), 10, "No items added", 1, 1, 'C')

    # Grand Total
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*DARK_GREEN)
    pdf.set_fill_color(*LIGHT_GREEN)
    pdf.cell(sum(col_widths[:-1]), 10, "Grand Total:", 1, 0, 'R', fill=True)
    pdf.cell(col_widths[-1], 10, f"{grand_total:,.2f}", 1, 1, 'R', fill=True)
    pdf.ln(8)

    # Bank Details
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(0, 8, "Bank Details:", ln=True)
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    if bank_details.get('bank'):
        pdf.cell(0, 5, f"Bank Name: {bank_details.get('bank')}", ln=True)
    if bank_details.get('ac_no'):
        pdf.cell(0, 5, f"Current A/C No.: {bank_details.get('ac_no')}", ln=True)
    if bank_details.get('ifsc'):
        pdf.cell(0, 5, f"IFSC: {bank_details.get('ifsc')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Thank you for your business!", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')


# --- Streamlit UI ---
st.set_page_config(page_title="Samarth Traders", layout="centered", page_icon="🛠️")
st.title(":rainbow[SAMARTH TRADERS]")
st.divider()

# Company Details + Logo Upload
st.header(":rainbow[Company Details]")
company_name = st.text_input("Company Name", "SAMARTH TRADERS")
company_address = st.text_area("Company Address", "Dealer of Plumbing Materials\nPinguli, Kudal, Maharashtra-416520")
company_phone = st.text_input("Company Phone", "+91 ")
company_email = st.text_input("Company Email", "")
company_gstin = st.text_input("Company GSTIN (Optional)", "")
company_logo = st.file_uploader("Upload Company Logo (Optional)", type=["png", "jpg", "jpeg"])

logo_path = None
if company_logo:
    logo_path = os.path.join("temp_logo." + company_logo.name.split('.')[-1])
    with open(logo_path, "wb") as f:
        f.write(company_logo.getbuffer())

st.markdown("---")

# Customer Details
st.header(":rainbow[Customer Details]")
customer_name = st.text_input("Customer Name", "")
customer_address = st.text_area("Customer Address", "")
customer_phone = st.text_input("Customer Phone", "")
customer_email = st.text_input("Customer Email (Optional)", "")
customer_gstin = st.text_input("Customer GSTIN (Optional)", "")

st.markdown("---")

# Bank Details
st.header(":rainbow[Bank Details]")
bank_name = st.text_input("Bank Name", "")
account_no = st.text_input("Account Number", "")
ifsc_code = st.text_input("IFSC Code", "")

# Product List
product_list = ["Product A", "Product B", "Product C", "Product D", "Product E"]

# Invoice Items Section
st.header(":rainbow[Invoice Items]")
if 'invoice_items' not in st.session_state:
    st.session_state.invoice_items = []

with st.form("new_item_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col1:
        product_choice = st.selectbox("Select Product", ["Other"] + product_list)
        description = st.text_input("Enter custom product name") if product_choice == "Other" else product_choice
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
    with col3:
        rate = st.number_input("Rate", min_value=0.0, value=0.0, step=10.0)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        add_item_button = st.form_submit_button("Add Item")

    if add_item_button:
        amount = calculate_amount(quantity, rate)
        st.session_state.invoice_items.append({
            "Sr No.": len(st.session_state.invoice_items) + 1,
            "Description": description,
            "Quantity": quantity,
            "Rate": rate,
            "Amount": amount
        })
        st.rerun()

invoice_df = pd.DataFrame(st.session_state.invoice_items)
if not invoice_df.empty:
    st.dataframe(invoice_df.set_index("Sr No."))
    grand_total = calculate_grand_total(invoice_df)
    st.subheader(f"Grand Total: ₹ {grand_total:,.2f}")

    if st.button("Clear All Items"):
        st.session_state.invoice_items = []
        st.rerun()
else:
    grand_total = 0.0
    st.info("No items added yet.")

st.markdown("---")

# Generate Invoice PDF
if not invoice_df.empty:
    company_details = {
        "name": company_name,
        "address": company_address,
        "phone": company_phone,
        "email": company_email,
        "gstin": company_gstin,
        "_background_path": "pdfbg6.jpg",
        "_logo_path": logo_path
    }
    customer_details = {
        "name": customer_name,
        "address": customer_address,
        "phone": customer_phone,
        "email": customer_email,
        "gstin": customer_gstin
    }
    bank_details = {"bank": bank_name, "ac_no": account_no, "ifsc": ifsc_code}

    pdf_output_bytes = create_invoice_pdf(company_details, customer_details, bank_details, invoice_df, grand_total)

    st.download_button(
        label="Download Invoice PDF",
        data=pdf_output_bytes,
        file_name=f"invoice_{date.today().strftime('%Y%m%d')}_{customer_name or 'customer'}.pdf",
        mime="application/pdf"
    )
    st.success("✅ PDF generated successfully! Click the button above to download.")
else:
    st.warning("Add items before generating an invoice.")