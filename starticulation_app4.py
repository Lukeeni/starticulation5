import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Tuple

# Define sound mastery ages (in months)
mastery_ages = {
    'h': 36, 'p': 36, 'm': 36, 'ŋ': 48, 'n': 36, 'w': 48, 'b': 36, 'k': 36, 'g': 36, 'd': 36, 't': 36,
    'j': 48, 'f': 48, 'ʒ': 72, 'l': 60, 'ʃ': 60, 'tʃ': 60, 's': 48, 'dʒ': 72, 'z': 60, 'r': 72, 'v': 60,
    'ð': 84, 'θ': 72,
    'sm': 84, 'sp': 84, 'sw': 84, 'sk': 84, 'sl': 84, 'sn': 84, 'st': 84,
    'bl': 84, 'fl': 84, 'pl': 84, 'br': 84, 'fr': 84, 'pr': 84, 'kw': 84, 'tw': 84,
    'gl': 84, 'kl': 84, 'dr': 84, 'gr': 84, 'kr': 84, 'tr': 84, 'θr': 84,
    'skr': 84, 'spr': 84, 'skw': 84, 'spl': 84
}

# Define positions for each sound
target_positions = {
    'tʃ': ['initial', 'medial', 'final'],
    'dʒ': ['initial', 'medial', 'final'],
    'ð': ['initial', 'medial']
}
for sound in mastery_ages:
    if sound not in target_positions:
        target_positions[sound] = ['initial', 'medial', 'final']

# Phonological processes/errors including frontal lisp
phonological_processes = {
    'backing': 'atypical', 'fronting': 36, 'gliding': 60, 'stopping': 48, 'vowelisation': 48, 'affrication': 48,
    'deaffrication': 48, 'alveolarization': 48, 'depalatisation': 48, 'labialisation': 48, 'assimilation': 36,
    'denasalisation': 48, 'final consonant devoicing': 60, 'prevocalic voicing': 48, 'coalescence': 36,
    'reduplication': 30, 'cluster reduction': 60, 'final consonant deletion': 48, 'initial consonant deletion': 'atypical',
    'weak syllable deletion': 48, 'epenthesis': 60, 'frontal lisp': 'atypical'
}

process_rules = [
    ('gliding', {'r': 'w', 'l': 'w'}),
    ('fronting', {'k': 't', 'g': 'd', 'ŋ': 'n'}),
    ('backing', {'t': 'k', 'd': 'g', 'n': 'ŋ'}),
    ('stopping', {
        'f': ['p', 'b'], 'v': ['b', 'p'], 's': ['t', 'd'], 'z': ['d', 't'], 'ʃ': ['t', 'd'],
        'ʒ': ['d', 't'], 'θ': ['t'], 'ð': ['d']
    }),
    ('deaffrication', {'tʃ': 'ʃ', 'dʒ': 'ʒ'}),
    ('affrication', {'ʃ': 'tʃ', 'ʒ': 'dʒ'}),
    ('labialisation', {'t': 'p', 'd': 'b'}),
    ('alveolarization', {'f': 's', 'v': 'z'}),
    ('depalatisation', {'ʃ': 's', 'ʒ': 'z'}),
    ('final consonant devoicing', {'b': 'p', 'd': 't', 'g': 'k', 'v': 'f', 'z': 's'}),
    ('prevocalic voicing', {'p': 'b', 't': 'd', 'k': 'g'}),
    ('frontal lisp', {'s': 'θ', 'ð': 'z'})
]

def detect_process(target, produced):
    for process, rules in process_rules:
        if isinstance(rules, dict):
            if target in rules:
                if (isinstance(rules[target], list) and produced in rules[target]) or (rules[target] == produced):
                    return process
    return None

def get_age_in_months(age_str: str) -> int:
    try:
        years, months = age_str.split(';')
        return int(years) * 12 + int(months)
    except:
        return 0

st.set_page_config(page_title="Starticulation Assessment", layout="wide")
st.title("Starticulation Articulation Assessment")

