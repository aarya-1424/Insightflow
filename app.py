import streamlit as st
import pandas as pd
from sheet_reader import get_sheet_data         #function to get Google Sheet data 
from langchain.chat_models import ChatOpenAI            #to interact with OpenAI chat models
import io                                       #Standard library for in-memory file handling
from fpdf import FPDF                           #Package for generating PDF files in Python
from langchain.callbacks.manager import CallbackManager             #handling streaming LLM outputs
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler             #handling streaming LLM outputs
import matplotlib.pyplot as plt             #for plotting graphs and charts
from tenacity import retry, stop_after_attempt, wait_exponential            #For retrying functions on failure

# --- Streamlit Config ---
st.set_page_config(page_title="InsightFlow", layout="wide")                 #Sets Streamlit app’s page title and uses wide-screen format

# Minimal timestamp header                                          Displays a right-aligned timestamp and author info at the top using custom HTML
st.markdown("""
<div style='text-align: right; margin-bottom: 8px;'>
    <span style='color: #666; font-size: 11px;'>
        🕒 2025-08-03 14:03:19 UTC • @aarya-1424
    </span>
</div>
""", unsafe_allow_html=True)

# Load Google Sheet data first
df = get_sheet_data()                   #Loads the data into a pandas dataframe (df). If nothing is loaded, shows an error and stops the app.
if df is None or df.empty:
    st.error("❌ No Instagram insights data found.")
    st.stop()

# Preprocess Dates
df["Date"] = pd.to_datetime(df["Date"])                     #Converts "Date" column to pandas date format. 
available_weeks = df["Date"].dt.strftime("%Y-%m-%d").tolist()       #Converts "Date" column to pandas date format.    

