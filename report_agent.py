# report_agent.py

from sheet_reader import get_sheet_data
from datetime import datetime, timedelta
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd

# ✅ Setup OpenRouter + Mistral 7B model
llm = ChatOpenAI(
    temperature=0.3,
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key="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",
    model="mistralai/mistral-7b-instruct"
)

# ✅ Analyze only the most recent week's data
def analyze_data(df):
    try:
        # Convert 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'])

        # Filter for last 7 days
        today = datetime.today()
        one_week_ago = today - timedelta(days=7)
        recent_df = df[(df['Date'] >= one_week_ago) & (df['Date'] <= today)]

        if recent_df.empty:
            return "⚠️ No data available for the past 7 days."

        # Use the most recent entry
        row = recent_df.sort_values('Date').iloc[-1]

        def safe_get(col):
            return row[col] if col in row and pd.notna(row[col]) else "N/A"

        followers_start = safe_get("Followers Start")
        followers_end = safe_get("Followers End")
        follower_growth = int(followers_end) - int(followers_start) if followers_end != "N/A" and followers_start != "N/A" else "N/A"

        top_reel = safe_get("Top Reels (Title or Hook) - Link")
        top_reel_views = safe_get("Reel Views for Top Reel")
        top_reel_shares = safe_get("Reel Shares for Top Reel")
        top_post_engagements = safe_get("Top Post Engagements (Likes + Comments + Saves)")
        profile_visits = safe_get("Profile Visits")
        reach = safe_get("Reach")
        impressions = safe_get("Impressions")
        story_views = safe_get("Story Views Average")

        summary = f"""
Instagram Weekly Summary:

- Followers: {followers_start} ➝ {followers_end} (+{follower_growth})
- Top Reel: {top_reel}
  • Views: {top_reel_views}, Shares: {top_reel_shares}
- Engagements: {top_post_engagements}
- Profile Visits: {profile_visits}, Reach: {reach}, Impressions: {impressions}
- Avg Story Views: {story_views}
"""
        return summary.strip()

    except Exception as e:
        return f"❌ Error during analysis: {e}"

# ✅ Save the final report to a file
def save_report_to_file(summary: str) -> str:
    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"weekly_report_{today}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"✅ Report saved to {filename}")
    return filename

# ✅ Main logic
def generate_report():
    df = get_sheet_data()
    if df is None:
        return "❌ Failed to fetch data.", None

    summary = analyze_data(df)

    prompt = ChatPromptTemplate.from_template(
        "Rewrite this Instagram analytics summary into a professional weekly performance report for stakeholders:\n\n{summary}"
    )

    chain = prompt | llm
    final_report = chain.invoke({"summary": summary})

    filename = save_report_to_file(final_report.content)
    return filename, final_report.content

# ✅ Entry point
if __name__ == "__main__":
    filename, summary = generate_report()
    if summary:
        print("📄 Summary:\n", summary)
    else:
        print("❌ Report generation failed.")