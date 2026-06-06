import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime, date, timedelta
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Mental Health Tracker",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Mental Health & Mood Tracker")
st.markdown("Track your daily mood, energy, "
            "sleep and stress — understand your "
            "mental wellness patterns.")
st.markdown("---")

# Data persistence
DATA_FILE = "mood_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Session state
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = load_data()

# Mood emojis
MOODS = {
    5: ("😄", "Excellent",  "#2ecc71"),
    4: ("🙂", "Good",       "#27ae60"),
    3: ("😐", "Neutral",    "#f39c12"),
    2: ("😔", "Low",        "#e67e22"),
    1: ("😢", "Very Low",   "#e74c3c")
}

ACTIVITIES = [
    "Exercise 🏃", "Reading 📚",
    "Meditation 🧘", "Music 🎵",
    "Friends 👥", "Gaming 🎮",
    "Study 📖", "Nature Walk 🌿",
    "Movies 🎬", "Cooking 🍳",
    "Art 🎨", "Sleep Early 😴"
]

# Sidebar — Log entry
st.sidebar.header("📝 Log Today's Mood")

log_date = st.sidebar.date_input(
    "Date:", date.today())

mood_score = st.sidebar.select_slider(
    "Mood:",
    options=[1, 2, 3, 4, 5],
    value=3,
    format_func=lambda x:
        f"{MOODS[x][0]} {MOODS[x][1]}"
)

energy_level = st.sidebar.slider(
    "Energy Level:", 1, 10, 5)
sleep_hours  = st.sidebar.slider(
    "Sleep Hours:", 3.0, 12.0, 7.0, 0.5)
stress_level = st.sidebar.slider(
    "Stress Level:", 1, 10, 5)
anxiety_level = st.sidebar.slider(
    "Anxiety Level:", 1, 10, 3)

activities_done = st.sidebar.multiselect(
    "Activities Done:",
    ACTIVITIES
)

journal = st.sidebar.text_area(
    "Journal (optional):",
    placeholder="How are you feeling today? "
                "What happened?",
    height=80
)

if st.sidebar.button("💾 Save Entry",
                     type="primary"):
    entry = {
        'date':       str(log_date),
        'mood':       mood_score,
        'energy':     energy_level,
        'sleep':      sleep_hours,
        'stress':     stress_level,
        'anxiety':    anxiety_level,
        'activities': activities_done,
        'journal':    journal,
        'logged_at':  datetime.now().strftime(
            '%H:%M')
    }

    # Update existing or add new
    existing = [
        e for e in st.session_state.mood_data
        if e['date'] != str(log_date)
    ]
    existing.append(entry)
    st.session_state.mood_data = \
        sorted(existing,
               key=lambda x: x['date'])
    save_data(st.session_state.mood_data)
    st.sidebar.success("✅ Entry saved!")
    st.rerun()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📈 Trends",
    "📅 Calendar",
    "📓 Journal",
    "💡 Insights"
])