# --- LLM Setup ---
llm = ChatOpenAI(                           #Configures the ChatOpenAI object: sets API details, model, temperature, timeout, and streaming callbacks for progress updates.
    model="mistralai/mistral-7b-instruct",
    openai_api_key="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",
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.7,
    request_timeout=90,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

# automatically retries the function if it raises an error .
@retry(                     #Retries the function if it raises an error.
            stop=stop_after_attempt(3),             # Stops after 3 failed attempts
    wait=wait_exponential(multiplier=1, min=4, max=10)  # Waits exponentially between attempts (1s, 2s, 4s, etc. up to 10s) 
)
def generate_dynamic_report(row):           # Generates a dynamic report based on the most recent Instagram data row.
    try:                                    # Attempts to generate a report using the LLM.
        prompt = f"""                      
You are an expert Instagram analytics reporter. Write a detailed, insightful, and professional weekly Instagram performance summary based ONLY on the following data. 
Highlight key insights, trends, and recommendations for the week. Do NOT use a pre-existing template or boilerplate text, and do NOT invent data that is not present.

DATA:
{row.to_dict()}                             

Format the report professionally with clear sections for:
1. Weekly Overview
2. Key Metrics Analysis
3. Content Performance
4. Growth Insights
5. Recommendations
"""
        response = llm.invoke(prompt)                   # Invokes the LLM with the prompt and returns the response.
        return response.content if hasattr(response, 'content') else str(response)                  # Handles the case where response might not have 'content' attribute.
    except Exception as e:                              # If the LLM fails to generate a report, it falls back to a basic report format.
        return create_fallback_report(row)              # Creates a basic report when the LLM fails to generate a detailed one.

def create_fallback_report(row):                        
    """Creates a basic report when the LLM fails"""
    try:
        return f"""
Weekly Instagram Performance Report

1. Weekly Overview
- Account had {row['Followers End']} followers by the end of the week
- Changed from {row['Followers Start']} at start of week

2. Key Metrics
- Profile Visits: {row['Profile Visits']}
- Reach: {row['Reach']}
- Impressions: {row['Impressions']}

3. Content Performance
- Top Reel Shares: {row['Reel Shares for Top Reel']}
- Top Reel Saves: {row['Reel Saves for Top Reel']}
- Average Story Views: {row['Story Views Average']}

4. Growth Insights
- Follower Growth: {row['Followers End'] - row['Followers Start']} new followers
- Engagement metrics show {row['Profile Visits']} profile visits

5. Top Content
{row['Top Reels (Title or Hook) - Link']}
"""
    except Exception as e:                          # If an error occurs while creating the fallback report, it returns a simple error message.
        return f"Unable to generate report due to error: {str(e)}"                  # Returns a simple error message if report generation fails.    

def sanitize_text(text):                            # Sanitizes text by replacing special characters with standard ones to ensure clean formatting.
    replacements = {
        '–': '-',
        '—': '-',
        '“': '"',
        '”': '"',
        '‘': "'",                                   
        '’': "'"
    }
    text = text.translate(str.maketrans(replacements))                  # Replace special characters with standard ones
    # Replace longer strings separately
    text = text.replace("…", "...")
    return text

# Title
st.markdown("<h1 class='main-title'>📸 InsightFlow - Weekly Instagram Report</h1>", unsafe_allow_html=True)                         
st.write("Welcome to **InsightFlow**! Visualize weekly Instagram metrics and generate polished reports.")

# Sidebar Navigation
st.sidebar.header("Navigation")                         # Adds a sidebar header for navigation
page = st.sidebar.radio(                                # Radio button for page selection
    "Navigate to:",
    ["📊 View Report", "📝 Generate Report", "📈 Compare Weeks"]
)

# === View Reports ===
if page == "📊 View Report":
    selected_date = st.selectbox("Select a Week:", available_weeks)                         # Selects a week from the available weeks for viewing the report.

    if selected_date:                                                                       # If a week is selected, it filters the DataFrame for that week.
        row = df[df["Date"] == pd.to_datetime(selected_date)].iloc[0]                       # Displays the data for the selected week.
        col1, col2, col3 = st.columns(3)                                                    # Creates three columns for displaying metrics side by side.

        with col1:                                                                          # all elements under this indentation will be placed in the first column 
            st.markdown("<div class='metric-box'><h4>📈 Growth</h4></div>", unsafe_allow_html=True)        # Adds a small HTML-styled title box labeled 📈 Growth.                     
            st.metric("Followers Start", row["Followers Start"])                                            # Displays "Followers Start" with the value from the dataframe row 
            st.metric("Followers End", row["Followers End"])
            st.metric("Growth", row["Followers End"] - row["Followers Start"])                                 # displays net growth in followers (end - start).

        with col2:                                                      # all elements under this indentation will be placed in the second column                                       
            st.markdown("<div class='metric-box'><h4>🎮 Top Reel</h4></div>", unsafe_allow_html=True)               # Shows the performance of the best-performing Reel 
            st.metric("Shares", row["Reel Shares for Top Reel"])
            st.metric("Saves", row["Reel Saves for Top Reel"])

        with col3:
            st.markdown("<div class='metric-box'><h4>📊 Engagement</h4></div>", unsafe_allow_html=True)
            st.metric("Profile Visits", row["Profile Visits"])
            st.metric("Reach", row["Reach"])
            st.metric("Impressions", row["Impressions"])

        st.markdown("<h4 class='section-title'>🎯 Avg Story Views</h4>", unsafe_allow_html=True)
        st.write(row["Story Views Average"])

        st.markdown("<h4 class='section-title'>🌟 Top Reel Description</h4>", unsafe_allow_html=True)
        st.code(row["Top Reels (Title or Hook) - Link"])

# === Generate Report ===
elif page == "📝 Generate Report":
    st.markdown("<div class='metric-box'><h3 class='section-title'>📝 Generate Weekly Performance Report</h3></div>", unsafe_allow_html=True)
    selected_date = st.selectbox("Select Week for Report:", available_weeks)                    # Selects a week from the available weeks for generating a report.

    if st.button("📤 Generate Report"):
        df_selected = df[df["Date"] == pd.to_datetime(selected_date)]                              # Filters the DataFrame for the selected week.
        if df_selected.empty:
            st.warning("⚠️ No data found for selected week.")
        else:
            row = df_selected.iloc[0]                           # Gets the first row of the filtered DataFrame.
            try:
                with st.spinner("Generating report, please wait..."):               # Displays a spinner while the report is being generated.
                    report_text = generate_dynamic_report(row)                      # Generates the report using the LLM.
                if "Unable to generate report due to error" in report_text:
                    st.warning("⚠️ Using basic report format due to API issues")
                else:
                    st.success("✅ Report generated!")
                
                # Single, clean report display
                edited_report = st.text_area(
                    "Generated Report",
                    value=report_text,
                    height=500
                )

                # === Generate PDF ===
                try:            # Generates a PDF version of the report
                    pdf = FPDF()                # Creates a new PDF object
                    pdf.add_page()                 # Adds a new page to the PDF
                    pdf.set_auto_page_break(auto=True, margin=15)                   # Sets automatic page breaks
                    pdf.set_font("Arial", size=12)              # Sets the font for the PDF
                    for line in edited_report.split("\n"):                  # Sanitizes and adds each line to the PDF
                        pdf.multi_cell(0, 10, sanitize_text(line))          # Adds the line to the PDF with line breaks
                    pdf_output = pdf.output(dest="S").encode("latin-1")     # Saves the PDF to a byte stream
                    pdf_buffer = io.BytesIO(pdf_output)                     # Creates an in-memory buffer for the PDF
                    st.download_button(
                        label="⬇️ Download Report as PDF",
                        data=pdf_buffer,
                        file_name=f"Instagram_Report_{selected_date}.pdf",
                        mime="application/pdf"                                 # Adds a download button for the PDF
                    )
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
                    st.info("💡 The report is still available in text format above")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try again in a few moments")

# === Compare Weeks ===
elif page == "📈 Compare Weeks":
    st.markdown("<div class='metric-box'><h3 class='section-title'>📈 Compare Weekly Performance</h3></div>", unsafe_allow_html=True)
    
    # Multiple week selection
    selected_weeks = st.multiselect(
        "Select Weeks to Compare:",
        available_weeks,
        default=available_weeks[:2] if len(available_weeks) >= 2 else available_weeks
    )
    
    if len(selected_weeks) > 0:
        # Get data for selected weeks
        comparison_data = df[df["Date"].dt.strftime("%Y-%m-%d").isin(selected_weeks)]
        
        # Metrics to compare
        metrics = {
            "Followers": ["Followers Start", "Followers End"],
            "Engagement": ["Profile Visits", "Reach", "Impressions"],
            "Reels Performance": ["Reel Shares for Top Reel", "Reel Saves for Top Reel"],
            "Story Views": ["Story Views Average"]
        }
        
        # Create tabs for different types of visualizations
        tab1, tab2, tab3 = st.tabs(["📊 Bar Charts", "📈 Line Graphs", "🔄 Growth Analysis"])
        
        with tab1:
            for metric_group, metric_list in metrics.items():
                st.subheader(f"{metric_group} Comparison")
                
                # Create bar chart using matplotlib
                fig, ax = plt.subplots(figsize=(10, 6))
                x = range(len(selected_weeks))
                width = 0.35
                
                for i, metric in enumerate(metric_list):
                    values = comparison_data[metric]
                    bars = ax.bar([xi + width*i for xi in x], values, width, label=metric)
                    
                    # Add value labels on top of bars
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(height):,}',
                               ha='center', va='bottom')
                
                ax.set_title(f"{metric_group} Across Selected Weeks")
                ax.set_xticks([xi + width/2 for xi in x])
                ax.set_xticklabels(selected_weeks, rotation=45)
                ax.legend()
                
                # Adjust layout to prevent label cutoff
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        
        with tab2:
            for metric_group, metric_list in metrics.items():
                st.subheader(f"{metric_group} Trends")
                
                # Create line graph using matplotlib
                fig, ax = plt.subplots(figsize=(10, 6))
                
                for metric in metric_list:
                    values = comparison_data[metric]
                    dates = comparison_data["Date"]
                    ax.plot(dates, values, marker='o', label=metric)
                    
                    # Add value labels
                    for x, y in zip(dates, values):
                        ax.text(x, y, f'{int(y):,}',
                               ha='right', va='bottom')
                
                ax.set_title(f"{metric_group} Trends Over Time")
                plt.xticks(rotation=45)
                ax.legend()
                
                # Adjust layout to prevent label cutoff
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        
        with tab3:
            st.subheader("Growth Analysis")
            
            # Calculate growth metrics
            growth_data = []
            for week in selected_weeks:
                week_data = df[df["Date"].dt.strftime("%Y-%m-%d") == week].iloc[0]
                follower_growth = week_data["Followers End"] - week_data["Followers Start"]
                engagement_rate = (week_data["Profile Visits"] / week_data["Followers End"]) * 100
                
                growth_data.append({
                    "Week": week,
                    "Follower Growth": follower_growth,
                    "Engagement Rate (%)": engagement_rate,
                    "Average Story Views": week_data["Story Views Average"]
                })
            
            growth_df = pd.DataFrame(growth_data)
            
            # Create simple bar chart for growth metrics
            fig, ax = plt.subplots(figsize=(10, 6))
            x = range(len(selected_weeks))
            width = 0.25
            
            metrics_to_plot = ["Follower Growth", "Engagement Rate (%)", "Average Story Views"]
            for i, metric in enumerate(metrics_to_plot):
                values = growth_df[metric]
                bars = ax.bar([xi + width*i for xi in x], values, width, label=metric)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height):,}',
                           ha='center', va='bottom')
            
            ax.set_title("Growth Metrics Comparison")
            ax.set_xticks([xi + width for xi in x])
            ax.set_xticklabels(selected_weeks, rotation=45)
            ax.legend()
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            # Show percentage changes
            st.subheader("Week-over-Week Changes")
            if len(selected_weeks) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    # Calculate week-over-week changes
                    for i in range(1, len(selected_weeks)):
                        prev_week = df[df["Date"].dt.strftime("%Y-%m-%d") == selected_weeks[i-1]].iloc[0]
                        curr_week = df[df["Date"].dt.strftime("%Y-%m-%d") == selected_weeks[i]].iloc[0]
                        
                        follower_change = ((curr_week["Followers End"] - prev_week["Followers End"]) / prev_week["Followers End"]) * 100
                        engagement_change = ((curr_week["Profile Visits"] - prev_week["Profile Visits"]) / prev_week["Profile Visits"]) * 100
                        
                        st.metric(
                            f"Follower Growth ({selected_weeks[i]})",
                            f"{follower_change:.1f}%",
                            delta=f"{follower_change:.1f}%"
                        )
                with col2:
                    for i in range(1, len(selected_weeks)):
                        prev_week = df[df["Date"].dt.strftime("%Y-%m-%d") == selected_weeks[i-1]].iloc[0]
                        