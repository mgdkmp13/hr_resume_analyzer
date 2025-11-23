import streamlit as st
import tempfile
from resume_parser import parse_resume
from analyzer import analyze_candidate
import os
import json

st.set_page_config(page_title="AI HR Candidate Analyzer")
st.title("AI HR Candidate Analyzer")
st.caption("🎓 Wersja studencka - analiza za pomocą embeddings (text-embedding-3-large)")

uploaded_file = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])

resumes_dir = "data/resumes"
sample_options = ["-- none --"]
if os.path.exists(resumes_dir):
    sample_options += [f for f in os.listdir(resumes_dir) if f.endswith('.pdf')]

sample_select = st.selectbox("Or pick a sample resume:", options=sample_options)

st.divider()
job_description = st.text_area("Paste Job Description here", height=250)

job_desc_dir = "data/job_descriptions"
job_desc_options = ["-- none --"]
if os.path.exists(job_desc_dir):
    job_desc_options += [f for f in os.listdir(job_desc_dir) if f.endswith('.pdf')]

job_desc_select = st.selectbox("Or pick a sample job description:", options=job_desc_options)

if st.button("Analyze Candidate"):
    tmp_path = None
    job_desc_text = None
    
    if sample_select and sample_select != "-- none --":
        tmp_path = os.path.join(resumes_dir, sample_select)
    elif uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
    
    if job_desc_select and job_desc_select != "-- none --":
        job_desc_path = os.path.join(job_desc_dir, job_desc_select)
        with st.spinner("Parsing job description..."):
            job_desc_data = parse_resume(job_desc_path)
            job_desc_text = job_desc_data.get('full_text', '')
    elif job_description:
        job_desc_text = job_description
    
    if not tmp_path:
        st.error("Please upload a PDF resume or select a sample.")
    elif not job_desc_text:
        st.error("Please paste a job description or select a sample.")
    else:  

        with st.spinner("Parsing resume..."):
            resume_data = parse_resume(tmp_path)
        
        if not resume_data or all(not resume_data.get(key) for key in ['skills', 'experience', 'education']):
            st.warning("⚠️ CV może być puste lub niepoprawnie sparsowane. Sprawdź 'View Parsed Resume' poniżej.")

        with st.spinner("Analyzing candidate with Azure OpenAI Embeddings..."):
            result = analyze_candidate(resume_data, job_desc_text)

        st.subheader("📊 Analysis Result")
        
        # Wyświetl wynik 
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Match Score", f"{result.get('score', 0)}%")
        with col2:
            rec = result.get('recommendation', 'NO')
            confidence = result.get('recommendation_confidence', 'low')
            
            # Wybierz kolor w zależności od confidence
            if rec == "YES":
                if confidence == "high":
                    rec_color = "🟢"  # Zielone - wysoki match
                elif confidence == "medium":
                    rec_color = "🟡"  # Żółte - tylko technical lub umiarkowany
                else:
                    rec_color = "🟠"  # Pomarańczowe - niski
            else:
                rec_color = "🔴"  # Czerwone - NO
            
            st.metric("Recommendation", f"{rec_color} {rec}")
        
        if 'recommendation_reason' in result:
            confidence_label = {
                "high": "High confidence",
                "medium": "Medium confidence - review carefully",
                "low": "Low confidence"
            }.get(confidence, "")
            st.info(f"💡 {result['recommendation_reason']}\n\n*{confidence_label}*")
        
        if 'similarity_scores' in result:
            st.write("**📈 Match Breakdown (weights: Technical 45%, Keywords 25%, Experience 20%, Embedding 10%):**")
            scores = result['similarity_scores']
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                tech_score = scores.get('technical', 0)*100
                st.metric("🔧 Technical", f"{tech_score:.1f}%", 
                         delta="Primary factor" if tech_score >= 40 else None)
            with col_b:
                st.metric("🔑 Keywords", f"{scores.get('keywords', 0)*100:.1f}%")
            with col_c:
                st.metric("👔 Experience", f"{scores.get('experience', 0)*100:.1f}%")
            with col_d:
                st.metric("🧠 Embedding", f"{scores.get('embedding', 0)*100:.1f}%")
        
        st.write("**✅ Strong Matches:**")
        for match in result.get('strong_matches', []):
            st.write(f"- {match}")
        
        st.write("**❌ Missing Requirements:**")
        for req in result.get('missing_requirements', []):
            st.write(f"- {req}")
        
        if 'debug' in result:
            with st.expander("🐛 Debug Info"):
                debug = result['debug']
                st.write("**Job Requirements Breakdown:**")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"🔴 Required tech: {debug.get('job_tech_required_count', 0)}")
                    if debug.get('job_tech_required'):
                        st.write(f"   → {', '.join(debug['job_tech_required'])}")
                with col_d2:
                    st.write(f"🟡 Nice-to-have tech: {debug.get('job_tech_nice_count', 0)}")
                    if debug.get('job_tech_nice'):
                        st.write(f"   → {', '.join(debug['job_tech_nice'])}")
                
                st.write(f"\n**Resume:**")
                st.write(f"- Keywords found: {debug.get('resume_keywords_count', 0)}")
                st.write(f"- Technical terms: {debug.get('resume_tech_count', 0)}")
                if 'resume_tech_terms' in debug:
                    st.write(f"   → {', '.join(debug['resume_tech_terms'])}")
                
                st.write(f"\n**Seniority & Experience:**")
                st.write(f"- Job requires: {debug.get('job_seniority', 'Not specified')} level, {debug.get('job_years', 0)}+ years")
                st.write(f"- Resume shows: {debug.get('resume_seniority', 'Not specified')} level, {debug.get('resume_years', 0)} years")
                st.write(f"- Seniority match: {debug.get('seniority_match', 0)*100:.1f}%")
                st.write(f"- Experience match: {debug.get('experience_match', 0)*100:.1f}%")
                
                st.write(f"\n**Match Ratios:**")
                st.write(f"- Required tech match: {debug.get('required_match_ratio', 0)*100:.1f}%")
                st.write(f"- Nice-to-have match: {debug.get('nice_match_ratio', 0)*100:.1f}%")
                st.write(f"- Keywords match: {debug.get('common_keywords_count', 0)}/{debug.get('job_keywords_count', 0)}")
        
        with st.expander("🔍 View Full Analysis (JSON)"):
            st.json(result)

        with st.expander("📄 View Parsed Resume"):
            st.json(resume_data)