import streamlit as st
import pandas as pd
import random
from PIL import Image

# ---------------- Logo ----------------
logo = Image.open("logo.png")  # Place logo.png in same folder
st.image(logo, width=250)  # fixed width

# ---------------- Language Toggle ----------------
language = st.sidebar.radio("Language / 語言", ("English", "繁體中文"))

# ---------------- UI Text ----------------
if language == "English":
    title = "Extracurricular Program Assignment"
    subtitle = "Assign kids to programs based on preferences, capacities, and time slots"
    upload_programs = "Upload Programs CSV"
    upload_programs_info = "CSV format: ProgramName, Capacity, Day, TimeSlot(1,2,3)"
    upload_kids = "Upload Kids Preferences CSV"
    upload_kids_info = "CSV format: KidName, Preference1, Preference2, Preference3..."
    max_programs_text = "Max Programs per Kid"
    assignments_text = "Assignments"
    download_text = "Download Assignments CSV"
    saved_file_text = "Load Previous Assignments (optional)"
    download_button_label = "Download CSV"
    preview_text = "Preview of Uploaded File"
    filters_text = "Filters"
    summary_text = "Summary Statistics"
    compact_sidebar_text = "Compact Mode (hide sidebar)"
else:
    title = "課外活動分配系統"
    subtitle = "根據偏好、名額與時段分配孩子到活動"
    upload_programs = "上傳活動 CSV"
    upload_programs_info = "CSV 格式: ProgramName, Capacity, Day, TimeSlot(1,2,3)"
    upload_kids = "上傳學生偏好 CSV"
    upload_kids_info = "CSV 格式: KidName, Preference1, Preference2, Preference3..."
    max_programs_text = "每位學生最多可分配活動數"
    assignments_text = "分配結果"
    download_text = "下載分配結果 CSV"
    saved_file_text = "載入先前分配結果 (可選)"
    download_button_label = "下載 CSV"
    preview_text = "上傳檔案預覽"
    filters_text = "篩選條件"
    summary_text = "統計摘要"
    compact_sidebar_text = "簡潔模式 (隱藏側邊欄)"

# ---------------- Page Title ----------------
st.markdown(f"<h1 style='text-align: center; color: #2E86C1;'>{title}</h1>", unsafe_allow_html=True)
st.markdown(f"<h5 style='text-align: center; color: #555;'>{subtitle}</h5>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- Compact Mode Toggle ----------------
compact_mode = st.sidebar.checkbox(compact_sidebar_text, value=False)
if compact_mode:
    st.markdown("<style>section[data-testid='stSidebar']{display:none;}</style>", unsafe_allow_html=True)

# ---------------- Collapsible Instructions ----------------
with st.expander("How the Program Works / 如何運作", expanded=True):
    if language == "English":
        st.markdown("""
### Overview
This app assigns kids to extracurricular programs based on their preferences, program capacities, and time slots.

### Rules
1. Each kid can list multiple program preferences.
2. Programs have limited capacities per time slot.
3. Assignments are done by preference ranking and random selection if multiple kids want the same program.
4. **Conflict-free scheduling**: A kid will not be assigned to two programs that overlap in the same time slot.

### How Results Are Displayed
- Assignments are **shown on-screen** with color coding.
- Tap a program to see day, slot, and preference rank (works on mobile).
- The table is **searchable and sortable**.
- Users can **download results as CSV**.
        """)
    else:
        st.markdown("""
### 簡介
本應用程式根據學生偏好、活動名額與時段將學生分配到課外活動。

### 規則
1. 每個孩子可以列出多個活動偏好。
2. 每個活動在每個時段有固定名額。
3. 分配依偏好順序進行，若多個孩子想選同一活動，將隨機抽籤分配。
4. **避免時間衝突**: 孩子不會被分配到同一時段有衝突的兩個活動。

### 結果顯示方式
- 分配結果會**顯示在螢幕上**，每個活動用顏色區分。
- 點擊活動查看時段與偏好 (手機也可用)。
- 表格**可搜索及排序**。
- 用戶可**下載 CSV 檔案**儲存進度。
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

st.subheader(saved_file_text)
saved_file = st.file_uploader("", type=["csv"], key="saved_file")

# ---------------- CSV Preview ----------------
def preview_file(file):
    try:
        df = pd.read_csv(file)
        st.write(preview_text)
        st.dataframe(df.head(), use_container_width=True)
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
        key = (row['ProgramName'], row['Day'], int(row['TimeSlot']))
        program_slots[key] = row['Capacity']

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

# ---------------- Main Logic ----------------
if saved_file:
    df_assignments = pd.read_csv(saved_file)
    st.subheader("Loaded Previous Assignments")
    st.dataframe(df_assignments, use_container_width=True)
elif df_programs is not None and df_kids is not None:
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
    display_df = pd.DataFrame(table_rows)

    # Filters
    st.sidebar.subheader(filters_text)
    filter_day = st.sidebar.multiselect("Filter by Day", options=display_df['Day'].unique(), default=display_df['Day'].unique())
    filter_program = st.sidebar.multiselect("Filter by Program", options=display_df['Program'].unique(), default=display_df['Program'].unique())
    filtered_df = display_df[(display_df['Day'].isin(filter_day)) & (display_df['Program'].isin(filter_program))]

    # Display Table
    st.subheader(assignments_text)
    st.dataframe(filtered_df[['Kid','Program','Details']], use_container_width=True)

    # Summary
    st.subheader(summary_text)
    program_fill = filtered_df.groupby('Program').size().reset_index(name='AssignedCount')
    program_fill = program_fill.merge(df_programs[['ProgramName','Capacity']], left_on='Program', right_on='ProgramName', how='left')
    program_fill['FillRate'] = program_fill['AssignedCount'] / program_fill['Capacity']
    st.dataframe(program_fill[['Program','AssignedCount','Capacity','FillRate']], use_container_width=True)

    # ---------------- Download CSV ----------------
    st.subheader(download_text)
    csv_download_df = filtered_df.drop(columns=['Details'])
    csv = csv_download_df.to_csv(index=False)
    st.download_button(label=download_button_label, data=csv, file_name="assignments.csv", mime="text/csv")
