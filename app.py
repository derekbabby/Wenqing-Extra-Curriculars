import streamlit as st
import pandas as pd
import random
from PIL import Image
import unicodedata

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
- Each student can list multiple preferences for clubs (not limited to 3).
- Each club has a limited number of slots for each day/time.
- Assignments are processed in rounds by preference ranking.
- If more students request a club than there are slots, random selection is used.
- Students cannot be assigned to two clubs that overlap in the same time slot.
- A student can be assigned up to the maximum number of programs per student, as set in the sidebar.

### Results
- Assignments are displayed on screen.
- You can download the results as a CSV file.
        """)
    else:
        st.markdown("""
### 簡介
抽籤系統會依照學生填寫的偏好、社團名額與時段，將學生分配到社團。

### 抽籤方式
- 每位學生可填寫多個社團偏好（不限於 3 個）。
- 每個社團在各時段有固定名額。
- 分配依偏好順序分回合進行。
- 若同一社團申請人數超過名額，將以隨機方式抽籤。
- 學生不會被分配到同一時段重疊的兩個社團。
- 每位學生最多可被分配到的社團數量，由側邊欄設定。

### 結果
- 分配結果會顯示在螢幕上。
- 您可以下載結果為 CSV 檔。
        """)

# ---------------- Usage Instructions Collapsible ----------------
with st.expander("How to Use the System / 系統使用說明", expanded=False):
    if language == "English":
        st.markdown("""
### Step 1: Prepare Programs CSV
- CSV must include the following columns: `ProgramName`, `Capacity`, `Day`, `Timeslot`.
- `ProgramName`: Name of the club/program (case-insensitive).
- `Capacity`: Maximum number of students allowed in the program.
- `Day`: Weekday (Monday, Tuesday, etc.).
- `Timeslot`: Slot number (1, 2, 3), corresponding to the time slot table shown above.
- Make sure there are no extra spaces in the program names.

### Step 2: Prepare Kids Preferences CSV
- First column: `KidName`.
- Remaining columns: `Preference1`, `Preference2`, etc. (number of preferences can vary per student).
- Preferences must match the program names in the Programs CSV (case-insensitive, whitespace ignored).

### Step 3: Upload Files
- Upload Programs CSV first, then Kids Preferences CSV.
- You will see a preview of each uploaded file.

### Step 4: Set Max Programs and Random Seed
- In the sidebar, set “Max Programs per Kid” (default 1).
- Optional: Set a Random Seed for reproducibility.

### Step 5: Generate Assignments
- Click “Generate Assignments” button.
- Assignments will appear in a scrollable table.
- You can download the results as a CSV.

### Tips
- Avoid typos in program names; use consistent spelling.
- Students will not be assigned to overlapping time slots.
- Random selection is used when too many students request the same program.
        """)
    else:
        st.markdown("""
### 步驟 1：準備社團活動 CSV
- CSV 必須包含欄位：`ProgramName`、`Capacity`、`Day`、`Timeslot`。
- `ProgramName`：社團名稱（不分大小寫）。
- `Capacity`：該社團最多可容納學生數。
- `Day`：星期幾（Monday, Tuesday 等）。
- `Timeslot`：時段編號（1, 2, 3），對應上方時段表。
- 確保社團名稱不要多餘空格。

### 步驟 2：準備學生偏好 CSV
- 第一欄：`KidName`。
- 後續欄位：`Preference1`, `Preference2` 等（每位學生可填多個）。
- 偏好必須與 Programs CSV 的社團名稱一致（不分大小寫，忽略空格）。

### 步驟 3：上傳檔案
- 先上傳 Programs CSV，再上傳 Kids Preferences CSV。
- 上傳後可看到檔案預覽。

### 步驟 4：設定每位學生最多分配社團數及隨機種子
- 在側邊欄設定 “每位學生最多可分配社團數”（預設 1）。
- 可選：設定隨機種子以重現相同分配結果。

### 步驟 5：生成分配結果
- 點擊 “生成分配” 按鈕。
- 分配結果將顯示在可捲動表格中。
- 可下載 CSV 保存結果。

