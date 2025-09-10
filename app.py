import streamlit as st
import pandas as pd
import random
from PIL import Image

# ---------------- Logo (centered) ----------------
logo = Image.open("logo.png")  # Place logo.png in the same folder as app.py
st.image(logo, width=250)  # centers naturally

# ---------------- Language Toggle ----------------
language = st.sidebar.radio("Language / 語言", ("English", "繁體中文"))

# ---------------- UI Text ----------------
if language == "English":
    title = "Student Club Assignment Lottery"
    subtitle = "Assign kids to programs based on preferences, capacities, and time slots"
    upload_programs = "Upload Programs CSV"
    upload_programs_info = "CSV format: ProgramName, Capacity, Day, Timeslot"
    upload_kids = "Upload Kids Preferences CSV"
    upload_kids_info = "CSV format: KidName, Preference1, Preference2, Preference3..."
    max_programs_text = "Max Programs per Kid"
    assignments_text = "Assignments"
    download_text = "Download Assignments CSV"
    download_button_label = "Download CSV"
    preview_text = "Preview of Uploaded File"
else:
    title = "學生社團分配抽籤系統"
    subtitle = "根據偏好、名額與時段分配學生到社團活動"
    upload_programs = "上傳社團活動 CSV"
    upload_programs_info = "CSV 格式: ProgramName, Capacity, Day, Timeslot"
    upload_kids = "上傳學生偏好 CSV"
    upload_kids_info = "CSV 格式: KidName, Preference1, Preference2, Preference3..."
    max_programs_text = "每位學生最多可分配社團數"
    assignments_text = "分配結果"
    download_text = "下載分配結果 CSV"
    download_button_label = "下載 CSV"
    preview_text = "上傳檔案預覽"

# ---------------- Page Title ----------------
st.markdown(f"<h1 style='text-align: center; color: #2E86C1;'>{title}</h1>", unsafe_allow_html=True)
st.markdown(f"<h5 style='text-align: center; color: #555;'>{subtitle}</h5>", unsafe_allow_html=True)
st.markdown("---")
# ---------------- Explanation Collapsible ----------------
with st.expander("How the Student Club Assignment Lottery Works / 學生社團抽籤系統說明", expanded=False):
    if language == "English":
        st.markdown("""
### Overview
The lottery assigns students to clubs based on their submitted preferences, club capacities, and time slots.

### How the Draw Works
- Each student can list multiple preferences for clubs (not limited to 3 — the system uses however many `Preference` columns are included in the student CSV).
- Each club has a limited number of slots for each day/time.
- Assignments are processed in rounds by preference ranking:
  - Round 1: Try to assign all students to their first preference.
  - Round 2: Assign remaining students to their second preference if available.
  - Round 3 and beyond: Continue processing additional preference columns in order.
- If more students request a club than there are slots, random selection is used.
- Students cannot be assigned to two clubs that overlap in the same time slot.
- A student can be assigned up to the maximum number of programs per student, as set in the sidebar.

### Results
- Assignments are displayed on screen in a scrollable table.
- Each row represents one student/program assignment.
- You can download the results as a CSV file to save your assignments.
        """)
    else:
        st.markdown("""
### 簡介
抽籤系統會依照學生填寫的偏好、社團名額與時段，將學生分配到社團。

### 抽籤方式
- 每位學生可填寫多個社團偏好（不限於 3 個，系統會依 CSV 中的 `Preference` 欄位數量進行處理）。
- 每個社團在各時段有固定名額。
- 分配依偏好順序分回合進行：
  - 第 1 回合：盡量將所有學生分配到第一志願。
  - 第 2 回合：將未分配的學生分配到第二志願（若有空位）。
  - 第 3 回合及之後：依序處理更多偏好欄位。
- 若同一社團申請人數超過名額，將以隨機方式抽籤。
- 學生不會被分配到同一時段重疊的兩個社團。
- 每位學生最多可被分配到的社團數量，由側邊欄設定。

### 結果
- 分配結果會顯示在螢幕上的可捲動表格中。
- 每一列代表一位學生的一個社團分配。
- 您可以下載結果為 CSV 檔，以便儲存或分享。
        """)

# ---------------- Sidebar Settings ----------------
st.sidebar.subheader(max_programs_text)
max_programs_per_kid = st.sidebar.number_input(max_programs_text, min_value=1, value=1)

# ---------------- Time Slot Table ----------------
time_slot_mapping = {1: "12:50-2:20", 2: "2:20-3:50", 3: "Undefined"}
st.subheader("Time Slots / 時段對照")
time_slots_df = pd.DataFrame([
    ["Monday", time_slot_mapping[1], time_slot_mapping[2], time_slot_mapping[3]],
    ["Tuesday", time_slot_mapping[1], time_slot_mapping[2], time_slot_mapping[3]],
    ["Wednesday", time_slot_mapping[1], time_slot_mapping[2], time_slot_mapping[3]],
    ["Thursday", time_slot_mapping[1], time_slot_mapping[2], time_slot_mapping[3]],
    ["Friday", time_slot_mapping[1], time_slot_mapping[2], time_slot_mapping[3]],
], columns=["Day","Slot 1","Slot 2","Slot 3"])
st.table(time_slots_df)

