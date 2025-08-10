def analyze_data(df):
    try:
        # Extract follower growth
        followers_start = int(df.loc[0, "Followers Start"])
        followers_end = int(df.loc[0, "Followers End"])
        follower_growth = followers_end - followers_start

        # Extract top reel
        top_reel = df.loc[0, "Top Reels (Title or Hook) - Link"]
        top_reel_views = df.loc[0, "Reel Views for Top Reel"]
        top_reel_shares = df.loc[0, "Reel Shares for Top Reel"]

        # Engagements & reach
        top_post_engagements = df.loc[0, "Top Post Engagements (Likes + Comments + Saves)"]
        profile_visits = df.loc[0, "Profile Visits"]
        reach = df.loc[0, "Reach"]
        impressions = df.loc[0, "Impressions"]

        # Optional: Story views
        story_views = df.loc[0, "Story Views Average"] if "Story Views Average" in df.columns else "N/A"

        summary = f"""
From the latest Instagram insights:
- 📈 Followers grew from {followers_start} to {followers_end} (+{follower_growth}).
- 🔥 Top Reel: {top_reel} with {top_reel_views} views and {top_reel_shares} shares.
- 💬 Top Post Engagements: {top_post_engagements}
- 👀 Profile Visits: {profile_visits}, Reach: {reach}, Impressions: {impressions}
- 📊 Avg Story Views: {story_views}
"""
        return summary.strip()
    
    except Exception as e:
        return f"Error during analysis: {e}"
