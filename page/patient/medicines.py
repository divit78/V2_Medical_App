import streamlit as st
from datetime import datetime, date
import os
import pymysql
from config.constants import MEDICINES_FILE, DB_CONFIG
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id


def get_db_connection():
    """Create MySQL database connection"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def add_medicine_to_db(medicine_data):
    """Add medicine to MySQL database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            sql = """INSERT INTO medicines 
                    (medicine_id, patient_id, name, contents, quantity, expiry_date, 
                     purpose, instructions, take_with_food, category, image_path, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(sql, (
                medicine_data['medicine_id'],
                medicine_data['patient_id'],
                medicine_data['name'],
                medicine_data['contents'],
                medicine_data['quantity'],
                medicine_data['expiry_date'],
                medicine_data['purpose'],
                medicine_data['instructions'],
                medicine_data['take_with_food'],
                medicine_data['category'],
                medicine_data['image_path'],
                medicine_data['created_at']
            ))
        
        connection.commit()
        return True
    except Exception as e:
        st.error(f"Error adding medicine to database: {e}")
        return False
    finally:
        connection.close()


def get_patient_medicines_from_db(patient_id):
    """Get all medicines for a patient from MySQL database"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM medicines WHERE patient_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (patient_id,))
            medicines = cursor.fetchall()
        return medicines
    except Exception as e:
        st.error(f"Error fetching medicines: {e}")
        return []
    finally:
        connection.close()


def update_medicine_quantity_in_db(medicine_id, new_quantity):
    """Update medicine quantity in MySQL database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE medicines SET quantity = %s WHERE medicine_id = %s"
            cursor.execute(sql, (new_quantity, medicine_id))
        
        connection.commit()
        return True
    except Exception as e:
        st.error(f"Error updating medicine quantity: {e}")
        return False
    finally:
        connection.close()


def delete_medicine_from_db(medicine_id):
    """Delete medicine from MySQL database"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # First get the medicine details to delete image file
            sql_select = "SELECT image_path FROM medicines WHERE medicine_id = %s"
            cursor.execute(sql_select, (medicine_id,))
            result = cursor.fetchone()
            
            # Delete the medicine record
            sql_delete = "DELETE FROM medicines WHERE medicine_id = %s"
            cursor.execute(sql_delete, (medicine_id,))
            
            # Delete image file if exists
            if result and result['image_path'] and os.path.exists(result['image_path']):
                try:
                    os.remove(result['image_path'])
                except:
                    pass  # Continue even if image deletion fails
        
        connection.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting medicine: {e}")
        return False
    finally:
        connection.close()