# ---------------- File Uploads ----------------
st.subheader(upload_programs)
st.markdown(upload_programs_info)
program_file = st.file_uploader("", type=["csv"], key="programs_file")

st.subheader(upload_kids)
st.markdown(upload_kids_info)
kids_file = st.file_uploader("", type=["csv"], key="kids_file")

# ---------------- CSV Preview Function ----------------
def preview_file(file):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()  # normalize columns
        st.write(preview_text)
        st.dataframe(df, use_container_width=True)
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None

df_programs = preview_file(program_file) if program_file else None
df_kids = preview_file(kids_file) if kids_file else None

# ---------------- Assignment Function ----------------
def assign_programs_with_times(kids_prefs, programs_df, max_per_kid=1):
    """
    Assign students to programs based on their preferences, program capacities, and time slots.
    Logic:
    - Each student can have up to `max_per_kid` programs.
    - Assignments processed by preference rank.
    - Random draw if more students request a program than available slots.
    - Students cannot be assigned to overlapping time slots.
    """
    assigned_programs = {kid: [] for kid in kids_prefs}  # {kid_name: [assigned_program strings]}
    program_slots = {}  # {(ProgramName, Day, TimeSlot): remaining_capacity}
    for _, row in programs_df.iterrows():
        key = (row['programname'], row['day'], int(row['timeslot']))
        program_slots[key] = row['capacity']
        
# ---------------- Filter out invalid preferences ----------------
    valid_program_names = set(programs_df['programname'])
    for kid, prefs in kids_prefs.items():
        kids_prefs[kid] = [p for p in prefs if p in valid_program_names]
        
    max_rank = max(len(prefs) for prefs in kids_prefs.values())

    # Continue looping until no one can be assigned more or programs are full
    assignments_remaining = True
    while assignments_remaining:
        assignments_remaining = False  # assume done unless we assign someone this round
        for rank in range(max_rank):
            applicants_per_program = {}
            for kid, prefs in kids_prefs.items():
                # Skip if student already reached max programs
                if len(assigned_programs[kid]) >= max_per_kid:
                    continue
                # Skip if student doesn't have a preference for this rank
                if rank >= len(prefs):
                    continue
                pref_program = prefs[rank]

                # Determine which slots this student can take without conflict
                # Track occupied day and slot pairs
occupied_slots = [
    (a.split("(")[1].split(" ")[0], int(a.split("slot ")[1].replace(")","")))
    for a in assigned_programs[kid]
]

# Check for programs in the student's preferences that are actually available
available_slots = [
    k for k in program_slots
    if k[0] == prefs[rank] and program_slots[k] > 0 and (k[1], k[2]) not in occupied_slots
]
# Check for programs in the student's preferences that are actually available
available_slots = [
    k for k in program_slots
    if k[0] == prefs[rank] and program_slots[k] > 0 and (k[1], k[2]) not in occupied_slots
]
                if available_slots:
                    assignments_remaining = True
                    chosen_slot = random.choice(available_slots)
                    applicants_per_program.setdefault(chosen_slot, []).append(kid)

            # Assign students randomly if too many applicants
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

# ---------------- Generate Button ----------------
if st.button("Generate Assignments / 生成分配"):
    if df_programs is not None and df_kids is not None:
        required_program_cols = ['programname','capacity','day','timeslot']
        missing_cols = [c for c in required_program_cols if c not in df_programs.columns]
        if missing_cols:
            st.error(f"Programs CSV is missing required columns: {missing_cols}")
        else:
            kids_preferences = {row[0]: [p for p in row[1:] if pd.notna(p)] for _, row in df_kids.iterrows()}
            assignments = assign_programs_with_times(kids_preferences, df_programs, max_programs_per_kid)

            table_rows = []
            for kid, progs in assignments.items():
                for p in progs:
                    prog_name = p.split(" ")[0]
                    day = p.split("(")[1].split(" ")[0]
                    slot = int(p.split("slot ")[1].replace(")",""))
                    prefs = kids_preferences[kid]
                    rank = prefs.index(prog_name)+1 if prog_name in prefs else 3
                    table_rows.append({
                        'Kid': kid,
                        'Program': prog_name,
                        'Day': day,
                        'TimeSlot': slot,
                        'PreferenceRank': rank,
                        'Details': f"Day: {day}, Slot: {slot}, Preference: {rank}"
                    })
            display_df = pd.DataFrame(table_rows).sort_values(by='Kid')

            st.subheader(assignments_text)
            st.dataframe(display_df[['Kid','Program','Details']], use_container_width=True)

            # Summary
            st.subheader("Summary Statistics / 統計摘要")
            program_fill = display_df.groupby('Program').size().reset_index(name='AssignedCount')
            program_fill = program_fill.merge(
                df_programs[['programname','capacity']], left_on='Program', right_on='programname', how='left'
            )
            program_fill['FillRate'] = program_fill['AssignedCount'] / program_fill['capacity']
            st.dataframe(program_fill[['Program','AssignedCount','capacity','FillRate']], use_container_width=True)

            # Download CSV
            st.subheader(download_text)
            csv_download_df = display_df.drop(columns=['Details'])
            st.download_button(
                label=download_button_label,
                data=csv_download_df.to_csv(index=False),
                file_name="assignments.csv",
                mime="text/csv"
            )
    else:
        st.error("Please upload both Programs and Kids CSV files before generating assignments.")
