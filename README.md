📊 InsightFlow -
AI-powered Instagram Insights & Weekly Reports Generator

InsightFlow is a Streamlit-based analytics tool that connects to Instagram insights stored in Google Sheets (later can directly fetch from an active business account), processes them with LangChain, and generates dynamic, AI-driven weekly reports with actionable recommendations and in the form of charts and graphs.

🚀 Features -

Google Sheets Integration – Automatically fetch Instagram insights.  (later can directly fetch from an active business account)
AI-Powered Summaries – Uses LangChain + LLM to analyze performance trends.
Dynamic Report Generation – Adapts tone & recommendations based on weekly results.
Clean UI – Modern glassmorphism design built with Streamlit.
Shows the analytics in charts and graphs form also.

Three Main Modules:

1. View Report – Instantly fetch and view analytics for a selected date range.
2. Generate Report – Get AI-curated weekly reports with key highlights & recommendations.
3. Reports and Charts - Shows the analytics in charts and graphs form also.


🛠 Tech Stack - 

Frontend: Streamlit (with custom CSS styling)
Backend: Python
AI Processing: LangChain + Local LLM (via Ollama)
Data Source: Google Sheets API / Active Business Account
Other: Pandas, dotenv, requests


📂 Project Structure

InsightFlow/
│
├── app.py                 # Main Streamlit application  
├── requirements.txt       # Python dependencies  
├── .env                   # Environment variables (ignored in GitHub)  
├── google_sheets.py       # Handles Google Sheets data fetching  
├── report_generator.py    # AI report generation logic  
├── styles.css             # Custom UI styles  
└── README.md              # Project documentation


🤝 Contributing - 
Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.


✨ Acknowledgements - 

LangChain
Streamlit
Ollama
