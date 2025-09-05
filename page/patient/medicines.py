import streamlit as st
from datetime import datetime, date
import os
import pymysql
import csv
import io
from config.constants import MEDICINES_FILE, DB_CONFIG
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id


class DatabaseHandler:
    """Simple database operations class"""
    
    @staticmethod
    def get_connection():
        try:
            return pymysql.connect(
                host=DB_CONFIG['host'], user=DB_CONFIG['user'], 
                password=DB_CONFIG['password'], database=DB_CONFIG['database'],
                charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None
    
    @staticmethod
    def execute_query(sql, params=None, fetch=False):
        connection = DatabaseHandler.get_connection()
        if not connection:
            return False if not fetch else []
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                if fetch:
                    return cursor.fetchall() if fetch == "all" else cursor.fetchone()
            connection.commit()
            return True
        except Exception as e:
            st.error(f"Database error: {e}")
            return False if not fetch else []
        finally:
            connection.close()


class MedicineRepository:
    """Repository for medicine data operations"""
    
    def __init__(self):
        self.db = DatabaseHandler()
    
    def add_medicine(self, medicine_data):
        sql = """INSERT INTO medicines (medicine_id, patient_id, name, contents, quantity, 
                 expiry_date, purpose, instructions, take_with_food, category, image_path, created_at) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        return self.db.execute_query(sql, tuple(medicine_data.values()))
    
    def get_patient_medicines(self, patient_id):
        return self.db.execute_query(
            "SELECT * FROM medicines WHERE patient_id = %s ORDER BY created_at DESC", 
            (patient_id,), "all"
        )
    
    def update_quantity(self, medicine_id, new_quantity):
        return self.db.execute_query(
            "UPDATE medicines SET quantity = %s WHERE medicine_id = %s", 
            (new_quantity, medicine_id)
        )
    
    def delete_medicine(self, medicine_id):
        # Get image path first
        result = self.db.execute_query(
            "SELECT image_path FROM medicines WHERE medicine_id = %s", 
            (medicine_id,), "one"
        )
        
        # Delete image file if exists
        if result and result.get('image_path') and os.path.exists(result['image_path']):
            try:
                os.remove(result['image_path'])
            except:
                pass
        
        return self.db.execute_query("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
    
    def check_duplicate(self, patient_id, medicine_name):
        return self.db.execute_query(
            "SELECT * FROM medicines WHERE patient_id = %s AND LOWER(name) = LOWER(%s)", 
            (patient_id, medicine_name), "one"
        )


class FileHandler:
    """Handle file operations"""
    
    @staticmethod
    def save_medicine_image(uploaded_file, medicine_id):
        if not uploaded_file:
            return None
        
        images_dir = "data/medicine_images"
        os.makedirs(images_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(images_dir, f"{medicine_id}_{timestamp}_{uploaded_file.name}")
        
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return image_path


class MedicineManager:
    """Main medicine manager class"""
    
    def __init__(self, patient_id):
        self.patient_id = patient_id
        self.repository = MedicineRepository()
        self.file_handler = FileHandler()
    
    def render(self):
        st.title("💊 Medicine Manager")
        self._load_styles()
        
        tab1, tab2, tab3 = st.tabs(["➕ Add Medicine", "📋 My Medicines", "📤 Export"])
        
        with tab1:
            self._render_add_form()
        with tab2:
            self._render_medicines_list()
        with tab3:
            self._render_export()
    
    def _load_styles(self):
        st.markdown("""<style>
        .medicine-container{border-radius:15px;padding:20px;margin:10px 0;box-shadow:0 4px 6px rgba(0,0,0,0.1);border-left:6px solid}
        .in-stock{background-color:#f0fdf4;border-left-color:#22c55e;border:2px solid #22c55e}
        .low-stock{background-color:#fffbeb;border-left-color:#f59e0b;border:2px solid #f59e0b}
        .out-of-stock{background-color:#fef2f2;border-left-color:#ef4444;border:2px solid #ef4444}
        .duplicate-warning{background-color:#fef3c7;border:1px solid #f59e0b;border-radius:8px;padding:1rem;margin:1rem 0;color:#92400e}
        </style>""", unsafe_allow_html=True)
    
    def _render_add_form(self):
        st.subheader("Add New Medicine")
        
        col1, col2 = st.columns(2)
        
        with col1:
            medicine_name = st.text_input("Medicine Name*", placeholder="e.g., Paracetamol")
            contents = st.text_input("Contents*", placeholder="e.g., Acetaminophen 500mg")
            quantity = st.number_input("Quantity*", min_value=0, value=30)
        
        with col2:
            expiry_date = st.date_input("Expiry Date*", min_value=date.today())
            purpose = st.text_input("Purpose*", placeholder="e.g., Fever, Pain relief")
            category = st.selectbox("Category*", ["General", "Antibiotic", "Painkiller", "Vitamin", "Other"])
        
        instructions = st.text_area("Instructions", placeholder="e.g., Take with water")
        
        col3, col4 = st.columns(2)
        with col3:
            take_with_food = st.selectbox("Take with food", ["Before Food", "After Food", "With Food"])
        with col4:
            uploaded_image = st.file_uploader("Medicine Image (Optional)", type=['jpg', 'jpeg', 'png'])
        
        if st.button("💾 Save Medicine", type="primary"):
            if not all([medicine_name, contents, quantity, purpose]):
                st.error("Please fill in all required fields marked with *")
                return
            
            # Check for duplicates
            existing = self.repository.check_duplicate(self.patient_id, medicine_name)
            if existing:
                self._handle_duplicate(existing, medicine_name, quantity)
                return
            
            # Save medicine
            self._save_new_medicine(medicine_name, contents, quantity, expiry_date, 
                                  purpose, category, instructions, take_with_food, uploaded_image)
    
    def _handle_duplicate(self, existing, medicine_name, quantity):
        st.markdown(f"""<div class="duplicate-warning"><h4>⚠️ Medicine Already Exists</h4>
        <p>You already have <strong>'{medicine_name}'</strong> with <strong>{existing['quantity']} units</strong>.</p></div>""", 
        unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            add_quantity = st.number_input("Add to current stock:", min_value=0, value=int(quantity))
            new_total = existing['quantity'] + add_quantity
            st.info(f"Current: {existing['quantity']}, New total: {new_total}")
        
        with col2:
            if st.button("🔄 Update Existing Medicine", type="primary"):
                if self.repository.update_quantity(existing['medicine_id'], new_total):
                    st.success(f"✅ Updated '{medicine_name}' quantity to {new_total}!")
                    st.balloons()
                    st.rerun()
    
    def _save_new_medicine(self, name, contents, quantity, expiry_date, purpose, 
                          category, instructions, take_with_food, uploaded_image):
        try:
            medicine_id = generate_id("MED")
            image_path = self.file_handler.save_medicine_image(uploaded_image, medicine_id)
            
            medicine_data = {
                "medicine_id": medicine_id,
                "patient_id": self.patient_id,
                "name": name,
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
            
            if self.repository.add_medicine(medicine_data):
                st.success(f"✅ Medicine '{name}' added successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to add medicine")
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    def _render_medicines_list(self):
        st.subheader("Your Medicine Collection")
        medicines = self.repository.get_patient_medicines(self.patient_id)
        
        if not medicines:
            st.info("No medicines added yet.")
            return
        
        # Show statistics
        total = len(medicines)
        in_stock = sum(1 for m in medicines if m.get("quantity", 0) > 5)
        low_stock = sum(1 for m in medicines if 1 <= m.get("quantity", 0) <= 5)
        out_stock = sum(1 for m in medicines if m.get("quantity", 0) == 0)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📊 Total", total)
        col2.metric("🟢 In Stock", in_stock)
        col3.metric("🟡 Low Stock", low_stock)
        col4.metric("🔴 Out of Stock", out_stock)
        
        st.markdown("---")
        
        # Display medicines
        for medicine in medicines:
            self._display_medicine_card(medicine)
    
    def _display_medicine_card(self, medicine):
        quantity = medicine.get("quantity", 0)
        
        # Determine style based on quantity
        if quantity > 5:
            container_class = "in-stock"
            status = "In Stock"
        elif quantity > 0:
            container_class = "low-stock"
            status = "Low Stock"
        else:
            container_class = "out-of-stock"
            status = "Out of Stock"
        
        st.markdown(f"""<div class="medicine-container {container_class}">
        <h4>💊 {medicine.get("name", "Unknown")}</h4>
        <p><strong>Contents:</strong> {medicine.get("contents", "Not specified")}</p>
        <p><strong>Status:</strong> {status} ({quantity} remaining)</p>
        </div>""", unsafe_allow_html=True)
        
        with st.expander(f"📋 Details for {medicine.get('name')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Purpose:** {medicine.get('purpose', 'Not specified')}")
                st.write(f"**Category:** {medicine.get('category', 'General')}")
            
            with col2:
                st.write(f"**Expiry:** {str(medicine.get('expiry_date', 'Unknown'))[:10]}")
                st.write(f"**Take with:** {medicine.get('take_with_food', 'Not specified')}")
            
            with col3:
                image_path = medicine.get('image_path')
                if image_path and os.path.exists(image_path):
                    st.image(image_path, width=150)
            
            if medicine.get('instructions'):
                st.write(f"**Instructions:** {medicine.get('instructions')}")
            
            # Action buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                new_qty = st.number_input("Update quantity:", min_value=0, 
                                        value=medicine.get('quantity', 0), 
                                        key=f"qty_{medicine['medicine_id']}")
                if st.button("🔄 Update", key=f"update_{medicine['medicine_id']}"):
                    if self.repository.update_quantity(medicine['medicine_id'], int(new_qty)):
                        st.success("✅ Updated!")
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{medicine['medicine_id']}", type="secondary"):
                    if self.repository.delete_medicine(medicine['medicine_id']):
                        st.success("✅ Deleted!")
                        st.rerun()
    
    def _render_export(self):
        st.subheader("Export Medicines")
        
        if st.button("📥 Download CSV"):
            medicines = self.repository.get_patient_medicines(self.patient_id)
            
            if not medicines:
                st.warning("No medicines to export.")
                return
            
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            headers = ["Name", "Contents", "Quantity", "Expiry", "Purpose", "Category"]
            writer.writerow(headers)
            
            for med in medicines:
                row = [
                    med.get('name', ''),
                    med.get('contents', ''),
                    med.get('quantity', 0),
                    str(med.get('expiry_date', ''))[:10],
                    med.get('purpose', ''),
                    med.get('category', '')
                ]
                writer.writerow(row)
            
            csv_data = output.getvalue()
            st.download_button(
                "📥 Download CSV", 
                csv_data, 
                f"medicines_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


def medicine_manager(patient_id):
    """Main entry point"""
    manager = MedicineManager(patient_id)
    manager.render()
