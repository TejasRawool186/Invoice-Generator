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
    # Ensure numeric
    try:
        return float(invoice_items_df['Amount'].astype(float).sum())
    except Exception:
        # fallback: sum manually
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
            # Apply the background image on every page only if exists
            if bg_path and os.path.exists(bg_path):
                # Fit to A4 (210x297 mm)
                try:
                    self.image(bg_path, x=0, y=0, w=210, h=297)
                except Exception:
                    # ignore if image can't be placed
                    pass

    pdf = PDFWithBackground()
    pdf.add_page()

    # Colors
    LIGHT_GREEN = (220, 240, 220)
    DARK_GREEN = (34, 139, 34)
    BLACK = (0, 0, 0)

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*BLACK)

    # Company Details (right-aligned)
    pdf.set_fill_color(*LIGHT_GREEN)
    pdf.set_text_color(*DARK_GREEN)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, str(company_details.get('name', '') or ""), ln=True, align="R", fill=True)

    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    address = company_details.get('address', '') or ""
    if address:
        # Use multi_cell to allow wrapping; align right by computing a small trick
        # (FPDF multi_cell doesn't support right alignment directly for the whole page,
        # so we'll just place it normally.)
        pdf.multi_cell(0, 5, address, align="R")
    if company_details.get('phone'):
        pdf.cell(0, 5, f"Phone: {company_details.get('phone')}", ln=True, align="R")
    if company_details.get('email'):
        pdf.cell(0, 5, f"Email: {company_details.get('email')}", ln=True, align="R")
    if company_details.get('gstin'):
        pdf.cell(0, 5, f"GSTIN: {company_details.get('gstin')}", ln=True, align="R")
    pdf.ln(6)

    # Invoice Title
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(0, 15, "QUOTATION / BILL", ln=True, align="C")

    # Horizontal line under title
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.1)
    y_after_title = pdf.get_y()
    pdf.line(10, y_after_title, 200, y_after_title)

    pdf.ln(6)

    # Date
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    today_str = date.today().strftime('%Y-%m-%d')
    pdf.cell(0, 7, f"Date: {today_str}", ln=True, align="R")
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

    # Invoice Items Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(*BLACK)
    pdf.set_fill_color(*LIGHT_GREEN)
    col_widths = [15, 95, 20, 30, 30]  # widened description area
    headers = ["Sr No.", "Description", "Qty", "Rate", "Amount"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 10, h, 1, 0, 'C', fill=True)
    pdf.ln()

    # Invoice Items Rows
    pdf.set_font("Arial", size=10)
    if invoice_items_df is not None and not invoice_items_df.empty:
        for idx, row in invoice_items_df.iterrows():
            # alternating fill
            if idx % 2 == 0:
                pdf.set_fill_color(245, 255, 245)
            else:
                pdf.set_fill_color(255, 255, 255)

            # Read values safely
            sr = str(row.get("Sr No.", idx + 1)) if isinstance(row, dict) else str(row.get("Sr No.") if "Sr No." in row else (idx + 1))
            desc = str(row.get("Description", "")) if isinstance(row, dict) else str(row["Description"])
            qty = str(row.get("Quantity", "")) if isinstance(row, dict) else str(row["Quantity"])
            try:
                rate_val = float(row.get("Rate", 0)) if isinstance(row, dict) else float(row["Rate"])
            except Exception:
                rate_val = 0.0
            try:
                amount_val = float(row.get("Amount", 0)) if isinstance(row, dict) else float(row["Amount"])
            except Exception:
                amount_val = rate_val * float(qty) if qty else 0.0

            # Cells
            pdf.cell(col_widths[0], 10, sr, 1, 0, 'C', fill=True)
            # For long description, use multi_cell trick: create a cell then move back up if needed.
            x_before = pdf.get_x()
            y_before = pdf.get_y()
            pdf.multi_cell(col_widths[1], 6, desc, 1, 'L', fill=True)
            # move cursor to the right for the remaining columns on the same line as the first multi_cell line
            x_after = pdf.get_x()
            y_after = pdf.get_y()
            # After multi_cell, we are at start of next line. So set x to right edge of description column for qty/rate/amount
            pdf.set_xy(10 + sum(col_widths[:2]), y_before)  # left margin(10) + first two widths
            pdf.cell(col_widths[2], 10, str(qty), 1, 0, 'C', fill=True)
            pdf.cell(col_widths[3], 10, f"{rate_val:,.2f}", 1, 0, 'R', fill=True)
            pdf.cell(col_widths[4], 10, f"{amount_val:,.2f}", 1, 1, 'R', fill=True)
    else:
        # No rows
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

    # Thank you
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Thank you for your business!", 0, 1, 'C')

    # Return PDF bytes
    return pdf.output(dest='S').encode('latin-1')


# --- Streamlit App ---
st.set_page_config(page_title="Samarth Traders", layout="centered", page_icon="🛠️")

st.title(":rainbow[SAMARTH TRADERS]")
st.divider()

