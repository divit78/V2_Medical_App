# reminders.py - generated file
import streamlit as st
from datetime import datetime, timedelta
from config.constants import SCHEDULES_FILE, MEDICINES_FILE
from utils.file_ops import load_json, save_json
from utils.id_utils import generate_id

def medicine_reminder_page(user_id):
    st.title("⏰ Medicine Reminders")

    medicines = load_json(MEDICINES_FILE)
    schedules = load_json(SCHEDULES_FILE)

    patient_meds = {mid: m for mid, m in medicines.items() if m.get("patient_id") == user_id}

    if not patient_meds:
        st.info("No medicines available. Please add medicines first.")
        return

    selected_med = st.selectbox("Select Medicine", list(patient_meds.keys()), format_func=lambda k: patient_meds[k]['name'])
    selected = patient_meds[selected_med]

    with st.form("schedule_med"):
        doses_per_day = st.slider("Doses per day", min_value=1, max_value=6, value=2)
        times = [st.time_input(f"Dose {i+1} time") for i in range(doses_per_day)]
        before_after_food = st.selectbox("When to take?", ["Before Eating", "After Eating", "With Food"])
        precaution = st.text_area("Precautions (if any)")
        submitted = st.form_submit_button("Save Reminder")

        if submitted:
            sched_id = generate_id("SCHD")
            schedules[sched_id] = {
                "patient_id": user_id,
                "medicine_id": selected_med,
                "doses_per_day": doses_per_day,
                "times": [t.strftime("%H:%M") for t in times],
                "before_after_food": before_after_food,
                "precaution": precaution,
                "remaining_quantity": selected.get("quantity", 0),
                "last_taken": None,
                "next_dose_time": None,
                "created_at": datetime.now().isoformat(),
                "missed_doses": 0
            }
            save_json(SCHEDULES_FILE, schedules)
            st.success("⏰ Reminder saved!")

    st.subheader("📋 Active Reminders")
    active_reminders = {sid: s for sid, s in schedules.items() if s.get("patient_id") == user_id}

    for sid, sched in active_reminders.items():
        med = patient_meds.get(sched.get("medicine_id"), {})
        st.markdown(f"**{med.get('name', 'Unknown')}**")
        st.write(f"Times: {', '.join(sched.get('times', []))}")
        st.write(f"Precautions: {sched.get('precaution', '-')}")
        st.write(f"Remaining Quantity: {sched.get('remaining_quantity', 0)}")
        st.write(f"Missed Doses: {sched.get('missed_doses', 0)}")
        st.markdown("---")

