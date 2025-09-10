import streamlit as st
import pandas as pd
import random
from io import BytesIO

# -------------------- Page Setup --------------------
st.set_page_config(page_title="Student Club Assignment Lottery", layout="wide")

# -------------------- Logo --------------------
logo = st.file_uploader("Upload School Logo", type=["png","jpg","jpeg"])
if logo:
    st.image(logo, use_column_width=True, output_format="auto")

# -------------------- Language Toggle --------------------
language = st.radio("Select Language / 選擇語言", ["English", "繁體中文"])

def t(text_en, text_tc):
    return text_en if language == "English" else text_tc

# -------------------- Explanation Section --------------------
with st.expander(t("How it works / 使用說明", "操作說明")):
    st.markdown(t(
        """
**Student Club Assignment Lottery Rules**

1. Upload the **Students CSV**: Column headers must be `KidName, Preference1, Preference2, Preference3` (more preferences optional).
2. Upload the **Programs CSV**: Column headers must be `ProgramName, Capacity, Day, TimeSlot`.
3. Each student is assigned to programs based on their ranked preferences, respecting **max programs per student**.
4. Each program has limited capacity for each timeslot.
5. Results are displayed on screen and can be downloaded as CSV.
        """,
        """
**學生社團抽籤規則**

1. 上傳 **學生 CSV**: 欄位名稱必須是 `KidName, Preference1, Preference2, Preference3`（可有更多偏好欄位）。
2. 上傳 **社團 CSV**: 欄位名稱必須是 `ProgramName, Capacity, Day, TimeSlot`。
3. 系統會根據學生的偏好排序分配社團，並遵守每位學生的最大社團數限制。
4. 每個社團每個時段有容量限制。
5. 結果會顯示在頁面上，可下載 CSV。
        """
    ))

# -------------------- Max Programs per Kid --------------------
max_programs_per_kid = st.number_input(
    t("Max programs per student", "每位學生最多可分配社團數"),
    min_value=1, max_value=10, value=1, step=1
)

# -------------------- File Upload --------------------
students_file = st.file_uploader(t("Upload Students CSV", "上傳學生 CSV"), type="csv")
programs_file = st.file_uploader(t("Upload Programs CSV", "上傳社團 CSV"), type="csv")

if students_file and programs_file:
    try:
        # Load CSVs
        df_students = pd.read_csv(students_file)
        df_programs = pd.read_csv(programs_file)

        # Strip whitespace from column names
        df_students.columns = df_students.columns.str.strip()
        df_programs.columns = df_programs.columns.str.strip()

        # Validate required columns
        required_student_cols = ['KidName']
        required_program_cols = ['ProgramName','Capacity','Day','TimeSlot']

        missing_student = [c for c in required_student_cols if c not in df_students.columns]
        missing_program = [c for c in required_program_cols if c not in df_programs.columns]

        if missing_student:
            st.error(t(f"Students CSV is missing columns: {', '.join(missing_student)}",
                       f"學生 CSV 缺少欄位: {', '.join(missing_student)}"))
            st.stop()
        if missing_program:
            st.error(t(f"Programs CSV is missing columns: {', '.join(missing_program)}",
                       f"社團 CSV 缺少欄位: {', '.join(missing_program)}"))
            st.stop()

        # Ensure TimeSlot and Capacity are numeric
        df_programs['TimeSlot'] = pd.to_numeric(df_programs['TimeSlot'], errors='coerce')
        df_programs['Capacity'] = pd.to_numeric(df_programs['Capacity'], errors='coerce').fillna(0).astype(int)
        df_programs = df_programs.dropna(subset=['ProgramName','Day','TimeSlot','Capacity'])

        # -------------------- Assignment Function --------------------
        def assign_programs_with_times(students_df, programs_df, max_per_student=1):
            assignments = []
            slot_fill = {}
            # Track how many programs each student has been assigned
            student_counts = {student:0 for student in students_df['KidName']}

            # Determine max number of preference rounds
            max_prefs = max([len([c for c in students_df.columns if c.startswith('Preference')])])

            for pref_round in range(1, max_prefs+1):
                pref_col = f'Preference{pref_round}'
                for _, student in students_df.iterrows():
                    student_name = student['KidName']
                    if student_counts[student_name] >= max_per_student:
                        continue  # already reached max programs
                    if pref_col not in student or pd.isna(student[pref_col]):
                        continue  # no preference for this round
                    program_name = student[pref_col]
                    matched_programs = programs_df[programs_df['ProgramName']==program_name]
                    assigned = False
                    for _, prog_row in matched_programs.iterrows():
                        key = (prog_row['ProgramName'], prog_row['Day'], int(prog_row['TimeSlot']))
                        filled = slot_fill.get(key, 0)
                        if filled < prog_row['Capacity']:
                            assignments.append({
                                "KidName": student_name,
                                "ProgramName": prog_row['ProgramName'],
                                "Day": prog_row['Day'],
                                "TimeSlot": prog_row['TimeSlot']
                            })
                            slot_fill[key] = filled + 1
                            student_counts[student_name] += 1
                            assigned = True
                            break  # move to next student
            return pd.DataFrame(assignments)

        # -------------------- Generate Assignments --------------------
        df_assignments = assign_programs_with_times(df_students, df_programs, max_programs_per_kid)

        # -------------------- Display & Download --------------------
        st.subheader(t("Assignment Results", "分配結果"))
        st.dataframe(df_assignments)

        csv_buffer = BytesIO()
        df_assignments.to_csv(csv_buffer, index=False)
        st.download_button(
            label=t("Download Results CSV", "下載結果 CSV"),
            data=csv_buffer,
            file_name="assignment_results.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(t(f"Error processing files: {e}", f"處理檔案時發生錯誤: {e}"))
