import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# Groq setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Page config
st.set_page_config(
    page_title="Innovation Sprint",
    page_icon="🚀",
    layout="wide"
)

# Header
st.title("🚀 Innovation Sprint")
st.markdown("##### Powered by Neostats x Groq AI")
st.markdown("---")

# Two columns layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📂 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload your CSV or Excel file",
        type=["csv", "xlsx"]
    )

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ Loaded {df.shape[0]} rows and {df.shape[1]} columns")
        st.dataframe(df.head(10), use_container_width=True)

        # Chart
        st.subheader("📊 Quick Visualization")
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Select column to visualize", numeric_cols)
            chart_type = st.selectbox("Chart type", ["Histogram", "Bar", "Line", "Scatter"])
            
            if chart_type == "Histogram":
                fig = px.histogram(df, x=selected_col, color_discrete_sequence=["#6366f1"])
            elif chart_type == "Bar":
                fig = px.bar(df, y=selected_col, color_discrete_sequence=["#6366f1"])
            elif chart_type == "Line":
                fig = px.line(df, y=selected_col, color_discrete_sequence=["#6366f1"])
            elif chart_type == "Scatter":
                if len(numeric_cols) > 1:
                    second_col = st.selectbox("Select second column", [c for c in numeric_cols if c != selected_col])
                    fig = px.scatter(df, x=selected_col, y=second_col, color_discrete_sequence=["#6366f1"])
                else:
                    fig = px.scatter(df, x=selected_col, color_discrete_sequence=["#6366f1"])
            
            st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🤖 AI Assistant")

    if uploaded_file and st.button("🔍 Analyze My Data with AI"):
        with st.spinner("Analyzing your data..."):
            preview = df.head(5).to_string()
            prompt = f"""
            Analyze this dataset and give:
            1. A brief summary of what this data is about
            2. 3 key insights
            3. 2 actionable recommendations
            
            Data preview:
            {preview}
            
            Columns: {list(df.columns)}
            Shape: {df.shape}
            """
            response = ask_ai(prompt)
            st.markdown(response)

    st.markdown("---")

    st.subheader("💬 Ask AI Anything")
    user_question = st.text_input("Type your question here...")
    if st.button("Ask") and user_question:
        with st.spinner("Thinking..."):
            response = ask_ai(user_question)
            st.markdown(response)

    st.markdown("---")

    # Bonus: chat history
    st.subheader("🗂️ Chat History")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    chat_input = st.text_input("Chat with AI...", key="chat")
    if st.button("Send") and chat_input:
        with st.spinner("Thinking..."):
            st.session_state.chat_history.append({"role": "user", "content": chat_input})
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=st.session_state.chat_history
            )
            reply = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")