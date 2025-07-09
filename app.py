import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF


# --- Helper Functions ---
def calculate_amount(quantity, rate):
    try:
        return quantity * float(rate)
    except ValueError:
        return 0.0

def calculate_grand_total(invoice_items_df):
    return invoice_items_df['Amount'].sum()

# --- PDF Generation Function ---
def create_invoice_pdf(company_details, customer_details, invoice_items_df, grand_total):
    # pdf = FPDF()
    # pdf.add_page()


    class PDFWithBackground(FPDF):
        def header(self):
            # Apply the background image on every page
            self.image("pdfbg3.jpg", x=0, y=0, w=210, h=297)

    pdf = PDFWithBackground()
    pdf.add_page()

    LIGHT_GREEN = (220, 240, 220)
    DARK_GREEN = (34, 139, 34)
    BLACK = (0, 0, 0)

    pdf.set_font("Arial", size=10)
    pdf.set_text_color(*BLACK)

    # Company Details
    pdf.set_fill_color(*LIGHT_GREEN)
    pdf.set_text_color(*DARK_GREEN)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, company_details['name'], ln=True, align="R", fill=True)

    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 3, company_details['address'], align="R")
    if company_details['phone']:
        pdf.cell(0, 4.5, f"Phone: {company_details['phone']}", ln=True, align="R")
    if company_details['email']:
        pdf.cell(0, 4.5, f"Email: {company_details['email']}", ln=True, align="R")
    if company_details['gstin']:
        pdf.cell(0, 4.5, f"GSTIN: {company_details['gstin']}", ln=True, align="R")
    pdf.ln(10)

    # Invoice Title
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(0, 15, "QUOTATION / BILL", ln=True, align="C")
    
    # Horizontal line under title
    pdf.set_draw_color(0, 0, 0)  
    pdf.set_line_width(0.1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Draw line from left to right margin

    pdf.ln(5)

    # Date
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, f"Date: {date.today().strftime('%Y-%m-%d')}", ln=True, align="R")
    pdf.ln(5)

    # Customer Details
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(0, 10, "Bill To:", ln=True)
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 5, customer_details['name'], ln=True)
    pdf.cell(0, 5, customer_details['address'], ln=True)
    if customer_details['phone']:
        pdf.cell(0, 5, f"Phone: {customer_details['phone']}", ln=True)
    if customer_details['email']:
        pdf.cell(0, 5, f"Email: {customer_details['email']}", ln=True)
    if customer_details['gstin']:
        pdf.cell(0, 5, f"GSTIN: {customer_details['gstin']}", ln=True)
    pdf.ln(10)
    

    # Invoice Items Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(*BLACK)
    pdf.set_fill_color(*LIGHT_GREEN)
    col_widths = [15, 80, 25, 25, 25]  # Sr No, Description, Qty, Rate, Amount
    pdf.cell(col_widths[0], 10, "Sr No.", 1, 0, 'C', fill=True)
    pdf.cell(col_widths[1], 10, "Description", 1, 0, 'C', fill=True)
    pdf.cell(col_widths[2], 10, "Qty", 1, 0, 'C', fill=True)
    pdf.cell(col_widths[3], 10, "Rate", 1, 0, 'C', fill=True)
    pdf.cell(col_widths[4], 10, "Amount", 1, 1, 'C', fill=True)

    # Invoice Items Rows
    pdf.set_font("Arial", size=10)
    for index, row in invoice_items_df.iterrows():
        if index % 2 == 0:
            pdf.set_fill_color(245, 255, 245)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(col_widths[0], 10, str(row["Sr No."]), 1, 0, 'C', fill=True)
        pdf.cell(col_widths[1], 10, str(row["Description"]), 1, 0, 'L', fill=True)
        pdf.cell(col_widths[2], 10, str(row["Quantity"]), 1, 0, 'C', fill=True)
        pdf.cell(col_widths[3], 10, f"{row['Rate']:,.2f}", 1, 0, 'R', fill=True)
        pdf.cell(col_widths[4], 10, f"{row['Amount']:,.2f}", 1, 1, 'R', fill=True)

    # Grand Total
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*DARK_GREEN)
    pdf.set_fill_color(*LIGHT_GREEN)
    pdf.cell(sum(col_widths[:-1]), 10, "Grand Total:", 1, 0, 'R', fill=True)
    pdf.cell(col_widths[-1], 10, f"{grand_total:,.2f}", 1, 1, 'R', fill=True)

    


    #Bank Details
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(*DARK_GREEN)
    pdf.cell(0, 10, "Bank Details:", ln=True)
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", size=10)
    if bank_details['bank']:
        pdf.cell(0, 5, f"Bank Name: {bank_details['bank']}", ln=True)
    if bank_details['ac_no']:
        pdf.cell(0, 5, f"Current A/C No.: {bank_details['ac_no']}", ln=True)
    if bank_details['ifsc']:
        pdf.cell(0, 5, f"IFSC: {bank_details['ifsc']}", ln=True)
    pdf.ln(10)

    #Thank you message
    pdf.ln(10)
    pdf.set_text_color(*BLACK)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Thank you for your business!", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin1')

