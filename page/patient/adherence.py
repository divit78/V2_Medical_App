# adherence.py - generated file
import streamlit as st
import json
from datetime import datetime
from utils.file_ops import load_json
from config.constants import SCHEDULES_FILE, MEDICINES_FILE

def adherence_history(user_id):
    st.title("📈 Adherence History")

    schedules = load_json(SCHEDULES_FILE)
    medicines = load_json(MEDICINES_FILE)

    patient_schedules = {
        sid: s for sid, s in schedules.items() if s.get("patient_id") == user_id
    }

    if not patient_schedules:
        st.info("No adherence history available.")
    else:
        for sid, sched in patient_schedules.items():
            med_info = medicines.get(sched.get("medicine_id"), {})
            st.subheader(f"{med_info.get('name', 'Unknown Medicine')}")
            st.write(f"Last Taken: {sched.get('last_taken', 'N/A')}")
            st.write(f"Missed Doses: {sched.get('missed_doses', 0)}")
            adherence_rate = 0.0
            if sched.get('doses_per_day'):
                taken = sched.get('doses_per_day') - sched.get('missed_doses', 0)
                rate = (taken / sched['doses_per_day']) * 100
                adherence_rate = max(0.0, min(rate, 100.0))
            st.write(f"Estimated Adherence: {adherence_rate:.1f}%")
            st.markdown("---")

        if st.button("📁 Export Adherence Report"):
            download_data = json.dumps(patient_schedules, indent=2)
            st.download_button("Download as JSON", download_data, "adherence_history.json", mime="application/json")



