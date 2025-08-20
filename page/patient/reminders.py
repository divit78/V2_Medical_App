import streamlit as st
from datetime import datetime, time
from utils.file_ops import load_json, save_json
from config.constants import MEDICINES_FILE, SCHEDULES_FILE
from utils.id_utils import generate_id

def safe_parse_datetime(iso_str):
    """Safely parse ISO datetime string, return None if invalid"""
    if not iso_str or not isinstance(iso_str, str):
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError):
        return None

def medicine_reminder_page(patient_id):
    st.title("⏰ Medicine Reminders")
    
    # Enhanced CSS for reminder containers
    st.markdown("""
    <style>
    .reminder-container {
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border-left: 6px solid;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 2px solid;
        transition: transform 0.2s ease;
    }
    .reminder-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    .active-reminder {
        border-left-color: #10b981;
        border-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    .paused-reminder {
        border-left-color: #f59e0b;
        border-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    .low-stock-reminder {
        border-left-color: #f59e0b;
        border-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fed7aa 100%);
    }
    .out-stock-reminder {
        border-left-color: #ef4444;
        border-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
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
    .time-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.1);
        color: #4f46e5;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        margin: 2px 4px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .reminder-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 15px;
    }
    .reminder-title {
        font-size: 1.3em;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    .reminder-details {
        line-height: 1.6;
        color: #4b5563;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load data
    medicines = load_json(MEDICINES_FILE)
    schedules = load_json(SCHEDULES_FILE)
    
    # Filter patient's medicines
    patient_medicines = {k: v for k, v in medicines.items() if v.get("patient_id") == patient_id}
    
    if not patient_medicines:
        st.warning("⚠️ No medicines found! Please add medicines first.")
        if st.button("➕ Add Medicine"):
            st.session_state.patient_nav_page = "Add Medicine"
            st.rerun()
        return
    
    # Create reminder form
    st.subheader("🔔 Set New Reminder")
    
    with st.form("reminder_form"):
        # Medicine selection with stock indicator
        medicine_options = []
        medicine_mapping = {}
        
        for med_id, medicine in patient_medicines.items():
            quantity = medicine.get("quantity", 0)
            if quantity > 5:
                stock_indicator = "🟢"
            elif 1 <= quantity <= 5:
                stock_indicator = "🟡"
            else:
                stock_indicator = "🔴"
            
            option_text = f"{stock_indicator} {medicine.get('name', 'Unknown')} (Stock: {quantity})"
            medicine_options.append(option_text)
            medicine_mapping[option_text] = med_id
        
        selected_medicine_option = st.selectbox("Select Medicine", medicine_options)
        selected_medicine_id = medicine_mapping.get(selected_medicine_option)
        
        if selected_medicine_id:
            selected_medicine = patient_medicines[selected_medicine_id]
            
            # Show medicine info
            with st.expander("📋 Medicine Information"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Contents:** {selected_medicine.get('contents', 'Not specified')}")
                    st.write(f"**Purpose:** {selected_medicine.get('purpose', 'Not specified')}")
                with col2:
                    st.write(f"**Category:** {selected_medicine.get('category', 'General')}")
                    st.write(f"**Expiry:** {selected_medicine.get('expiry_date', 'Not specified')}")
            
            # Dosage configuration
            st.subheader("💊 Dosage Schedule")
            
            doses_per_day = st.selectbox("Doses per day", [1, 2, 3, 4, 5, 6])
            
            # Time inputs for each dose
            dose_times = []
            cols = st.columns(min(doses_per_day, 3))  # Max 3 columns
            
            for i in range(doses_per_day):
                col_index = i % 3
                with cols[col_index]:
                    default_times = [time(8, 0), time(14, 0), time(20, 0), time(6, 0), time(12, 0), time(18, 0)]
                    default_time = default_times[i] if i < len(default_times) else time(8, 0)
                    
                    dose_time = st.time_input(f"Dose {i+1} time", value=default_time, key=f"dose_{i}")
                    dose_times.append(dose_time)
            
            # Additional settings
            col1, col2 = st.columns(2)
            
            with col1:
                before_after_food = st.selectbox("When to take?", 
                                               ["Before Eating", "After Eating", "With Food", "Empty Stomach"])
            
            with col2:
                # Auto-fill based on medicine's take_with_food preference
                medicine_preference = selected_medicine.get('take_with_food', 'After Food')
                st.info(f"💡 Recommended: {medicine_preference}")
            
            precautions = st.text_area("Precautions (if any)", 
                                     placeholder="e.g., Do not take with milk, Avoid alcohol",
                                     value=selected_medicine.get('instructions', ''))
            
            # Submit button
            submitted = st.form_submit_button("🔔 Set Reminder", type="primary")
            
            if submitted:
                # Create schedule
                schedule_id = generate_id("SCH")
                
                # Convert times to strings (12-hour format)
                time_strings = [t.strftime("%I:%M %p") for t in dose_times]
                
                new_schedule = {
                    "schedule_id": schedule_id,
                    "patient_id": patient_id,
                    "medicine_id": selected_medicine_id,
                    "medicine_name": selected_medicine.get('name', 'Unknown'),
                    "doses_per_day": doses_per_day,
                    "times": time_strings,
                    "before_after_food": before_after_food,
                    "precaution": precautions,
                    "remaining_quantity": selected_medicine.get('quantity', 0),
                    "last_taken": None,
                    "next_dose_time": None,
                    "missed_doses": 0,
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                
                # Save schedule
                schedules[schedule_id] = new_schedule
                save_json(SCHEDULES_FILE, schedules)
                
                st.success(f"✅ Reminder set for {selected_medicine.get('name')}!")
                st.rerun()
    
    # Display active reminders
    st.markdown("---")
    st.subheader("📋 Active Reminders")
    
    # Filter patient's schedules
    patient_schedules = {k: v for k, v in schedules.items() if v.get("patient_id") == patient_id}
    
    if not patient_schedules:
        st.info("No reminders set yet.")
    else:
        for schedule_id, schedule in patient_schedules.items():
            medicine_info = patient_medicines.get(schedule.get("medicine_id"), {})
            display_reminder_container(schedule_id, schedule, medicine_info)

def display_reminder_container(schedule_id, schedule, medicine_info):
    medicine_name = schedule.get("medicine_name") or medicine_info.get("name", "Unknown Medicine")
    quantity = medicine_info.get("quantity", 0)
    
    # Determine stock status and container style
    if quantity > 5:
        stock_color = "stock-green"
        stock_status = "In Stock"
        container_class = "active-reminder"
    elif 1 <= quantity <= 5:
        stock_color = "stock-yellow"
        stock_status = "Low Stock"
        container_class = "low-stock-reminder"
    else:
        stock_color = "stock-red"
        stock_status = "Out of Stock"
        container_class = "out-stock-reminder"
    
    # Get schedule times in 12-hour format
    times = schedule.get('times', [])
    if times and isinstance(times[0], str) and ":" in times:
        # Check if already in 12-hour format
        if "AM" in times[0] or "PM" in times:
            formatted_times = times
        else:
            # Convert from 24-hour to 12-hour format
            formatted_times = []
            for time_str in times:
                try:
                    hour, minute = map(int, time_str.split(':'))
                    time_obj = time(hour, minute)
                    formatted_times.append(time_obj.strftime("%I:%M %p"))
                except:
                    formatted_times.append(time_str)
    else:
        formatted_times = times
    
    # Create time badges
    time_badges = ''.join([f'<span class="time-badge">{t}</span>' for t in formatted_times])
    
    # Create reminder container
    st.markdown(f"""
    <div class="reminder-container {container_class}">
        <div class="reminder-header">
            <h3 class="reminder-title">💊 {medicine_name}</h3>
            <span class="stock-indicator {stock_color}"></span>
        </div>
        <div class="reminder-details">
            <p><strong>📊 Stock Status:</strong> {stock_status} ({quantity} remaining)</p>
            <p><strong>⏰ Schedule:</strong> {schedule.get('doses_per_day', 0)} times daily</p>
            <p><strong>🕐 Times:</strong> {time_badges}</p>
            <p><strong>🍽️ Instructions:</strong> {schedule.get('before_after_food', 'Not specified')}</p>
            {f'<p><strong>⚠️ Precautions:</strong> {schedule.get("precaution")}</p>' if schedule.get('precaution') else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons in expander
    with st.expander(f"⚙️ Manage {medicine_name} Reminder"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Mark Taken", key=f"taken_{schedule_id}", help="Mark this dose as taken"):
                mark_medicine_taken(schedule_id, schedule.get("medicine_id"))
        
        with col2:
            current_status = schedule.get('status', 'active')
            if current_status == 'active':
                if st.button("⏸️ Pause", key=f"pause_{schedule_id}", help="Pause this reminder"):
                    toggle_reminder_status(schedule_id, 'paused')
            else:
                if st.button("▶️ Resume", key=f"resume_{schedule_id}", help="Resume this reminder"):
                    toggle_reminder_status(schedule_id, 'active')
        
        with col3:
            if st.button("✏️ Edit", key=f"edit_reminder_{schedule_id}", help="Edit reminder settings"):
                st.info("Edit reminder functionality coming soon!")
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_reminder_{schedule_id}", help="Delete this reminder"):
                delete_reminder(schedule_id, medicine_name)
        
        # Show additional info with safe date parsing
        col1, col2 = st.columns(2)
        with col1:
            # FIXED: Safe parsing of last_taken datetime
            last_taken_str = schedule.get('last_taken')
            last_taken = safe_parse_datetime(last_taken_str)
            if last_taken:
                st.write(f"**🕐 Last taken:** {last_taken.strftime('%I:%M %p on %b %d, %Y')}")
        
        with col2:
            if schedule.get('missed_doses', 0) > 0:
                st.warning(f"⚠️ Missed doses: {schedule.get('missed_doses')}")
            
            remaining_qty = schedule.get('remaining_quantity', quantity)
            if remaining_qty != quantity:
                st.write(f"**💊 Schedule quantity:** {remaining_qty}")

def mark_medicine_taken(schedule_id, medicine_id):
    # Update schedule
    schedules = load_json(SCHEDULES_FILE)
    if schedule_id in schedules:
        schedules[schedule_id]['last_taken'] = datetime.now().isoformat()
        schedules[schedule_id]['remaining_quantity'] = max(0, schedules[schedule_id].get('remaining_quantity', 0) - 1)
        save_json(SCHEDULES_FILE, schedules)
    
    # Update medicine quantity
    medicines = load_json(MEDICINES_FILE)
    if medicine_id and medicine_id in medicines:
        medicines[medicine_id]['quantity'] = max(0, medicines[medicine_id].get('quantity', 0) - 1)
        save_json(MEDICINES_FILE, medicines)
    
    st.success("✅ Medicine marked as taken!")
    st.rerun()

def toggle_reminder_status(schedule_id, new_status):
    schedules = load_json(SCHEDULES_FILE)
    if schedule_id in schedules:
        schedules[schedule_id]['status'] = new_status
        save_json(SCHEDULES_FILE, schedules)
        status_text = "paused" if new_status == 'paused' else "resumed"
        st.success(f"✅ Reminder {status_text}!")
        st.rerun()

def delete_reminder(schedule_id, medicine_name):
    # Create a confirmation dialog
    if f"confirm_delete_{schedule_id}" not in st.session_state:
        st.session_state[f"confirm_delete_{schedule_id}"] = False
    
    if not st.session_state[f"confirm_delete_{schedule_id}"]:
        if st.button(f"⚠️ Confirm Delete", key=f"confirm_{schedule_id}"):
            st.session_state[f"confirm_delete_{schedule_id}"] = True
            st.rerun()
        st.warning(f"Click the button above to confirm deletion of {medicine_name} reminder.")
    else:
        schedules = load_json(SCHEDULES_FILE)
        if schedule_id in schedules:
            del schedules[schedule_id]
            save_json(SCHEDULES_FILE, schedules)
            # Clear confirmation state
            del st.session_state[f"confirm_delete_{schedule_id}"]
            st.success(f"✅ Reminder for {medicine_name} deleted!")
            st.rerun()