def check_duplicate_medicine(patient_id, medicine_name):
    """Check if medicine with same name exists for patient"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM medicines WHERE patient_id = %s AND LOWER(name) = LOWER(%s)"
            cursor.execute(sql, (patient_id, medicine_name))
            result = cursor.fetchone()
        return result
    except Exception as e:
        st.error(f"Error checking duplicate medicine: {e}")
        return None
    finally:
        connection.close()


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
    .duplicate-warning {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #92400e;
    }
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
            category = st.selectbox("Category*", ["General", "Antibiotic", "Painkiller", "Vitamin", "Other"])
        
        st.subheader("Additional Details")
        instructions = st.text_area("Instructions", placeholder="e.g., Take with water, Do not crush", height=100)
        
        col3, col4 = st.columns(2)
        with col3:
            take_with_food = st.selectbox("Take with food", ["Before Food", "After Food", "With Food"])
        
        with col4:
            uploaded_image = st.file_uploader("Medicine Image (Optional)", type=['jpg', 'jpeg', 'png'])
        
        if st.button("💾 Save Medicine", type="primary", use_container_width=True):
            if not all([medicine_name, contents, quantity, purpose]):
                st.error("Please fill in all required fields marked with *")
                return
            
            # FIXED: Check for duplicates in database
            existing_medicine = check_duplicate_medicine(patient_id, medicine_name)
            
            if existing_medicine:
                st.markdown(f"""
                <div class="duplicate-warning">
                    <h4>⚠️ Medicine Already Exists</h4>
                    <p>You already have <strong>'{medicine_name}'</strong> with <strong>{existing_medicine['quantity']} units</strong>.</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    current_qty = existing_medicine['quantity']
                    st.info(f"Current quantity: {current_qty}")
                    add_quantity = st.number_input("Add to current stock:", min_value=0, value=int(quantity))
                    new_total = current_qty + add_quantity
                    st.success(f"New total will be: {new_total}")
                
                with col2:
                    if st.button("🔄 Update Existing Medicine", type="primary"):
                        # FIXED: Update in database
                        if update_medicine_quantity_in_db(existing_medicine['medicine_id'], new_total):
                            st.success(f"✅ Updated '{medicine_name}' quantity to {new_total}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Failed to update medicine quantity")
                
                if st.button("➕ Add as New Medicine Anyway", type="secondary"):
                    st.session_state['force_create_new'] = True
                    st.rerun()
                
                return
            
            try:
                medicine_id = generate_id("MED")
                
                # Handle image upload
                image_path = None
                if uploaded_image:
                    images_dir = "data/medicine_images"
                    os.makedirs(images_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(images_dir, f"{medicine_id}_{timestamp}_{uploaded_image.name}")
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
                
                # FIXED: Save to MySQL database instead of JSON file
                if add_medicine_to_db(new_medicine):
                    st.success(f"✅ Medicine '{medicine_name}' added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to add medicine to database")
                        
            except Exception as e:
                st.error(f"❌ Error saving medicine: {e}")


def display_medicines(patient_id):
    st.subheader("Your Medicine Collection")
    
    # FIXED: Load medicines from MySQL database
    patient_medicines = get_patient_medicines_from_db(patient_id)
    
    if not patient_medicines:
        st.info("No medicines added yet. Use the 'Add Medicine' tab to get started.")
        return
    
    # Statistics
    total_medicines = len(patient_medicines)
    in_stock = sum(1 for med in patient_medicines if med.get("quantity", 0) > 5)
    low_stock = sum(1 for med in patient_medicines if 1 <= med.get("quantity", 0) <= 5)
    out_of_stock = sum(1 for med in patient_medicines if med.get("quantity", 0) == 0)
    
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
                                     ["All"] + list(set([med.get("category", "General") for med in patient_medicines])))
    with col2:
        stock_filter = st.selectbox("Filter by Stock Status", 
                                  ["All", "In Stock (>5)", "Low Stock (1-5)", "Out of Stock (0)"])
    
    # Apply filters
    filtered_medicines = patient_medicines.copy()
    
    if category_filter != "All":
        filtered_medicines = [med for med in filtered_medicines if med.get("category") == category_filter]
    
    if stock_filter != "All":
        if stock_filter == "In Stock (>5)":
            filtered_medicines = [med for med in filtered_medicines if med.get("quantity", 0) > 5]
        elif stock_filter == "Low Stock (1-5)":
            filtered_medicines = [med for med in filtered_medicines if 1 <= med.get("quantity", 0) <= 5]
        elif stock_filter == "Out of Stock (0)":
            filtered_medicines = [med for med in filtered_medicines if med.get("quantity", 0) == 0]
    
    # Display filtered medicines
    for medicine in filtered_medicines:
        display_medicine_container(medicine, patient_id)


