import streamlit as st
import plotly.graph_objects as go


def draw_gauge_chart(risk_percent, title_text):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_percent,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": title_text,
                "font": {"size": 18, "color": "#94A3B8", "family": "Outfit"},
            },
            number={
                "suffix": "%",
                "font": {"size": 38, "color": "#F8FAFC", "family": "Outfit"},
            },
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#475569"},
                "bar": {"color": "#6366F1"},
                "bgcolor": "rgba(30, 41, 59, 0.5)",
                "borderwidth": 1,
                "bordercolor": "rgba(255, 255, 255, 0.1)",
                "steps": [
                    {"range": [0, 35], "color": "rgba(16, 185, 129, 0.15)"},
                    {"range": [35, 70], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [70, 100], "color": "rgba(239, 68, 68, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#818CF8", "width": 3},
                    "thickness": 0.75,
                    "value": risk_percent,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#F8FAFC", "family": "Outfit"},
        height=220,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def draw_radar_chart(categories, user_vals, target_vals):
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=user_vals + [user_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Patient Metrics",
            fillcolor="rgba(99, 102, 241, 0.25)",
            line=dict(color="#6366F1", width=2),
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=target_vals + [target_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Healthy Limit",
            fillcolor="rgba(16, 185, 129, 0.05)",
            line=dict(color="#10B981", width=2, dash="dash"),
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                ticks="",
                gridcolor="rgba(255, 255, 255, 0.08)",
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.08)",
                linecolor="rgba(255, 255, 255, 0.08)",
                tickfont=dict(size=11, color="#94A3B8"),
            ),
            bgcolor="rgba(15, 23, 42, 0.4)",
        ),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=30, b=30),
        height=240,
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0.5,
            xanchor="center",
            font=dict(color="#94A3B8", size=10),
        ),
    )
    return fig


def draw_symptoms_chart(cardio, neuro, auto):
    categories = ["Cardiorespiratory", "Neurological", "Autonomic"]
    active = [cardio, neuro, auto]
    total = [4, 3, 3]
    fig = go.Figure(
        data=[
            go.Bar(
                name="Reported Symptoms",
                x=categories,
                y=active,
                marker_color="#818CF8",
                opacity=0.9,
                width=0.4,
            ),
            go.Bar(
                name="Absent Symptoms",
                x=categories,
                y=[t - a for t, a in zip(total, active)],
                marker_color="rgba(255, 255, 255, 0.05)",
                opacity=0.5,
                width=0.4,
            ),
        ]
    )
    fig.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8", family="Outfit"),
        height=220,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(
            orientation="h", y=-0.2, x=0.5, xanchor="center", font=dict(size=10)
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.08)",
            tickfont=dict(size=10),
            dtick=1,
            range=[0, 4],
        ),
        xaxis=dict(tickfont=dict(size=11)),
    )
    return fig


def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)