# Tab 1 — Dashboard
with tab1:
    if not st.session_state.mood_data:
        st.info(
            "👈 Log your first mood entry "
            "using the sidebar!")
        st.markdown("### 🌟 Why Track Your Mood?")
        benefits = [
            "🔍 Identify patterns in your "
            "emotional wellbeing",
            "😴 Understand how sleep affects "
            "your mood",
            "💪 See which activities boost "
            "your energy",
            "📉 Track stress levels and "
            "find triggers",
            "🎯 Build self-awareness for "
            "better mental health"
        ]
        for b in benefits:
            st.markdown(f"• {b}")
    else:
        df = pd.DataFrame(
            st.session_state.mood_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Today's status
        today_entries = df[
            df['date'].dt.date == date.today()]

        if len(today_entries) > 0:
            today = today_entries.iloc[-1]
            mood_info = MOODS[int(today['mood'])]
            st.markdown(
                f"<h2 style='text-align:center;"
                f"color:{mood_info[2]}'>"
                f"Today: {mood_info[0]} "
                f"{mood_info[1]}</h2>",
                unsafe_allow_html=True
            )
        else:
            st.warning(
                "⚠️ You haven't logged "
                "today's mood yet!")

        st.markdown("---")

        # KPIs
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Days Tracked",
                  len(df))
        c2.metric("Avg Mood",
                  f"{df['mood'].mean():.1f}/5 "
                  f"{MOODS[round(df['mood'].mean())][0]}")
        c3.metric("Avg Sleep",
                  f"{df['sleep'].mean():.1f}h")
        c4.metric("Avg Energy",
                  f"{df['energy'].mean():.1f}/10")
        c5.metric("Avg Stress",
                  f"{df['stress'].mean():.1f}/10")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            # Mood gauge
            latest_mood = df['mood'].iloc[-1]
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=latest_mood,
                domain={'x': [0, 1],
                        'y': [0, 1]},
                title={'text':
                           "Latest Mood Score"},
                gauge={
                    'axis': {'range': [1, 5]},
                    'bar':  {'color':
                                 MOODS[int(
                                     round(
                                         latest_mood))
                                 ][2]},
                    'steps': [
                        {'range': [1, 2],
                         'color': '#fadbd8'},
                        {'range': [2, 3],
                         'color': '#fdebd0'},
                        {'range': [3, 4],
                         'color': '#d5f5e3'},
                        {'range': [4, 5],
                         'color': '#a9dfbf'}
                    ]
                }
            ))
            fig.update_layout(height=280)
            st.plotly_chart(
                fig,
                use_container_width=True)

        with col2:
            # Recent 7 days
            recent = df.tail(7)
            fig2   = go.Figure()
            fig2.add_trace(go.Scatter(
                x=recent['date'],
                y=recent['mood'],
                mode='lines+markers',
                name='Mood',
                line=dict(color='#3498db',
                          width=2),
                marker=dict(size=10)
            ))
            fig2.update_layout(
                title='Last 7 Days Mood',
                yaxis=dict(range=[0, 6],
                           tickvals=[1,2,3,4,5],
                           ticktext=[
                               '😢 Very Low',
                               '😔 Low',
                               '😐 Neutral',
                               '🙂 Good',
                               '😄 Excellent']),
                height=280,
                template='plotly_white'
            )
            st.plotly_chart(
                fig2,
                use_container_width=True)

# Tab 2 — Trends
with tab2:
    if not st.session_state.mood_data:
        st.info("Log some entries first!")
    else:
        df = pd.DataFrame(
            st.session_state.mood_data)
        df['date'] = pd.to_datetime(df['date'])

        col1, col2 = st.columns(2)

        with col1:
            # All metrics over time
            fig3 = go.Figure()
            metrics = [
                ('mood',    '#3498db', 'Mood (×2)'),
                ('energy',  '#2ecc71', 'Energy'),
                ('stress',  '#e74c3c', 'Stress'),
                ('anxiety', '#f39c12', 'Anxiety')
            ]
            for col_name, color, label in metrics:
                y_vals = df[col_name].values
                if col_name == 'mood':
                    y_vals = y_vals * 2
                fig3.add_trace(go.Scatter(
                    x=df['date'],
                    y=y_vals,
                    mode='lines+markers',
                    name=label,
                    line=dict(color=color,
                              width=2),
                    marker=dict(size=5)
                ))
            fig3.update_layout(
                title='All Metrics Over Time',
                xaxis_title='Date',
                yaxis_title='Score',
                height=400,
                template='plotly_white'
            )
            st.plotly_chart(
                fig3,
                use_container_width=True)

        with col2:
            # Sleep vs Mood
            fig4 = px.scatter(
                df,
                x='sleep',
                y='mood',
                color='mood',
                size='energy',
                title='Sleep vs Mood',
                labels={
                    'sleep': 'Sleep Hours',
                    'mood': 'Mood Score'
                },
                color_continuous_scale=
                    'RdYlGn',
                trendline='ols'
            )
            fig4.update_layout(
                height=400,
                template='plotly_white'
            )
            st.plotly_chart(
                fig4,
                use_container_width=True)

        # Correlation heatmap
        st.markdown(
            "#### 🔗 Metric Correlations")
        numeric_cols = [
            'mood', 'energy', 'sleep',
            'stress', 'anxiety']
        corr = df[numeric_cols].corr()

        fig5 = px.imshow(
            corr,
            title='Correlation Between Metrics',
            color_continuous_scale='RdYlGn',
            labels=dict(color='Correlation'),
            zmin=-1, zmax=1
        )
        fig5.update_layout(
            height=350,
            template='plotly_white'
        )
        st.plotly_chart(
            fig5,
            use_container_width=True)