# --- Streamlit App ---
st.set_page_config(page_title="Samarth Traders", layout="centered",page_icon='🛠️')

st.title(":rainbow[SAMARTH TRADERS]")
st.divider()

# Company Details
st.header(":rainbow[Company Details]",divider="rainbow")
company_name = st.text_input("Company Name","SAMARTH TRADERS" )
company_address = st.text_area("Company Address", "\n\n Dealer of All Types of Plumbing \n\n A.P.V.C,C.P.V.C,P.V.C,S.W.R & C.P. Fittings \n\n Nivara Models building.Pinguli Titha,Pinguli \n\n Nerur road ,Tal.-Kudal,Dist.-Sindhudurg,Maharashtra-416520")
company_phone = st.text_input("Company Phone", "+91 ")
company_email = st.text_input("Company Email", "")
company_gstin = st.text_input("Company GSTIN (Optional)", "")

st.markdown("---")

# Customer Details
st.header(":rainbow[Customer Details]",divider='rainbow')
customer_name = st.text_input("Customer Name", "")
customer_address = st.text_area("Customer Address", "")
customer_phone = st.text_input("Customer Phone", "")
customer_email = st.text_input("Customer Email(Optional)", "")
customer_gstin = st.text_input("Customer GSTIN (Optional)", "")

st.markdown("---")

# Bank Details
st.header(":rainbow[Bank Details]",divider='rainbow')
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
st.header(":rainbow[Invoice Items]",divider='rainbow')

if 'invoice_items' not in st.session_state:
    st.session_state.invoice_items = []

# Add new item form with dropdown instead of text input for description
with st.form("new_item_form", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
    with col1:
        product_choice = st.selectbox("Select Product", options= ["Other"]+product_list , key="new_desc")
        if product_choice == "Other":
            custom_product = st.text_input("Enter custom product name", key="custom_product")
            description = custom_product.strip()
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
                "Rate": rate,
                "Amount": amount
            })
        else:
            st.warning("Please enter valid Quantity (> 0) and Rate (>= 0).")

# Display invoice items DataFrame
invoice_df = pd.DataFrame()
if st.session_state.invoice_items:
    invoice_df = pd.DataFrame(st.session_state.invoice_items)
    
    # Delete row buttons — one per item
    st.write("### Invoice Items Table")
    for i, row in invoice_df.iterrows():
        cols = st.columns([1, 5, 1])
        with cols[0]:
            st.write(row["Sr No."])
        with cols[1]:
            st.write(row["Description"])
        with cols[2]:
            # Delete button with unique key per row
            if st.button("❌", key=f"delete_{row['Sr No.']}"):
                st.session_state.invoice_items.pop(i)
                # Reassign Sr No.
                for idx, item in enumerate(st.session_state.invoice_items):
                    item["Sr No."] = idx + 1
                st.rerun()

    st.dataframe(invoice_df.set_index('Sr No.'))

    # Grand total display
    grand_total = calculate_grand_total(invoice_df)
    st.subheader(f"Grand Total: ₹ {grand_total:,.2f}")

    if st.button("Clear All Items", key="clear_all"):
        st.session_state.invoice_items = []
        st.rerun()
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
        "gstin": company_gstin
    }
    customer_details = {
        "name": customer_name,
        "address": customer_address,
        "phone": customer_phone,
        "email": customer_email,
        "gstin": customer_gstin
    }
    bank_details ={
        "bank":bank_name,
        "ac_no":account_no,
        "ifsc":ifsc_code
    }

    pdf_output_bytes = create_invoice_pdf(company_details, customer_details, invoice_df, grand_total)

    st.download_button(
        label="Download Invoice PDF",
        data=pdf_output_bytes,
        file_name=f"invoice_{date.today().strftime('%Y%m%d')}_{customer_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

    st.success("PDF generated successfully! Click the button above to download.")
else:
    st.warning("Add some invoice items to generate an invoice.")
