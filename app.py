import streamlit as st
import pandas as pd
import random

# --- Language Toggle ---
language = st.sidebar.radio("Language / 語言", ("English", "繁體中文"))

# --- Define text based on language ---
if language == "English":
    title = "Extracurricular Program Assignment"
    subtitle = "Assign kids to programs based on preferences, capacities, and time slots"
    upload_logo = "Upload School Logo (optional)"
    upload_programs = "Upload Programs CSV"
    upload_programs_info = "CSV format: ProgramName, Capacity, Day, TimeSlot(1,2,3)"
    upload_kids = "Upload Kids Preferences CSV"
    upload_kids_info = "CSV format: KidName, Preference1, Preference2, Preference3..."
    max_programs_text = "Max Programs per Kid"
    time_slot_ref = "Time Slots Reference"
    assignments_text = "Assignments"
    download_text = "Download Assignments CSV"
    download_button_label = "Download CSV"
else:
    title = "課外活動分配系統"
    subtitle = "根據偏好、名額與時段分配孩子到活動"
    upload_logo = "上傳校徽 (可選)"
    upload_programs = "上傳活動 CSV"
    upload_programs_info = "CSV 格式: ProgramName, Capacity, Day, TimeSlot(1,2,3)"
    upload_kids = "上傳學生偏好 CSV"
    upload_kids_info = "CSV 格式: KidName, Preference1, Preference2, Preference3..."
    max_programs_text = "每位學生最多可分配活動數"
    time_slot_ref = "時段對照表"
    assignments_text = "分配結果"
    download_text = "下載分配結果 CSV"
    download_button_label = "下載 CSV"

# --- Upload Logo at top ---
logo_file = st.file_uploader(upload_logo, type=["png", "jpg", "jpeg"])
if logo_file:
    st.image(logo_file, use_column_width=False, width=250, output_format="PNG", caption="")

# --- Page Title ---
st.markdown(f"<h1 style='text-align: center; color: #2E86C1;'>{title}</h1>", unsafe_allow_html=True)
st.markdown(f"<h5 style='text-align: center; color: #555;'>{subtitle}</h5>", unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar Settings ---
st.sidebar.subheader(max_programs_text)
max_programs_per_kid = st.sidebar.number_input(max_programs_text, min_value=1, value=1)

# Time slots
time_slot_mapping = {1: "12:50-2:20", 2: "2:20-3:50", 3: "Undefined"}
st.sidebar.subheader(time_slot_ref)
for k, v in time_slot_mapping.items():
    st.sidebar.write(f"{k}: {v}")

# --- File Uploads ---
st.subheader(upload_programs)
st.markdown(upload_programs_info)
program_file = st.file_uploader("", type=["csv"], key="programs_file")

st.subheader(upload_kids)
st.markdown(upload_kids_info)
kids_file = st.file_uploader("", type=["csv"], key="kids_file")

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

# --- Assign colors to programs ---
def get_program_colors(program_names):
    palette = ['#FF9999','#99FF99','#9999FF','#FFD699','#FF99FF','#99FFFF','#FFCC99','#CCFF99','#99CCFF','#FF6666']
    colors = {}
    for i, prog in enumerate(program_names):
        colors[prog] = palette[i % len(palette)]
    return colors

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

    # Get unique program names for colors
    program_names = df_programs['ProgramName'].unique()
    program_colors = get_program_colors(program_names)

    # --- Display Assignments with colors ---
    st.subheader(assignments_text)
    for kid, progs in assignments.items():
        colored_progs = []
        for p in progs:
            prog_name = p.split(" ")[0]
            color = program_colors.get(prog_name, "#CCCCCC")
            colored_progs.append(f"<span style='background-color:{color};padding:3px;border-radius:3px;'>{p}</span>")
        st.markdown(f"- **{kid}**: {' '.join(colored_progs)}", unsafe_allow_html=True)

    # --- Download CSV ---
    st.subheader(download_text)
    download_df = pd.DataFrame({
        'KidName': list(assignments.keys()),
        'AssignedPrograms': [', '.join(v) for v in assignments.values()]
    })
    csv = download_df.to_csv(index=False)
    st.download_button(label=download_button_label, data=csv, file_name="assignments.csv", mime="text/csv")