# Tab 3 — Calendar
with tab3:
    st.markdown("### 📅 Mood Calendar")

    if not st.session_state.mood_data:
        st.info("Log some entries first!")
    else:
        df = pd.DataFrame(
            st.session_state.mood_data)
        df['date'] = pd.to_datetime(df['date'])

        # Calendar heatmap
        df['day_of_week'] = \
            df['date'].dt.dayofweek
        df['week'] = df['date'].dt.isocalendar()\
            .week.astype(int)

        fig6 = px.density_heatmap(
            df,
            x='week',
            y='day_of_week',
            z='mood',
            title='Mood Calendar Heatmap',
            color_continuous_scale='RdYlGn',
            labels={
                'week': 'Week of Year',
                'day_of_week': 'Day',
                'mood': 'Mood'
            }
        )
        fig6.update_layout(
            yaxis=dict(
                tickvals=[0,1,2,3,4,5,6],
                ticktext=['Mon','Tue','Wed',
                          'Thu','Fri','Sat',
                          'Sun']),
            height=350,
            template='plotly_white'
        )
        st.plotly_chart(
            fig6,
            use_container_width=True)

        # Entries table
        st.markdown("#### 📋 All Entries")
        display = df[[
            'date', 'mood', 'energy',
            'sleep', 'stress', 'anxiety'
        ]].copy()
        display['date'] = \
            display['date'].dt.strftime(
                '%d %b %Y')
        display['mood'] = display['mood']\
            .apply(lambda x:
                   f"{MOODS[int(x)][0]} {x}")
        display.columns = [
            'Date', 'Mood', 'Energy',
            'Sleep (h)', 'Stress', 'Anxiety'
        ]
        st.dataframe(
            display.sort_values(
                'Date', ascending=False),
            use_container_width=True,
            hide_index=True)

        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Data",
            csv, "mood_data.csv",
            "text/csv"
        )

# Tab 4 — Journal
with tab4:
    st.markdown("### 📓 Journal Entries")

    if not st.session_state.mood_data:
        st.info("Log some entries first!")
    else:
        entries_with_journal = [
            e for e in
            st.session_state.mood_data
            if e.get('journal', '').strip()
        ]

        if not entries_with_journal:
            st.info(
                "No journal entries yet. "
                "Add thoughts when logging mood!")
        else:
            for entry in reversed(
                entries_with_journal[-10:]
            ):
                mood_info = MOODS[
                    int(entry['mood'])]
                with st.expander(
                    f"{entry['date']} — "
                    f"{mood_info[0]} "
                    f"{mood_info[1]} | "
                    f"Energy: {entry['energy']}"
                ):
                    st.markdown(
                        entry['journal'])
                    if entry.get('activities'):
                        st.caption(
                            "Activities: " +
                            ", ".join(
                                entry['activities']))

