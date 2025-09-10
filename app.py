import streamlit as st
import pandas as pd
import random

# --- Upload School Logo ---
st.sidebar.subheader("Upload School Logo (optional)")
logo_file = st.sidebar.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])
if logo_file:
    st.image(logo_file, use_column_width=True)

# --- Page Title ---
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>Extracurricular Program Assignment</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #555;'>Assign kids to programs based on preferences, capacities, and time slots</h5>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar: max programs per kid
st.sidebar.subheader("Settings")
max_programs_per_kid = st.sidebar.number_input("Max Programs per Kid", min_value=1, value=1)

# Time slot reference
time_slot_mapping = {1: "12:50-2:20", 2: "2:20-3:50", 3: "Undefined"}
st.sidebar.subheader("Time Slots Reference")
for k, v in time_slot_mapping.items():
    st.sidebar.write(f"{k}: {v}")

# --- File Uploads ---
st.subheader("Upload Programs CSV")
st.markdown("CSV format: ProgramName, Capacity, Day, TimeSlot(1,2,3)")
program_file = st.file_uploader("Upload Programs CSV", type=["csv"])

st.subheader("Upload Kids Preferences CSV")
st.markdown("CSV format: KidName, Preference1, Preference2, Preference3...")
kids_file = st.file_uploader("Upload Kids CSV", type=["csv"])

# --- Assignment Function ---
def assign_programs_with_times(kids_prefs, programs_df, max_per_kid=1):
    assigned_programs = {kid: [] for kid in kids_prefs}
    program_slots = {}
    for _, row in programs_df.iterrows():
        key = (row['ProgramName'], row['Day'], int(row['TimeSlot']))
        program_slots[key] = row['Capacity']

    max_rank = max(len(prefs) for prefs in kids_prefs.values())

    for rank in range(max_rank):
        applicants_per_program = {}
        for kid, prefs in kids_prefs.items():
            if len(assigned_programs[kid]) >= max_per_kid:
                continue
            if rank < len(prefs):
                available_slots = [k for k in program_slots if k[0] == prefs[rank] and program_slots[k] > 0]
                if available_slots:
                    chosen_slot = random.choice(available_slots)
                    applicants_per_program.setdefault(chosen_slot, []).append(kid)

        # Assign kids
        for slot_key, applicants in applicants_per_program.items():
            available = program_slots[slot_key]
            unassigned_applicants = [kid for kid in applicants if len(assigned_programs[kid]) < max_per_kid]
            if len(unassigned_applicants) <= available:
                for kid in unassigned_applicants:
                    assigned_programs[kid].append(f"{slot_key[0]} ({slot_key[1]} slot {slot_key[2]})")
                    program_slots[slot_key] -= 1
            else:
                selected = random.sample(unassigned_applicants, available)
                for kid in selected:
                    assigned_programs[kid].append(f"{slot_key[0]} ({slot_key[1]} slot {slot_key[2]})")
                    program_slots[slot_key] -= 1

    return assigned_programs

# --- Process CSVs ---
if program_file and kids_file:
    df_programs = pd.read_csv(program_file)
    df_kids = pd.read_csv(kids_file)

    kids_preferences = {}
    for idx, row in df_kids.iterrows():
        kid_name = row[0]
        prefs = [p for p in row[1:] if pd.notna(p)]
        kids_preferences[kid_name] = prefs

    assignments = assign_programs_with_times(kids_preferences, df_programs, max_programs_per_kid)

    # --- Display Assignments ---
    st.subheader("Assignments")
    for kid, progs in assignments.items():
        st.markdown(f"- **{kid}**: {', '.join(progs) if progs else 'No assignment'}")

    # --- Download CSV ---
    st.subheader("Download Assignments CSV")
    download_df = pd.DataFrame({
        'KidName': list(assignments.keys()),
        'AssignedPrograms': [', '.join(v) for v in assignments.values()]
    })
    csv = download_df.to_csv(index=False)
    st.download_button(label="Download CSV", data=csv, file_name="assignments.csv", mime="text/csv")
