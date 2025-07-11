import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

def show_toast(message: str, type: str = "success"):
    """Show a toast notification"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "info":
        st.info(message)
    elif type == "warning":
        st.warning(message)

def call_api(endpoint: str, method: str = "POST", data: Dict = None, files: Dict = None) -> Dict[str, Any]:
    """Make API call to backend"""
    try:
        url = f"http://localhost:8000/api/v1{endpoint}"
        
        if method == "POST":
            if files:
                response = requests.post(url, files=files, data=data)
            else:
                response = requests.post(url, json=data)
        else:
            response = requests.get(url)
        
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def upload_study_material_page():
    """Page for uploading study material"""
    st.markdown('<h1 class="main-header">📘 Upload Study Material</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Instructions
    1. Upload a `.txt` file containing your study material
    2. Or paste the study material directly in the text area below
    3. The material will be processed and stored for question generation and evaluation
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 File Upload")
        uploaded_file = st.file_uploader(
            "Choose a .txt file",
            type=['txt'],
            help="Upload a text file containing study material"
        )
        
        if uploaded_file is not None:
            study_text = uploaded_file.read().decode('utf-8')
            st.session_state['study_text'] = study_text
            st.success(f"✅ File uploaded successfully! ({len(study_text)} characters)")
            
            # Show preview
            with st.expander("📖 Preview Study Material"):
                st.text_area("Study Material Preview", study_text[:1000] + "..." if len(study_text) > 1000 else study_text, height=200)
    
    with col2:
        st.subheader("✍️ Direct Input")
        study_text_input = st.text_area(
            "Paste study material here",
            height=400,
            placeholder="Paste your study material here..."
        )
        
        if study_text_input.strip():
            st.session_state['study_text'] = study_text_input
            st.success(f"✅ Text input saved! ({len(study_text_input)} characters)")
    
    # Store in session state
    if 'study_text' in st.session_state:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("**✅ Study material is ready for use!**")
        st.markdown("You can now proceed to generate question papers or evaluate answers.")
        st.markdown("</div>", unsafe_allow_html=True)

def generate_question_paper_page():
    """Page for generating question papers"""
    st.markdown('<h1 class="main-header">📝 Generate Question Paper</h1>', unsafe_allow_html=True)
    
    if 'study_text' not in st.session_state or not st.session_state['study_text'].strip():
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("**⚠️ No study material found!**")
        st.markdown("Please upload study material first from the 'Upload Study Material' page.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    st.markdown("""
    ### Generate Question Paper
    Click the button below to generate a 50-mark question paper from your study material.
    The system will create questions worth 2, 5, or 10 marks each.
    """)
    
    if st.button("🚀 Generate Question Paper", type="primary", use_container_width=True):
        with st.spinner("⚙️ Generating question paper..."):
            # Call API to generate question paper
            result = call_api("/generate/paper/text", data={
                "study_text": st.session_state['study_text']
            })
            
            if result["success"]:
                data = result["data"]
                st.session_state['generated_paper'] = data
                
                show_toast("✅ Question paper generated successfully!", "success")
                
                # Display the generated paper
                st.subheader("📄 Generated Question Paper")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.text_area("Raw Question Paper", data["raw_paper"], height=400)
                
                with col2:
                    st.subheader("📊 Paper Summary")
                    st.metric("Total Questions", len(data["questions"]))
                    st.metric("Total Marks", data["total_marks"])
                    
                    # Questions breakdown
                    st.subheader("📋 Questions Breakdown")
                    for i, q in enumerate(data["questions"], 1):
                        with st.expander(f"Question {i} ({q['marks']} marks)"):
                            st.write(f"**Question:** {q['question_text']}")
                            st.write(f"**Answer:** {q['answer_text']}")
                
                # Download options
                st.subheader("💾 Download Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download as text
                    st.download_button(
                        label="📄 Download as Text",
                        data=data["raw_paper"],
                        file_name="generated_question_paper.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    # Download as CSV
                    questions_df = pd.DataFrame(data["questions"])
                    csv_data = questions_df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download as CSV",
                        data=csv_data,
                        file_name="generated_question_paper.csv",
                        mime="text/csv"
                    )
                
            else:
                show_toast(f"❌ Failed to generate question paper: {result['error']}", "error")

def evaluate_single_answer_page():
    """Page for evaluating a single answer"""
    st.markdown('<h1 class="main-header">✅ Evaluate Single Answer</h1>', unsafe_allow_html=True)
    
    if 'study_text' not in st.session_state or not st.session_state['study_text'].strip():
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("**⚠️ No study material found!**")
        st.markdown("Please upload study material first from the 'Upload Study Material' page.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    if 'generated_paper' not in st.session_state:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("**⚠️ No question paper found!**")
        st.markdown("Please generate a question paper first from the 'Generate Question Paper' page.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    st.markdown("""
    ### Evaluate Student Answer
    Select a question and enter the student's answer to get detailed evaluation feedback.
    """)
    
    # Get questions from generated paper
    questions = st.session_state['generated_paper']['questions']
    
    # Question selection
    question_options = [f"Q{i+1}: {q['question_text'][:50]}..." for i, q in enumerate(questions)]
    selected_question_idx = st.selectbox("Select Question", range(len(questions)), format_func=lambda x: question_options[x])
    
    selected_question = questions[selected_question_idx]
    
    # Display selected question details
    st.subheader("📝 Selected Question")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Question:** {selected_question['question_text']}")
        st.write(f"**Marks:** {selected_question['marks']}")
    
    with col2:
        st.write(f"**Reference Answer:** {selected_question['answer_text']}")
    
    # Student answer input
    st.subheader("✍️ Student Answer")
    student_answer = st.text_area(
        "Enter student's answer",
        height=200,
        placeholder="Type the student's answer here..."
    )
    
    if st.button("🔍 Evaluate Answer", type="primary", use_container_width=True):
        if not student_answer.strip():
            show_toast("⚠️ Please enter a student answer", "warning")
            return
        
        with st.spinner("🔍 Evaluating answer..."):
            # Call API to evaluate
            result = call_api("/evaluate/one/text", data={
                "study_text": st.session_state['study_text'],
                "question": selected_question['question_text'],
                "reference_answer": selected_question['answer_text'],
                "student_answer": student_answer,
                "max_marks": selected_question['marks']
            })
            
            if result["success"]:
                data = result["data"]
                evaluation = data["evaluation"]
                
                show_toast("✅ Evaluation completed!", "success")
                
                # Display evaluation results
                st.subheader("📊 Evaluation Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Score", f"{evaluation['score']:.1f}")
                
                with col2:
                    st.metric("Max Marks", evaluation['max_marks'])
                
                with col3:
                    percentage = (evaluation['score'] / evaluation['max_marks']) * 100
                    st.metric("Percentage", f"{percentage:.1f}%")
                
                # Detailed feedback
                st.subheader("📝 Detailed Feedback")
                st.text_area("Evaluation Feedback", evaluation['feedback'], height=300)
                
                # Score visualization
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=evaluation['score'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Score"},
                    delta={'reference': evaluation['max_marks']},
                    gauge={
                        'axis': {'range': [None, evaluation['max_marks']]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, evaluation['max_marks']*0.6], 'color': "lightgray"},
                            {'range': [evaluation['max_marks']*0.6, evaluation['max_marks']*0.8], 'color': "yellow"},
                            {'range': [evaluation['max_marks']*0.8, evaluation['max_marks']], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': evaluation['max_marks']*0.9
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                show_toast(f"❌ Evaluation failed: {result['error']}", "error")

def evaluate_csv_page():
    """Page for evaluating answers from CSV files"""
    st.markdown('<h1 class="main-header">📊 Evaluate from CSV</h1>', unsafe_allow_html=True)
    
    if 'study_text' not in st.session_state or not st.session_state['study_text'].strip():
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("**⚠️ No study material found!**")
        st.markdown("Please upload study material first from the 'Upload Study Material' page.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    st.markdown("""
    ### Batch Evaluation from CSV
    Upload CSV files containing questions and student answers for batch evaluation.
    
    **Required CSV Formats:**
    - **Questions CSV:** Should have columns: `question_text`, `marks`, `answer_text`
    - **Student Answers CSV:** Should have columns: `question_number`, `student_answer`
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Questions CSV")
        questions_csv = st.file_uploader(
            "Upload questions CSV",
            type=['csv'],
            help="CSV file with question_text, marks, answer_text columns"
        )
        
        if questions_csv is not None:
            questions_df = pd.read_csv(questions_csv)
            st.success(f"✅ Questions CSV uploaded! ({len(questions_df)} questions)")
            
            with st.expander("📖 Preview Questions"):
                st.dataframe(questions_df.head())
    
    with col2:
        st.subheader("📝 Student Answers CSV")
        student_answers_csv = st.file_uploader(
            "Upload student answers CSV",
            type=['csv'],
            help="CSV file with question_number, student_answer columns"
        )
        
        if student_answers_csv is not None:
            student_answers_df = pd.read_csv(student_answers_csv)
            st.success(f"✅ Student answers CSV uploaded! ({len(student_answers_df)} answers)")
            
            with st.expander("📖 Preview Student Answers"):
                st.dataframe(student_answers_df.head())
    
    if questions_csv is not None and student_answers_csv is not None:
        if st.button("🚀 Start Batch Evaluation", type="primary", use_container_width=True):
            with st.spinner("🔍 Evaluating all answers..."):
                # Call API for batch evaluation
                result = call_api("/evaluate/csv", files={
                    'questions_csv': ('questions.csv', questions_csv.getvalue()),
                    'student_answers_csv': ('student_answers.csv', student_answers_csv.getvalue())
                }, data={
                    'study_text': st.session_state['study_text']
                })
                
                if result["success"]:
                    data = result["data"]
                    
                    show_toast("✅ Batch evaluation completed!", "success")
                    
                    # Display results
                    st.subheader("📊 Evaluation Results")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Score", f"{data['total_score']:.1f}")
                    
                    with col2:
                        st.metric("Max Marks", data['total_max_marks'])
                    
                    with col3:
                        st.metric("Percentage", f"{data['percentage']:.1f}%")
                    
                    with col4:
                        st.metric("Questions Evaluated", len(data['results']))
                    
                    # Results table
                    st.subheader("📋 Detailed Results")
                    results_df = pd.DataFrame(data['results'])
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Score distribution chart
                    st.subheader("📈 Score Distribution")
                    fig = px.bar(
                        results_df,
                        x='question_number',
                        y='score',
                        title="Score per Question",
                        labels={'question_number': 'Question Number', 'score': 'Score'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Download results
                    st.subheader("💾 Download Results")
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Results CSV",
                        data=csv_data,
                        file_name="evaluation_results.csv",
                        mime="text/csv"
                    )
                    
                else:
                    show_toast(f"❌ Batch evaluation failed: {result['error']}", "error")

def score_summary_page():
    """Page for displaying score summaries"""
    st.markdown('<h1 class="main-header">📈 Score Summary</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Score Summary Dashboard
    Upload evaluation results CSV to view detailed score analysis and statistics.
    """)
    
    uploaded_file = st.file_uploader(
        "Upload evaluation results CSV",
        type=['csv'],
        help="CSV file with evaluation results"
    )
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        if 'score' in df.columns and 'max_marks' in df.columns:
            st.success(f"✅ Results loaded! ({len(df)} evaluations)")
            
            # Calculate summary statistics
            total_score = df['score'].sum()
            total_max = df['max_marks'].sum()
            percentage = (total_score / total_max) * 100 if total_max > 0 else 0
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Score", f"{total_score:.1f}")
            
            with col2:
                st.metric("Max Marks", total_max)
            
            with col3:
                st.metric("Percentage", f"{percentage:.1f}%")
            
            with col4:
                st.metric("Questions", len(df))
            
            # Score table
            st.subheader("📋 Score Breakdown")
            st.dataframe(df, use_container_width=True)
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Score per question
                fig1 = px.bar(
                    df,
                    x='question_number',
                    y='score',
                    title="Score per Question",
                    labels={'question_number': 'Question', 'score': 'Score'}
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Score vs Max Marks
                fig2 = px.scatter(
                    df,
                    x='max_marks',
                    y='score',
                    title="Score vs Max Marks",
                    labels={'max_marks': 'Max Marks', 'score': 'Score'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Enhanced Performance Analysis
            st.subheader("📊 Advanced Performance Analysis")
            
            # Calculate advanced metrics
            df['percentage'] = (df['score'] / df['max_marks']) * 100
            df['performance_ratio'] = df['score'] / df['max_marks']
            
            # Statistical metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Average Score", f"{df['score'].mean():.1f}")
            
            with col2:
                st.metric("Median Score", f"{df['score'].median():.1f}")
            
            with col3:
                st.metric("Std Deviation", f"{df['score'].std():.1f}")
            
            with col4:
                st.metric("Average %", f"{df['percentage'].mean():.1f}%")
            

            
            # Question difficulty analysis
            st.subheader("📈 Question Difficulty Analysis")
            
            # Create difficulty categories based on performance
            df['difficulty'] = pd.cut(df['percentage'], 
                                    bins=[0, 50, 70, 85, 100], 
                                    labels=['Very Hard', 'Hard', 'Moderate', 'Easy'])
            
            difficulty_counts = df['difficulty'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Difficulty distribution
                fig_difficulty = px.pie(
                    values=difficulty_counts.values,
                    names=difficulty_counts.index,
                    title="Question Difficulty Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_difficulty, use_container_width=True)
            
            with col2:
                # Performance by difficulty
                difficulty_performance = df.groupby('difficulty')['percentage'].mean().reset_index()
                fig_perf_by_diff = px.bar(
                    difficulty_performance,
                    x='difficulty',
                    y='percentage',
                    title="Average Performance by Difficulty",
                    labels={'percentage': 'Average %', 'difficulty': 'Difficulty Level'}
                )
                st.plotly_chart(fig_perf_by_diff, use_container_width=True)
            
            # Performance trends
            st.subheader("📊 Performance Trends")
            
            # Score distribution histogram
            fig_hist = px.histogram(
                df,
                x='percentage',
                nbins=10,
                title="Score Distribution",
                labels={'percentage': 'Percentage Score', 'count': 'Number of Questions'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Performance recommendations
            st.subheader("💡 Performance Recommendations")
            
            avg_percentage = df['percentage'].mean()
            
            if avg_percentage >= 85:
                recommendation = "Excellent performance! Consider challenging with more difficult questions."
                color = "success"
            elif avg_percentage >= 70:
                recommendation = "Good performance. Focus on areas with lower scores for improvement."
                color = "info"
            elif avg_percentage >= 50:
                recommendation = "Moderate performance. Review fundamental concepts and practice more."
                color = "warning"
            else:
                recommendation = "Performance needs improvement. Consider additional study and practice."
                color = "error"
            
            st.markdown(f'<div class="{color}-box">**Recommendation:** {recommendation}</div>', unsafe_allow_html=True)
            
            # Detailed question analysis
            with st.expander("🔍 Detailed Question Analysis"):
                st.dataframe(df[['question_number', 'score', 'max_marks', 'percentage', 'difficulty']].sort_values('percentage', ascending=False))
            
        else:
            st.error("❌ Invalid CSV format. Expected columns: score, max_marks") 