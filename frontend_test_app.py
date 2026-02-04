import streamlit as st
import pandas as pd
import requests
import json
import os

st.set_page_config(layout="wide")

@st.cache_data
def load_questions():
    try:
        df = pd.read_csv('references.csv', sep='__', encoding='cp1252')
        questions = df['TestQuestion'].dropna().unique()[:2]
        return [str(q).strip() for q in questions.tolist()]
    except Exception as e:
        st.error(f"Error loading references.csv: {e}")
        return [
            "_Marcel has recently started work in the sales department of a global international. It is his first position working virtually and will be based for most of the year in a remote part of the USA. He has never met his other colleagues in the team and is not sure how to overcome feelings of isolation. Think of at least three ways that Marcel can get to know his colleagues within the sales team and build relations with them.",
            "Write an email to a friend suggesting how to reduce the use of technology."
        ]

def display_scores(result):
    ok_score = float(result.get("OK", 0.0))
    good_score = float(result.get("GOOD", 0.0))
    bad_score = float(result.get("BAD", 0.0))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div style="text-align: center; font-size: 28px; font-weight: bold; color: #ffc107;">OK</div><div style="text-align: center; font-size: 24px;">{ok_score:.2f}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="text-align: center; font-size: 28px; font-weight: bold; color: #28a745;">GOOD</div><div style="text-align: center; font-size: 24px;">{good_score:.2f}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div style="text-align: center; font-size: 28px; font-weight: bold; color: #dc3545;">BAD</div><div style="text-align: center; font-size: 24px;">{bad_score:.2f}</div>', unsafe_allow_html=True)

st.title("Fluency")

col_left, col_right = st.columns([0.65, 0.35])

with col_left:
    questions = load_questions()
    st.write("**Trained Test Questions:**")
    for i, q in enumerate(questions, 1):
        st.write(f"{i}. {q}")

    selected_question = st.selectbox("Select Question (test_question):", questions)
    user_response = st.text_area("Enter your response (will be used as transcript):", height=100)
    endpoint = st.selectbox("Select Endpoint:", ["/getFreeScore", "/getMLFreeScore", "/getHybridFreeScore"])

    if st.button("Get Score"):
        if user_response.strip():
            payload = {
                "test_question": selected_question,
                "use_comprehend": "1",
                "use_doc2vec": "1",
                "results": {
                    "transcripts": [{"transcript": user_response.strip()}]
                }
            }
            try:
                BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8100")
                response = requests.post(f"{BACKEND_URL}{endpoint}",
                                         json=payload,
                                         headers={'Content-Type': 'application/json'})
                response.raise_for_status()
                result = response.json()
                display_scores(result)
                st.info(f"**Verdict:** {result.get('verdict', 'N/A')}")
                st.write(f"**Speaker Text:** {result.get('speaker text', 'N/A')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error calling webservice: {e}")
            except json.JSONDecodeError:
                st.error("Invalid JSON response from server")
        else:
            st.warning("Please enter your response.")

with col_right:
    st.markdown("<div style='border-left: 1px solid #ccc; height: 100%; padding-left: 10px;'>", unsafe_allow_html=True)
    st.header("Info")
    info_text = "The backend is based on statistical analysis, and machine learning. getFreeScore calculates the scores deterministically (almost), it is a combination of vector similarities, machine translation algorithms and statistical diffs - proprietary algorithms. The purpose is to check against best responses from the corpus and assess similarity in structure mainly, and secondarily in the meaning. getMLFreeScore is a combination of support vector machines, conv nets and recurrent neural networks.  The purpose is to qualify both the meaning and also the topic of the phrase. \n Future improvements: use better embeddings - for now they are restricted to the training corpus - use newer models to generate corpus, or even better use real responses from learners. "
    st.markdown(f'<p style="color:red;">{info_text}</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)






















