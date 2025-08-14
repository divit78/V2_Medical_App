import streamlit as st
import os
import json
from datetime import datetime, date

from config.constants import MEDICINES_FILE, UPLOAD_DIR
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id




from datetime import date, datetime
import json

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")





def local_css():
    st.markdown("""
    <style>
    .med-card {
        background: #fefeff;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 6px solid #5a75f9;
    }
    .pill {
        display: inline-block;
        padding: 4px 10px;
        margin: 4px 0;
        border-radius: 12px;
        font-size: 12px;
        color: white;
    }
    .pill-danger { background: #dc3545; }
    .pill-warning { background: #ffc107; color: black; }
    .pill-safe { background: #28a745; }
    .tag {
        display: inline-block;
        background: #e8ebff;
        padding: 2px 8px;
        margin: 2px 2px;
        border-radius: 8px;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

def medicine_manager(user_id):
    local_css()
    st.title("💊 Medicine Manager")

    tab1, tab2, tab3 = st.tabs(["➕ Add Medicine", "📋 My Medicines", "📤 Import / Export"])

    # ---------------- TAB 1: ADD MEDICINE ----------------
    with tab1:
        with st.form("add_medicine_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Medicine Name*", max_chars=100)
                contents = st.text_area("Contents / Composition*", max_chars=300)
                quantity = st.number_input("Quantity*", min_value=1)
                expiry_date = st.date_input("Expiry Date*", min_value=date.today())
                purpose = st.text_input("Purpose*", max_chars=150)
                category = st.selectbox("Category*", ["General", "Antibiotic", "Painkiller", "Vitamin", "Other"])
            with col2:
                instructions = st.text_area("Instructions (optional)")
                timing = st.selectbox("When to take?", ["Before Food", "After Food", "With Food"])
                photo = st.file_uploader("Medicine Image (optional)", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("Save Medicine")

        if submitted:
            if not name or not contents or not purpose:
                st.error("❌ Please complete all required fields.")
            else:
                medicines = load_json(MEDICINES_FILE)
                med_id = generate_id("MED")

                medicine_data = {
                    "medicine_id": med_id,  # Ensure this is always saved!
                    "patient_id": user_id,
                    "name": name,
                    "contents": contents,
                    "quantity": quantity,
                    "expiry_date": expiry_date.isoformat(),
                    "purpose": purpose,
                    "instructions": instructions,
                    "take_with_food": timing,
                    "category": category,
                    "created_at": datetime.now().isoformat()
                }

                if photo:
                    folder = os.path.join(UPLOAD_DIR, user_id)
                    os.makedirs(folder, exist_ok=True)
                    path = os.path.join(folder, photo.name)
                    with open(path, "wb") as f:
                        f.write(photo.getbuffer())
                    medicine_data["image_path"] = path

                medicines[med_id] = medicine_data
                save_json(MEDICINES_FILE, medicines)
                st.success(f"✅ Medicine '{name}' saved successfully!")

    # ---------------- TAB 2: VIEW / MANAGE ----------------
    with tab2:
        st.subheader("📋 Your Medicines")

        medicines = load_json(MEDICINES_FILE)
        all_meds = [m for m in medicines.values() if m.get("patient_id") == user_id]

        if not all_meds:
            st.info("You haven't added any medicines yet.")
            return

        search = st.text_input("🔎 Search medicine...")
        category_filter = st.selectbox("Filter by Category", ["All"] + list(set(m.get("category", "Other") for m in all_meds)))
        sort_option = st.radio("Sort by", ["Name", "Expiry Date"], horizontal=True)

        meds = all_meds
        if search:
            meds = [m for m in meds if search.lower() in m.get("name", "").lower()
                    or search.lower() in m.get("purpose", "").lower()]

        if category_filter != "All":
            meds = [m for m in meds if m.get("category") == category_filter]

        if sort_option == "Name":
            meds.sort(key=lambda x: x.get("name", ""))
        elif sort_option == "Expiry Date":
            meds.sort(key=lambda x: x.get("expiry_date", ""))

        for med in meds:
            st.markdown('<div class="med-card">', unsafe_allow_html=True)
            st.markdown(f"### {med.get('name', 'Unknown')}")
            st.markdown(f"**Purpose:** {med.get('purpose', '-')}")
            st.markdown(f"💬 {med.get('instructions', 'No instructions')}")
            st.markdown(" ".join([
                f"<span class='tag'>{med.get('take_with_food')}</span>",
                f"<span class='tag'>Qty: {med.get('quantity', 0)}</span>",
                f"<span class='tag'>{med.get('category')}</span>"
            ]), unsafe_allow_html=True)

            try:
                exp = datetime.fromisoformat(med["expiry_date"]).date()
                days_left = (exp - date.today()).days
                if days_left < 0:
                    badge = "<span class='pill pill-danger'>❌ Expired</span>"
                elif days_left < 7:
                    badge = f"<span class='pill pill-warning'>⚠️ {days_left} days left</span>"
                else:
                    badge = f"<span class='pill pill-safe'>✅ {days_left} days left</span>"
                st.markdown(badge, unsafe_allow_html=True)
            except:
                pass

            if med.get("image_path") and os.path.exists(med["image_path"]):
                st.image(med["image_path"], width=160)

            col1, col2 = st.columns([1, 1])
            if col1.button("✅ I took my dose", key=f"take_{med.get('medicine_id')}"):
                med["quantity"] = max(0, med.get("quantity", 0) - 1)
                medicines[med.get("medicine_id")] = med
                save_json(MEDICINES_FILE, medicines)
                st.success("Medicine updated.")

            if col2.button("❌ Delete", key=f"del_{med.get('medicine_id')}"):
                medicines.pop(med.get("medicine_id"), None)
                save_json(MEDICINES_FILE, medicines)
                st.warning(f"'{med.get('name')}' removed.")

            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TAB 3: IMPORT / EXPORT ----------------
    with tab3:
        st.subheader("📤 Export / Import Medicines")

        export_data = [m for m in load_json(MEDICINES_FILE).values() if m.get("patient_id") == user_id]                 
        json_data = json.dumps(export_data, indent=2, default=json_serial)

        st.download_button("⬇️ Export JSON", data=json_data, file_name="my_medicines.json", mime="application/json")

        uploaded = st.file_uploader("📥 Import from JSON", type=["json"])
        if uploaded:
            try:
                parsed = json.load(uploaded)
                meds = load_json(MEDICINES_FILE)
                added = 0
                for entry in parsed:
                    if entry.get("patient_id") == user_id:
                        meds[entry["medicine_id"]] = entry
                        added += 1
                save_json(MEDICINES_FILE, meds)
                st.success(f"✅ {added} medicines imported.")
            except:
                st.error("⚠️ Invalid JSON file.")