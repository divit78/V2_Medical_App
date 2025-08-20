import streamlit as st
from datetime import datetime, date
import os
from utils.file_ops import load_json, save_json
from config.constants import MEDICINES_FILE
from utils.id_utils import generate_id

def medicine_manager(patient_id):
    st.title("💊 Medicine Manager")
    
    # Custom CSS for medicine containers
    st.markdown("""
    <style>
    .medicine-container {
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 6px solid;
    }
    .in-stock {
        background-color: #f0fdf4;
        border-left-color: #22c55e;
        border: 2px solid #22c55e;
    }
    .low-stock {
        background-color: #fffbeb;
        border-left-color: #f59e0b;
        border: 2px solid #f59e0b;
    }
    .out-of-stock {
        background-color: #fef2f2;
        border-left-color: #ef4444;
        border: 2px solid #ef4444;
    }
    .stock-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .stock-green { background-color: #22c55e; }
    .stock-yellow { background-color: #f59e0b; }
    .stock-red { background-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)
    
    # Tab navigation
    tab1, tab2, tab3 = st.tabs(["➕ Add Medicine", "📋 My Medicines", "📤 Import / Export"])
    
    with tab1:
        add_medicine_form(patient_id)
    
    with tab2:
        display_medicines(patient_id)
    
    with tab3:
        import_export_medicines(patient_id)

def add_medicine_form(patient_id):
    st.subheader("Add New Medicine")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            medicine_name = st.text_input("Medicine Name*", placeholder="e.g., Paracetamol")
            contents = st.text_input("Contents / Composition*", placeholder="e.g., Acetaminophen 500mg")
            quantity = st.number_input("Quantity*", min_value=0, value=30, help="Number of tablets/capsules")
            
        with col2:
            expiry_date = st.date_input("Expiry Date*", min_value=date.today())
            purpose = st.text_input("Purpose*", placeholder="e.g., Fever, Pain relief")
            category = st.selectbox("Category*", 
                                   ["General", "Antibiotics", "Pain Relief", "Vitamins", 
                                    "Blood Pressure", "Diabetes", "Heart", "Other"])
        
        # Instructions and additional details
        st.subheader("Additional Details")
        instructions = st.text_area("Instructions", 
                                   placeholder="e.g., Take with water, Do not crush",
                                   height=100)
        
        col3, col4 = st.columns(2)
        with col3:
            take_with_food = st.selectbox("Take with food", ["After Food", "Before Food", "With Food", "Empty Stomach"])
        
        with col4:
            # Optional: Medicine image upload
            uploaded_image = st.file_uploader("Medicine Image (Optional)", 
                                            type=['jpg', 'jpeg', 'png'],
                                            help="Upload a photo of the medicine for easy identification")
        
        # Submit button
        if st.button("💾 Save Medicine", type="primary", use_container_width=True):
            if not all([medicine_name, contents, quantity, purpose]):
                st.error("Please fill in all required fields marked with *")
            else:
                # Generate medicine ID
                medicine_id = generate_id("MED")
                
                # Handle image upload
                image_path = None
                if uploaded_image:
                    # Create medicine images directory
                    images_dir = "data/medicine_images"
                    os.makedirs(images_dir, exist_ok=True)
                    
                    # Save uploaded image
                    image_path = os.path.join(images_dir, f"{medicine_id}_{uploaded_image.name}")
                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.getbuffer())
                
                # Create medicine record
                new_medicine = {
                    "medicine_id": medicine_id,
                    "patient_id": patient_id,
                    "name": medicine_name,
                    "contents": contents,
                    "quantity": int(quantity),
                    "expiry_date": expiry_date.isoformat(),
                    "purpose": purpose,
                    "instructions": instructions,
                    "take_with_food": take_with_food,
                    "category": category,
                    "image_path": image_path,
                    "created_at": datetime.now().isoformat()
                }
                
                # Save to database
                medicines = load_json(MEDICINES_FILE)
                medicines[medicine_id] = new_medicine
                save_json(MEDICINES_FILE, medicines)
                
                st.success(f"✅ Medicine '{medicine_name}' added successfully!")
                st.balloons()
                st.rerun()

def display_medicines(patient_id):
    st.subheader("Your Medicine Collection")
    
    medicines = load_json(MEDICINES_FILE)
    patient_medicines = {k: v for k, v in medicines.items() if v.get("patient_id") == patient_id}
    
    if not patient_medicines:
        st.info("No medicines added yet. Use the 'Add Medicine' tab to get started.")
        return
    
    # Statistics
    total_medicines = len(patient_medicines)
    in_stock = sum(1 for med in patient_medicines.values() if med.get("quantity", 0) > 5)
    low_stock = sum(1 for med in patient_medicines.values() if 1 <= med.get("quantity", 0) <= 5)
    out_of_stock = sum(1 for med in patient_medicines.values() if med.get("quantity", 0) == 0)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Total Medicines", total_medicines)
    col2.metric("🟢 In Stock", in_stock)
    col3.metric("🟡 Low Stock", low_stock)
    col4.metric("🔴 Out of Stock", out_of_stock)
    
    st.markdown("---")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox("Filter by Category", 
                                     ["All"] + list(set([med.get("category", "General") for med in patient_medicines.values()])))
    with col2:
        stock_filter = st.selectbox("Filter by Stock Status", 
                                  ["All", "In Stock (>5)", "Low Stock (1-5)", "Out of Stock (0)"])
    
    # Display medicines in containers
    filtered_medicines = patient_medicines.copy()
    
    # Apply filters
    if category_filter != "All":
        filtered_medicines = {k: v for k, v in filtered_medicines.items() if v.get("category") == category_filter}
    
    if stock_filter != "All":
        if stock_filter == "In Stock (>5)":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v.get("quantity", 0) > 5}
        elif stock_filter == "Low Stock (1-5)":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if 1 <= v.get("quantity", 0) <= 5}
        elif stock_filter == "Out of Stock (0)":
            filtered_medicines = {k: v for k, v in filtered_medicines.items() if v.get("quantity", 0) == 0}
    
    # Display filtered medicines
    for med_id, medicine in filtered_medicines.items():
        display_medicine_container(med_id, medicine, patient_id)

def display_medicine_container(med_id, medicine, patient_id):
    quantity = medicine.get("quantity", 0)
    
    # Determine container style based on stock
    if quantity > 5:
        container_class = "in-stock"
        stock_color = "stock-green"
        stock_status = "In Stock"
    elif 1 <= quantity <= 5:
        container_class = "low-stock"
        stock_color = "stock-yellow"
        stock_status = "Low Stock"
    else:
        container_class = "out-of-stock"
        stock_color = "stock-red"
        stock_status = "Out of Stock"
    
    # Create container with appropriate styling
    st.markdown(f"""
    <div class="medicine-container {container_class}">
        <h4>💊 {medicine.get("name", "Unknown Medicine")}</h4>
        <p><strong>Contents:</strong> {medicine.get("contents", "Not specified")}</p>
        <p><strong>Stock Status:</strong> <span class="stock-indicator {stock_color}"></span>{stock_status} ({quantity} remaining)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional details in expander
    with st.expander(f"📋 Details for {medicine.get('name', 'Medicine')}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Purpose:** {medicine.get('purpose', 'Not specified')}")
            st.write(f"**Category:** {medicine.get('category', 'General')}")
            st.write(f"**Take with:** {medicine.get('take_with_food', 'Not specified')}")
            
        with col2:
            st.write(f"**Expiry Date:** {medicine.get('expiry_date', 'Not specified')}")
            st.write(f"**Added on:** {medicine.get('created_at', 'Unknown')}")
            
        with col3:
            # Show medicine image if available
            image_path = medicine.get('image_path')
            if image_path and os.path.exists(image_path):
                st.image(image_path, caption="Medicine Image", width=150)
        
        # Instructions
        if medicine.get('instructions'):
            st.write(f"**Instructions:** {medicine.get('instructions')}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"🔄 Update Quantity", key=f"update_{med_id}"):
                update_quantity_dialog(med_id, medicine)
        
        with col2:
            if st.button(f"✏️ Edit Medicine", key=f"edit_{med_id}"):
                st.info("Edit feature coming soon!")
        
        with col3:
            if st.button(f"🗑️ Delete", key=f"delete_{med_id}"):
                if st.confirm(f"Are you sure you want to delete {medicine.get('name')}?"):
                    delete_medicine(med_id)

def update_quantity_dialog(med_id, medicine):
    with st.form(f"update_quantity_{med_id}"):
        st.write(f"Update quantity for **{medicine.get('name')}**")
        current_qty = medicine.get('quantity', 0)
        st.write(f"Current quantity: {current_qty}")
        
        new_quantity = st.number_input("New Quantity", 
                                     min_value=0, 
                                     value=current_qty,
                                     help="Enter the current number of tablets/capsules remaining")
        
        if st.form_submit_button("Update"):
            medicines = load_json(MEDICINES_FILE)
            medicines[med_id]['quantity'] = int(new_quantity)
            save_json(MEDICINES_FILE, medicines)
            st.success("Quantity updated successfully!")
            st.rerun()

def delete_medicine(med_id):
    medicines = load_json(MEDICINES_FILE)
    if med_id in medicines:
        medicine_name = medicines[med_id].get('name', 'Unknown')
        del medicines[med_id]
        save_json(MEDICINES_FILE, medicines)
        st.success(f"Medicine '{medicine_name}' deleted successfully!")
        st.rerun()

def import_export_medicines(patient_id):
    st.subheader("Import / Export Medicines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📥 Import Medicines**")
        st.info("Import feature coming soon! You'll be able to upload CSV files with medicine data.")
    
    with col2:
        st.write("**📤 Export Medicines**")
        if st.button("Download My Medicines (CSV)"):
            medicines = load_json(MEDICINES_FILE)
            patient_medicines = {k: v for k, v in medicines.items() if v.get("patient_id") == patient_id}
            
            if patient_medicines:
                # Create CSV data
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write headers
                headers = ["Medicine Name", "Contents", "Quantity", "Expiry Date", "Purpose", "Category", "Instructions", "Take With Food", "Added Date"]
                writer.writerow(headers)
                
                # Write data
                for med in patient_medicines.values():
                    row = [
                        med.get('name', ''),
                        med.get('contents', ''),
                        med.get('quantity', 0),
                        med.get('expiry_date', ''),
                        med.get('purpose', ''),
                        med.get('category', ''),
                        med.get('instructions', ''),
                        med.get('take_with_food', ''),
                        med.get('created_at', '')
                    ]
                    writer.writerow(row)
                
                csv_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"my_medicines_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No medicines to export.")
