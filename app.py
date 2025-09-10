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
1. Each student lists up to 3 preferences for clubs.
2. Each club has a limited number of slots for each day/time.
3. Assignments are processed in rounds by **preference ranking**:
   - Round 1: Try to assign all students to their first preference.
   - Round 2: Assign remaining students to their second preference if available.
   - Round 3: Assign remaining students to their third preference if available.
4. If more students request a club than there are slots, **random selection** is used.
5. Students cannot be assigned to two clubs that overlap in the same time slot.
6. A student can be assigned up to the **maximum programs per student** as set in the sidebar.

### Results
- Assignments are displayed on screen in a scrollable table.
- Each row represents one student/program assignment.
- You can download the results as a CSV file to save your assignments.
        """)
    else:
        st.markdown("""
### 簡介
抽籤系統根據學生提交的偏好、社團名額與時段，將學生分配到社團。

### 抽籤流程
1. 每位學生最多列出三個社團偏好。
2. 每個社團在每個時段有固定名額。
3. 分配依偏好順序進行：
   - 第一輪：盡量將學生分配到第一偏好。
   - 第二輪：將未分配的學生分配到第二偏好（若名額允許）。
   - 第三輪：將未分配的學生分配到第三偏好（若名額允許）。
4. 若申請人數超過社團名額，將以**隨機抽籤**決定分配。
5. 學生不可被分配到同一時段有衝突的兩個社團。
6. 每位學生最多可被分配到**側邊欄設定的最大社團數**。

### 結果
- 分配結果會在螢幕上以可滾動表格顯示。
- 每一行表示一個學生與社團的分配。
- 可下載 CSV 文件以保存分配結果。
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
    assigned_programs = {kid: [] for kid in kids_prefs}
    program_slots = {}
    for _, row in programs_df.iterrows():
        key = (row['programname'], row['day'], int(row['timeslot']))
        program_slots[key] = row['capacity']

    max_rank = max(len(prefs) for prefs in kids_prefs.values())
    for rank in range(max_rank):
        applicants_per_program = {}
        for kid, prefs in kids_prefs.items():
            if len(assigned_programs[kid]) >= max_per_kid:
                continue
            if rank < len(prefs):
                occupied_slots = [a.split("slot ")[-1].replace(")","") for a in assigned_programs[kid]]
                available_slots = [
                    k for k in program_slots 
                    if k[0] == prefs[rank] and program_slots[k] > 0 and str(k[2]) not in occupied_slots
                ]
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