# Company Details
st.header(":rainbow[Company Details]")
company_name = st.text_input("Company Name", "SAMARTH TRADERS")
company_address = st.text_area(
    "Company Address",
    "Dealer of All Types of Plumbing\nA.P.V.C, C.P.V.C, P.V.C, S.W.R & C.P. Fittings\nNivara Models building, Pinguli Titha, Pinguli\nNerur road, Tal.-Kudal, Dist.-Sindhudurg, Maharashtra-416520"
)
company_phone = st.text_input("Company Phone", "+91 ")
company_email = st.text_input("Company Email", "")
company_gstin = st.text_input("Company GSTIN (Optional)", "")

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

# Predefined product list for dropdown
product_list = [
    "Product A",
    "Product B",
    "Product C",
    "Product D",
    "Product E",
]

# Invoice Items
st.header(":rainbow[Invoice Items]")

if 'invoice_items' not in st.session_state:
    st.session_state.invoice_items = []

# Add new item form with dropdown instead of free text
with st.form("new_item_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col1:
        product_choice = st.selectbox("Select Product", options=["Other"] + product_list, key="new_desc")
        if product_choice == "Other":
            custom_product = st.text_input("Enter custom product name", key="custom_product")
            description = (custom_product or "").strip()
        else:
            description = product_choice
    with col2:
        quantity = st.number_input("Quantity", min_value=0, value=1, step=1, key="new_qty")
    with col3:
        rate = st.number_input("Rate", min_value=0.0, value=0.0, step=10.0, key="new_rate")
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        add_item_button = st.form_submit_button("Add Item")

    if add_item_button:
        if description and quantity > 0 and rate >= 0:
            amount = calculate_amount(quantity, rate)
            st.session_state.invoice_items.append({
                "Sr No.": len(st.session_state.invoice_items) + 1,
                "Description": description,
                "Quantity": quantity,
                "Rate": float(rate),
                "Amount": float(amount)
            })
            st.success("Item added.")
            st.experimental_rerun()
        else:
            st.warning("Please enter valid Description, Quantity (> 0) and Rate (>= 0).")

# Display invoice items DataFrame
invoice_df = pd.DataFrame(st.session_state.invoice_items) if st.session_state.invoice_items else pd.DataFrame()

if not invoice_df.empty:
    st.write("### Invoice Items Table")
    # Show rows with delete buttons
    for i, row in invoice_df.iterrows():
        cols = st.columns([1, 6, 1])
        with cols[0]:
            st.write(row["Sr No."])
        with cols[1]:
            st.write(row["Description"])
        with cols[2]:
            if st.button("❌", key=f"delete_{int(row['Sr No.'])}"):
                # remove that index from session_state list
                st.session_state.invoice_items.pop(i)
                # reassign Sr No.
                for idx2, it in enumerate(st.session_state.invoice_items):
                    it["Sr No."] = idx2 + 1
                st.experimental_rerun()

    st.dataframe(invoice_df.set_index('Sr No.'))

    # Grand total display
    grand_total = calculate_grand_total(invoice_df)
    st.subheader(f"Grand Total: ₹ {grand_total:,.2f}")

    if st.button("Clear All Items", key="clear_all"):
        st.session_state.invoice_items = []
        st.experimental_rerun()
else:
    st.info("No invoice items added yet. Use the form above to add items.")
    grand_total = 0.0

st.markdown("---")

# Generate invoice PDF
st.header("Generate Invoice")
if st.session_state.invoice_items:
    company_details = {
        "name": company_name,
        "address": company_address,
        "phone": company_phone,
        "email": company_email,
        "gstin": company_gstin,
        # optional: if you want a custom path for a background file, add "_background_path"
        "_background_path": "pdfbg6.jpg"
    }
    customer_details = {
        "name": customer_name,
        "address": customer_address,
        "phone": customer_phone,
        "email": customer_email,
        "gstin": customer_gstin
    }
    bank_details = {
        "bank": bank_name,
        "ac_no": account_no,
        "ifsc": ifsc_code
    }

    invoice_df = pd.DataFrame(st.session_state.invoice_items)  # ensure DataFrame
    # ensure numeric types
    invoice_df['Rate'] = invoice_df['Rate'].astype(float)
    invoice_df['Amount'] = invoice_df['Amount'].astype(float)

    grand_total = calculate_grand_total(invoice_df)
    try:
        pdf_output_bytes = create_invoice_pdf(company_details, customer_details, bank_details, invoice_df, grand_total)
        # safe filename
        safe_customer = (customer_name.strip().replace(" ", "_") or "customer")
        filename = f"invoice_{date.today().strftime('%Y%m%d')}_{safe_customer}.pdf"
        st.download_button(
            label="Download Invoice PDF",
            data=pdf_output_bytes,
            file_name=filename,
            mime="application/pdf"
        )
        st.success("PDF generated successfully! Click the button above to download.")
    except Exception as e:
        st.error(f"Failed to generate PDF: {e}")
else:
    st.warning("Add some invoice items to generate an invoice.")