def display_medicine_container(medicine, patient_id):
    quantity = medicine.get("quantity", 0)
    med_id = medicine.get("medicine_id")
    
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
    
    st.markdown(f"""
    <div class="medicine-container {container_class}">
        <h4>💊 {medicine.get("name", "Unknown Medicine")}</h4>
        <p><strong>Contents:</strong> {medicine.get("contents", "Not specified")}</p>
        <p><strong>Stock Status:</strong> <span class="stock-indicator {stock_color}"></span>{stock_status} ({quantity} remaining)</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander(f"📋 Details for {medicine.get('name', 'Medicine')}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Purpose:** {medicine.get('purpose', 'Not specified')}")
            st.write(f"**Category:** {medicine.get('category', 'General')}")
            st.write(f"**Take with:** {medicine.get('take_with_food', 'Not specified')}")
            
        with col2:
            # Safe date formatting
            expiry_date = medicine.get('expiry_date', 'Not specified')
            if hasattr(expiry_date, 'strftime'):
                expiry_date = expiry_date.strftime('%Y-%m-%d')
            elif isinstance(expiry_date, str) and len(expiry_date) > 10:
                expiry_date = expiry_date[:10]
            
            created_date = medicine.get('created_at', 'Unknown')
            if hasattr(created_date, 'strftime'):
                created_date = created_date.strftime('%Y-%m-%d')
            elif isinstance(created_date, str) and len(created_date) > 10:
                created_date = created_date[:10]
            
            st.write(f"**Expiry Date:** {expiry_date}")
            st.write(f"**Added on:** {created_date}")
            
        with col3:
            image_path = medicine.get('image_path')
            if image_path and os.path.exists(image_path):
                st.image(image_path, caption="Medicine Image", width=150)
        
        if medicine.get('instructions'):
            st.write(f"**Instructions:** {medicine.get('instructions')}")
        
        st.markdown("---")
        st.subheader("⚙️ Actions")
        
        col1, col2, col3 = st.columns(3)
        
        # FIXED: Update quantity functionality with database
        with col1:
            current_qty = medicine.get('quantity', 0)
            new_qty = st.number_input(
                f"Update quantity:", 
                min_value=0, 
                value=current_qty,
                key=f"qty_input_{med_id}"
            )
            
            if st.button("🔄 Update Quantity", key=f"update_{med_id}", type="primary"):
                # FIXED: Update in MySQL database
                if update_medicine_quantity_in_db(med_id, int(new_qty)):
                    st.success(f"✅ Updated quantity to {new_qty}!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update quantity")
        
        with col2:
            if st.button("✏️ Edit Medicine", key=f"edit_{med_id}"):
                st.info("Edit feature coming soon!")
        
        # FIXED: Delete functionality with database
        with col3:
            delete_key = f'delete_confirm_{med_id}'
            
            if delete_key not in st.session_state:
                st.session_state[delete_key] = False
            
            if not st.session_state[delete_key]:
                if st.button("🗑️ Delete Medicine", key=f"delete_btn_{med_id}", type="secondary"):
                    st.session_state[delete_key] = True
                    st.rerun()
            else:
                st.warning(f"⚠️ Delete '{medicine.get('name')}'?")
                
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, Delete", key=f"confirm_yes_{med_id}", type="primary"):
                        # FIXED: Delete from MySQL database
                        if delete_medicine_from_db(med_id):
                            # Clean up session state
                            keys_to_delete = [key for key in st.session_state.keys() if med_id in str(key)]
                            for key in keys_to_delete:
                                del st.session_state[key]
                            
                            st.success(f"✅ '{medicine.get('name')}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete medicine")
                
                with col_no:
                    if st.button("❌ Cancel", key=f"confirm_no_{med_id}"):
                        st.session_state[delete_key] = False
                        st.rerun()


def import_export_medicines(patient_id):
    st.subheader("Import / Export Medicines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📥 Import Medicines**")
        st.info("Import feature coming soon!")
    
    with col2:
        st.write("**📤 Export Medicines**")
        if st.button("Download My Medicines (CSV)"):
            # FIXED: Export from database
            patient_medicines = get_patient_medicines_from_db(patient_id)
            
            if patient_medicines:
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                headers = ["Medicine Name", "Contents", "Quantity", "Expiry Date", "Purpose", "Category", "Instructions", "Take With Food", "Added Date"]
                writer.writerow(headers)
                
                for med in patient_medicines:
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
