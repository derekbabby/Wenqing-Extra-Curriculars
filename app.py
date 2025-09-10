import streamlit as st
import pandas as pd
import random

st.title("School Extracurricular Program Assignment")

st.markdown("""
Upload CSV files for kids and programs, then assign kids to programs based on their ranked preferences.
Each kid can get multiple programs (up to a specified number), and program capacities are enforced.
""")

# Sidebar inputs
max_programs_per_kid = st.sidebar.number_input("Max Programs per Kid", min_value=1, value=1)

# Upload programs CSV
st.subheader("Upload Programs CSV")
st.markdown("CSV format: ProgramName, Capacity")
program_file = st.file_uploader("Upload Programs CSV", type=["csv"])

# Upload kids CSV
st.subheader("Upload Kids Preferences CSV")
st.markdown("CSV format: KidName, Preference1, Preference2, Preference3...")
kids_file = st.file_uploader("Upload Kids CSV", type=["csv"])

# Function to assign programs
def assign_programs_multi(kids_prefs, prog_capacity, max_per_kid=1):
    assigned_programs = {kid: [] for kid in kids_prefs}
    program_slots = prog_capacity.copy()
    max_rank = max(len(prefs) for prefs in kids_prefs.values())

    for rank in range(max_rank):
        applicants_per_program = {}
        for kid, prefs in kids_prefs.items():
            if len(assigned_programs[kid]) >= max_per_kid:
                continue
            if rank < len(prefs):
                program = prefs[rank]
                applicants_per_program.setdefault(program, []).append(kid)

        for program, applicants in applicants_per_program.items():
            available = program_slots.get(program, 0)
            if available <= 0:
                continue
            unassigned_applicants = [kid for kid in applicants if len(assigned_programs[kid]) < max_per_kid]
            if len(unassigned_applicants) <= available:
                for kid in unassigned_applicants:
                    assigned_programs[kid].append(program)
                    program_slots[program] -= 1
            else:
                selected = random.sample(unassigned_applicants, available)
                for kid in selected:
                    assigned_programs[kid].append(program)
                    program_slots[program] -= 1
    return assigned_programs

# When both files are uploaded
if program_file and kids_file:
    # Read CSVs
    df_programs = pd.read_csv(program_file)
    df_kids = pd.read_csv(kids_file)

    # Convert to dicts
    program_capacity = dict(zip(df_programs['ProgramName'], df_programs['Capacity']))
    kids_preferences = {}
    for idx, row in df_kids.iterrows():
        kid_name = row[0]
        prefs = [p for p in row[1:] if pd.notna(p)]
        kids_preferences[kid_name] = prefs

    # Run assignment
    assignments = assign_programs_multi(kids_preferences, program_capacity, max_programs_per_kid)

    # Show results
    st.subheader("Assignments")
    for kid, progs in assignments.items():
        st.write(f"{kid}: {', '.join(progs) if progs else 'No assignment'}")

    # Allow download
    st.subheader("Download Assignments")
    download_df = pd.DataFrame({
        'KidName': list(assignments.keys()),
        'AssignedPrograms': [', '.join(v) for v in assignments.values()]
    })
    csv = download_df.to_csv(index=False)
    st.download_button(label="Download CSV", data=csv, file_name="assignments.csv", mime="text/csv")