# Tab 5 — Insights
with tab5:
    st.markdown("### 💡 Personal Insights")

    if len(st.session_state.mood_data) < 3:
        st.info(
            "Log at least 3 days to "
            "see insights!")
    else:
        df = pd.DataFrame(
            st.session_state.mood_data)
        df['date'] = pd.to_datetime(df['date'])

        # Auto insights
        st.markdown("#### 🔍 What the Data Says")

        insights = []

        # Sleep insight
        sleep_mood_corr = df['sleep'].corr(
            df['mood'])
        if sleep_mood_corr > 0.3:
            insights.append(
                f"😴 **Sleep matters for you:** "
                f"More sleep is positively "
                f"correlated with better mood "
                f"(r={sleep_mood_corr:.2f})")
        elif sleep_mood_corr < -0.3:
            insights.append(
                f"😴 **Unusual sleep pattern:** "
                f"Your sleep and mood have "
                f"negative correlation — "
                f"investigate further")

        # Stress insight
        stress_mood_corr = df['stress'].corr(
            df['mood'])
        if stress_mood_corr < -0.3:
            insights.append(
                f"😰 **Stress impacts your mood:** "
                f"High stress days tend to have "
                f"lower mood "
                f"(r={stress_mood_corr:.2f})")

        # Best day
        if len(df) >= 5:
            best_day = df.loc[
                df['mood'].idxmax()]
            insights.append(
                f"🌟 **Best day so far:** "
                f"{best_day['date'].strftime('%d %b')} "
                f"with mood {int(best_day['mood'])}/5")

        # Streak
        df_sorted = df.sort_values(
            'date', ascending=False)
        streak     = 0
        today_dt   = pd.Timestamp(date.today())
        for i, row in df_sorted.iterrows():
            expected = today_dt - \
                timedelta(days=streak)
            if row['date'].date() == \
                    expected.date():
                streak += 1
            else:
                break

        if streak > 0:
            insights.append(
                f"🔥 **Current tracking streak:** "
                f"{streak} consecutive days!")

        # Activity impact
        all_activities = []
        for entry in st.session_state.mood_data:
            acts = entry.get('activities', [])
            mood = entry['mood']
            for act in acts:
                all_activities.append({
                    'activity': act,
                    'mood': mood
                })

        if all_activities:
            act_df   = pd.DataFrame(
                all_activities)
            act_mood = act_df.groupby(
                'activity')['mood'].mean()\
                .sort_values(ascending=False)
            if len(act_mood) > 0:
                best_act = act_mood.index[0]
                insights.append(
                    f"💪 **Best activity for "
                    f"your mood:** {best_act} "
                    f"(avg mood: "
                    f"{act_mood.iloc[0]:.1f}/5)")

        for insight in insights:
            st.success(insight)

        # Recommendations
        st.markdown("#### 🎯 Recommendations")
        avg_mood    = df['mood'].mean()
        avg_sleep   = df['sleep'].mean()
        avg_stress  = df['stress'].mean()
        avg_exercise = sum(
            1 for e in
            st.session_state.mood_data
            if 'Exercise 🏃' in
               e.get('activities', [])
        ) / max(len(df), 1)

        recs = []
        if avg_mood < 3:
            recs.append(
                "🆘 Your average mood is low. "
                "Consider talking to someone "
                "you trust.")
        if avg_sleep < 7:
            recs.append(
                "😴 You're averaging less than "
                "7 hours of sleep. "
                "Prioritize sleep hygiene.")
        if avg_stress > 7:
            recs.append(
                "🧘 High stress levels detected. "
                "Try meditation or deep "
                "breathing exercises.")
        if avg_exercise < 0.3:
            recs.append(
                "🏃 You rarely exercise. "
                "Even 20 minutes of walking "
                "significantly improves mood.")

        if recs:
            for rec in recs:
                st.warning(rec)
        else:
            st.success(
                "✅ Great habits! "
                "Keep maintaining your "
                "wellness routine.")

        # Activity chart
        if all_activities:
            st.markdown(
                "#### 🎯 Activity Impact on Mood")
            act_df_plot = pd.DataFrame([{
                'Activity': k.split(' ')[0],
                'Avg Mood': round(v, 2)
            } for k, v in act_mood.items()])

            fig7 = px.bar(
                act_df_plot,
                x='Activity',
                y='Avg Mood',
                title='Avg Mood by Activity',
                color='Avg Mood',
                color_continuous_scale='RdYlGn'
            )
            fig7.update_layout(
                height=300,
                template='plotly_white',
                yaxis_range=[0, 5]
            )
            st.plotly_chart(
                fig7,
                use_container_width=True)

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "Mental Health Tracker | "
    "Your data stays private on your device"
)