with st.expander("Welcome Message and Instructions", expanded=True):
    st.markdown("""
    Welcome to Starticulation, a tool for assessing consonant articulation. Starticulation is made by speech pathologists, for speech pathologists.

    HOW TO USE: Fill in each box with the actual sound produced by the child. Target boxes are filled in by default. For example, if the child produces the /p/ sound accurately, leave the boxes unchanged.

    It is important for the speech pathologist to do their due diligence in determining if phonological processes such as Cluster Reduction are present.

    To report bugs and suggestions, please email lakestundun@gmail.com.
    """)

if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = False

child_name = st.text_input("Child's First Name")
age_input = st.text_input("Child's Age (e.g., 4;6 for 4 years 6 months)")
age_in_months = get_age_in_months(age_input)

ordered_sounds = list(mastery_ages.keys())

if child_name and age_in_months:
    st.header("Articulation Assessment")

    records = []
    for sound in ordered_sounds:
        for pos in ['initial', 'medial', 'final']:
            if pos in target_positions[sound]:
                records.append({"Sound": sound, "Position": pos.title(), "Produced": sound})

    df = pd.DataFrame(records)
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    st.subheader("Assessment Results")
    results = []
    delayed = []
    age_appropriate_incorrect = []
    correct = []
    process_records = []

    for _, row in edited_df.iterrows():
        sound = row["Sound"]
        pos = row["Position"]
        produced = row["Produced"].strip()
        mastery_age = mastery_ages[sound]
        if produced == sound:
            results.append((sound, pos, "Age Appropriate"))
            correct.append(f"/{sound}/ ({pos})")
        else:
            process = detect_process(sound, produced)
            if process:
                status = phonological_processes.get(process)
                if status == 'atypical' or (isinstance(status, int) and age_in_months >= status):
                    process_records.append((process, sound, produced, 'Delayed'))
                else:
                    process_records.append((process, sound, produced, 'Age Appropriate'))

            if age_in_months >= mastery_age:
                results.append((sound, pos, "Delayed"))
                delayed.append(f"/{sound}/ ({pos})")
            else:
                results.append((sound, pos, "Incorrect but Age Appropriate"))
                age_appropriate_incorrect.append(f"/{sound}/ ({pos})")

    color_map = {
        "Age Appropriate": "#d4edda",
        "Incorrect but Age Appropriate": "#ffe082",
        "Delayed": "#f8d7da"
    }

    def highlight_result(val):
        return f"background-color: {color_map[val]}; color: black;"

    result_df = pd.DataFrame(results, columns=["Sound", "Position", "Result"])
    styled_table = result_df.style.applymap(lambda v: highlight_result(v) if v in color_map else "").to_html()
    st.markdown(styled_table, unsafe_allow_html=True)

    if process_records:
        st.subheader("Detected Phonological Processes")
        proc_df = pd.DataFrame(process_records, columns=["Process", "Target", "Produced", "Status"])
        styled_proc = proc_df.style.applymap(lambda v: highlight_result(v) if v in color_map else "").to_html()
        st.markdown(styled_proc, unsafe_allow_html=True)

    st.subheader("Summary Report")
    delayed_html = ''.join([f'<span style="background-color:{color_map["Delayed"]}; color:black; padding: 2px 5px; border-radius: 3px;">{s}</span> ' for s in delayed]) or "none"
    age_app_html = ''.join([f'<span style="background-color:{color_map["Incorrect but Age Appropriate"]}; color:black; padding: 2px 5px; border-radius: 3px;">{s}</span> ' for s in age_appropriate_incorrect]) or "none"
    summary = f"""
    <div style='font-size:16px;'>
    The following report summarises the findings of <strong>{child_name}</strong>.<br><br>
    The following sounds in {child_name}'s speech were produced incorrectly, and are considered <strong>delayed</strong> for their age:<br>
    {delayed_html}<br><br>
    The following sounds were produced incorrectly, but are still considered <strong>age appropriate</strong>:<br>
    {age_app_html}
    </div>
    """
    st.markdown(summary, unsafe_allow_html=True)

    csv = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name=f"{child_name}_articulation_results.csv",
        mime='text/csv'
    )