### 小提示
- 避免社團名稱拼寫錯誤，保持一致。
- 學生不會被分配到同一時段重疊的社團。
- 當太多學生選擇同一社團時，系統將隨機抽籤。
        """)

# ---------------- Sidebar Settings ----------------
st.sidebar.subheader(max_programs_text)
max_programs_per_kid = st.sidebar.number_input(max_programs_text, min_value=1, value=1)

# Random Seed for reproducibility
st.sidebar.subheader("Random Seed / 隨機種子")
seed_value = st.sidebar.number_input("Set Seed (optional)", min_value=0, value=42, step=1)

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
        df.columns = df.columns.str.strip().str.lower()
        st.write(preview_text)
        st.dataframe(df, use_container_width=True)
        return df
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None

df_programs = preview_file(program_file) if program_file else None
df_kids = preview_file(kids_file) if kids_file else None

# ---------------- Helper to normalize names ----------------
def clean_name(name):
    return unicodedata.normalize("NFKC", str(name).strip())

# ---------------- Assignment Function ----------------
def assign_programs_with_times(kids_prefs, programs_df, max_per_kid=1):
    assigned_programs = {kid: [] for kid in kids_prefs}
    
    # Build available slots map
    program_slots = {}
    for _, row in programs_df.iterrows():
        key = (clean_name(row['programname']), clean_name(row['day']), int(row['timeslot']))
        program_slots[key] = int(row['capacity'])

    max_rank = max(len(prefs) for prefs in kids_prefs.values())

    assignments_remaining = True
    while assignments_remaining:
        assignments_remaining = False
        for rank in range(max_rank):
            applicants_per_slot = {}
            for kid, prefs in kids_prefs.items():
                if len(assigned_programs[kid]) >= max_per_kid:
                    continue
                if rank >= len(prefs):
                    continue

                pref_program = prefs[rank]
                occupied_slots = {(a['Day'], a['TimeSlot']) for a in assigned_programs[kid]}
                available_slots = [
                    k for k in program_slots
                    if k[0] == pref_program and program_slots[k] > 0 and (k[1], k[2]) not in occupied_slots
                ]
                if available_slots:
                    assignments_remaining = True
                    chosen_slot = random.choice(available_slots)
                    applicants_per_slot.setdefault(chosen_slot, []).append(kid)

            for slot_key, applicants in applicants_per_slot.items():
                remaining = program_slots[slot_key]
                eligible = [kid for kid in applicants if len(assigned_programs[kid]) < max_per_kid]
                if len(eligible) <= remaining:
                    for kid in eligible:
                        assigned_programs[kid].append({
                            'Program': slot_key[0],
                            'Day': slot_key[1],
                            'TimeSlot': slot_key[2],
                            'PreferenceRound': rank + 1
                        })
                        program_slots[slot_key] -= 1
                else:
                    selected = random.sample(eligible, remaining)
                    for kid in selected:
                        assigned_programs[kid].append({
                            'Program': slot_key[0],
                            'Day': slot_key[1],
                            'TimeSlot': slot_key[2],
                            'PreferenceRound': rank + 1
                        })
                        program_slots[slot_key] -= 1

    return assigned_programs

# ---------------- Generate Button ----------------
if st.button("Generate Assignments / 生成分配"):
    if df_programs is None or df_kids is None:
        st.error("Please upload both Programs and Kids CSV files before generating assignments.")
    else:
        required_cols = ['programname','capacity','day','timeslot']
        missing_cols = [c for c in required_cols if c not in df_programs.columns]
        if missing_cols:
            st.error(f"Programs CSV is missing required columns: {missing_cols}")
        else:
            # Set random seed
            random.seed(seed_value)

            # Clean and normalize names
            kids_preferences = {}
            for _, row in df_kids.iterrows():
                kid_name = clean_name(row[0])
                prefs = [clean_name(p) for p in row[1:] if pd.notna(p) and str(p).strip()]
                kids_preferences[kid_name] = prefs

            # Map valid program names
            valid_program_names = {clean_name(p): p for p in df_programs['programname']}
            for kid in kids_preferences:
                kids_preferences[kid] = [valid_program_names[p] for p in kids_preferences[kid] if p in valid_program_names]

            # Assign students
            assignments = assign_programs_with_times(kids_preferences, df_programs, max_programs_per_kid)

            # Build display DataFrame
            table_rows = []
            for kid, progs in assignments.items():
                prefs = kids_preferences[kid]
                for p in progs:
                    prog_name = p['Program']
                    day = p['Day']
                    slot = p['TimeSlot']
                    rank = prefs.index(prog_name)+1 if prog_name in prefs else None
                    table_rows.append({
                        'Kid': kid,
                        'Program': prog_name,
                        'Day': day,
                        'TimeSlot': slot,
                        'PreferenceRank': rank,
                        'PreferenceRound': p['PreferenceRound'],
                        'Details': f"Day: {day}, Slot: {slot}, PreferenceRank: {rank}, Round: {p['PreferenceRound']}"
            })
            display_df = pd.DataFrame(table_rows).sort_values(by='Kid')
            st.subheader(assignments_text)
            st.dataframe(display_df[['Kid','Program','Details']], use_container_width=True)

            # Summary Statistics
            st.subheader("Summary Statistics / 統計摘要")
            df_programs['programname_clean'] = df_programs['programname'].apply(clean_name)
            program_fill = display_df.groupby('Program').size().reset_index(name='AssignedCount')
            program_fill['Program_clean'] = program_fill['Program'].apply(clean_name)
            program_capacity_map = dict(zip(df_programs['programname_clean'], df_programs['capacity']))
            program_fill['Capacity'] = program_fill['Program_clean'].map(program_capacity_map)
            program_fill['FillRate'] = program_fill.apply(
                lambda row: row['AssignedCount'] / row['Capacity'] if row['Capacity'] > 0 else 0,
                axis=1
            )
            totals = pd.DataFrame([{
                'Program': 'Total',
                'AssignedCount': program_fill['AssignedCount'].sum(),
                'Capacity': program_fill['Capacity'].sum(),
                'FillRate': (program_fill['AssignedCount'].sum() / program_fill['Capacity'].sum()
                             if program_fill['Capacity'].sum() > 0 else 0)
            }])
            summary_df = pd.concat([program_fill[['Program','AssignedCount','Capacity','FillRate']], totals], ignore_index=True)
            st.dataframe(summary_df, use_container_width=True)

            # Download CSV
            st.subheader(download_text)
            csv_download_df = display_df.drop(columns=['Details'])
            st.download_button(
                label=download_button_label,
                data=csv_download_df.to_csv(index=False),
                file_name="assignments.csv",
                mime="text/csv"
            )
