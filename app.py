# ---> dynamic dashboard | migration forecasting analytics dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---> μπλοκ 1 | βασικές ρυθμίσεις σελίδας
st.set_page_config(
    page_title="Migration Forecasting Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---> μπλοκ 2 | custom style
st.markdown("""
<style>

.stApp {
    background-color: #eef2f7;
}

/* τίτλοι */
h1, h2, h3 {
    color: #1e293b;
}

/* captions */
p, span, label {
    color: #475569;
}

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #dbe4f0;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    text-align: center;
    height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* force same height for KPI column containers */
div[data-testid="column"] > div:has(.kpi-card) {
    height: 110px;
}

.kpi-label {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: #0f172a;
}

.kpi-good {
    color: #16a34a;
}

.kpi-bad {
    color: #dc2626;
}

/* sections */
.section-box {
    background: #ffffff;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #dbe4f0;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

/* selectboxes */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] span {
    color: #1e293b !important;
}

div[data-baseweb="select"] svg {
    fill: #1e293b !important;
}

/* tables */
thead tr th {
    color: #1e293b !important;
}

tbody tr td {
    color: #334155 !important;
}

</style>
""", unsafe_allow_html=True)

# ---> μπλοκ 3 | φόρτωση δεδομένων
base_dir = Path(__file__).resolve().parent

dashboard = pd.read_csv(base_dir / "dashboard_table.csv")
forecast = pd.read_csv(base_dir / "forecast_monthly.csv")
visuals = pd.read_parquet(base_dir / "gdelt_visuals_route_month.parquet")

try:
    drivers = pd.read_csv(base_dir / "drivers_importance.csv")
except Exception:
    drivers = pd.DataFrame(columns=["Route", "Model", "Feature", "AbsCoefficient"])

# ---> καθαρισμός headers
dashboard.columns = dashboard.columns.str.strip()
forecast.columns = forecast.columns.str.strip()
visuals.columns = visuals.columns.str.strip()
drivers.columns = drivers.columns.str.strip()

# ---> καθαρισμός Route values
if "Route" in dashboard.columns:
    dashboard["Route"] = dashboard["Route"].astype(str).str.strip()

if "Route" in forecast.columns:
    forecast["Route"] = forecast["Route"].astype(str).str.strip()

if "Route" in visuals.columns:
    visuals["Route"] = visuals["Route"].astype(str).str.strip()

if "Route" in drivers.columns:
    drivers["Route"] = drivers["Route"].astype(str).str.strip()

# ---> καθαρισμός Model values
if "Model" in drivers.columns:
    drivers["Model"] = drivers["Model"].astype(str).str.strip()

# ---> μπλοκ 4 | τίτλος
st.title("📊 Migration Forecasting Dashboard")
st.markdown("### 🌍 Migration Forecasting Analytics")
st.caption("Monitoring best-model accuracy, baseline comparison and migration drivers across routes.")

# ---> μπλοκ 5 | επιλογές χρήστη
routes = dashboard["Route"].unique().tolist()

col_filter1, col_filter2 = st.columns([2, 1])

with col_filter1:
    route = st.selectbox("Select Migration Route", routes)

with col_filter2:
    metric_type = st.selectbox("Select Error Metric", ["MAE", "RMSE"])

# ---> μπλοκ 5.1 | map + heatmap δίπλα δίπλα

routes_map_df = pd.DataFrame({
    "Route": [
        "Central Mediterranean Route",
        "Eastern Mediterranean Route",
        "Western African Route",
        "Western Balkan Route"
    ],
    "start_lat": [32.9, 38.4, 14.7, 41.9],
    "start_lon": [13.2, 27.1, -17.4, 20.5],
    "end_lat": [35.9, 37.9, 28.1, 47.0],
    "end_lon": [14.5, 23.7, -15.4, 19.0]
})

visuals_heat = visuals[visuals["Route"] == route].copy()

map_col, heat_col = st.columns(2)

with map_col:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Migration Routes Map")

    fig_map = go.Figure()

    for _, row in routes_map_df.iterrows():

        line_color = "#38bdf8" if row["Route"] == route else "#475569"
        line_width = 5 if row["Route"] == route else 2

        fig_map.add_trace(go.Scattergeo(
            lon=[row["start_lon"], row["end_lon"]],
            lat=[row["start_lat"], row["end_lat"]],
            mode="lines",
            line=dict(width=line_width, color=line_color),
            opacity=0.9,
            name=row["Route"]
        ))

        fig_map.add_trace(go.Scattergeo(
            lon=[row["start_lon"]],
            lat=[row["start_lat"]],
            mode="markers",
            marker=dict(size=8, color="#22c55e"),
            showlegend=False
        ))

        fig_map.add_trace(go.Scattergeo(
            lon=[row["end_lon"]],
            lat=[row["end_lat"]],
            mode="markers",
            marker=dict(size=8, color="#ef4444"),
            showlegend=False
        ))

    fig_map.update_layout(
        geo=dict(
            scope="europe",
            projection_type="natural earth",
            showland=True,
            landcolor="#e5e7eb",
            showocean=True,
            oceancolor="#dbeafe",
            showcountries=True,
            countrycolor="#9ca3af",
            showlakes=True,
            lakecolor="#dbeafe",
            coastlinecolor="#9ca3af",
            showframe=False,
            lataxis=dict(range=[0, 60]),
            lonaxis=dict(range=[-25, 40])
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font_color="#1e293b",
        height=420,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig_map, use_container_width=True, theme=None, key=f"fig_map_{route}")
    st.caption("Blue line = selected route, grey lines = other routes, green marker = departure, red marker = arrival.")
    st.markdown('</div>', unsafe_allow_html=True)

with heat_col:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Push Factors vs Detected Crossings")

    if visuals_heat.empty:
        st.info("No scatter data available for this route.")
    else:
        fig_scatter = px.scatter(
            visuals_heat,
            x="push_events_sum",
            y="total_detections_sum",
            trendline="ols",
            labels={
                "push_events_sum": "Push Events",
                "total_detections_sum": "Detections"
            },
            title=f"Push Events vs Detections — {route}"
        )

        fig_scatter.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font_color="#1e293b",
            xaxis=dict(color="#1e293b"),
            yaxis=dict(color="#1e293b"),
            height=420
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True,
            theme=None,
            key=f"fig_scatter_{route}"
        )

    st.markdown('</div>', unsafe_allow_html=True)

# ---> μπλοκ 6 | φιλτράρισμα δεδομένων
route_data = dashboard[dashboard["Route"] == route].copy()
forecast_route = forecast[forecast["Route"] == route].copy()
visuals_route = visuals[visuals["Route"] == route].copy()

# ---> σωστή μορφή month
forecast_route["Month"] = pd.to_datetime(forecast_route["Month"])
forecast_route = forecast_route.sort_values("Month")

if not visuals_route.empty:
    visuals_route["target_month"] = pd.to_datetime(
        visuals_route["target_month"].astype(str),
        format="%Y%m"
    )
    visuals_route = visuals_route.sort_values("target_month")

# ---> μπλοκ 6.1 | βασικά metrics του route
best_model = str(route_data["Best_Model"].iloc[0])

mae_best = float(route_data["MAE_best"].iloc[0])
mae_baseline = float(route_data["MAE_baseline"].iloc[0])

rmse_best = float(route_data["RMSE_best"].iloc[0])
rmse_baseline = float(route_data["RMSE_baseline"].iloc[0])

n_predictions = int(route_data["n_predictions"].iloc[0])

mae_improvement = float(route_data["MAE_improvement_%"].iloc[0])
rmse_improvement = float(route_data["RMSE_improvement_%"].iloc[0])

# ---> drivers filtering
drivers_route = drivers[drivers["Route"] == route].copy()

if "Model" in drivers_route.columns:
    drivers_route = drivers_route[drivers_route["Model"] == best_model].copy()

# ---> μπλοκ 7 | KPI cards
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Route</div>
        <div class="kpi-value" style="font-size:22px;">{route.replace(" Route","")}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Best Model</div>
        <div class="kpi-value" style="font-size:22px;">{best_model}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Best MAE</div>
        <div class="kpi-value">{mae_best:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    improvement_class = "kpi-good" if mae_improvement > 0 else "kpi-bad" if mae_improvement < 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">MAE Improvement vs Baseline</div>
        <div class="kpi-value {improvement_class}">{mae_improvement:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Forecast Windows</div>
        <div class="kpi-value">{n_predictions}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---> μπλοκ 8 | layout δύο στηλών
left_col, right_col = st.columns(2)

with left_col:

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Best Model vs Baseline")

    if metric_type == "MAE":
        best_value = mae_best
        baseline_value = mae_baseline
        chart_title = f"MAE Comparison — {route}"
        y_axis_label = "MAE"
    else:
        best_value = rmse_best
        baseline_value = rmse_baseline
        chart_title = f"RMSE Comparison — {route}"
        y_axis_label = "RMSE"

    compare_df = pd.DataFrame({
        "Type": ["Best Model", "Baseline"],
        "Value": [best_value, baseline_value]
    })

    fig_compare = px.bar(
        compare_df,
        x="Type",
        y="Value",
        text="Value",
        color="Type",
        color_discrete_map={
            "Best Model": "#38bdf8",
            "Baseline": "#fb923c"
        },
        title=chart_title
    )

    fig_compare.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_compare.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font_color="#1e293b",
        xaxis=dict(color="#1e293b"),
        yaxis=dict(color="#1e293b", title=y_axis_label),
        showlegend=False,
        height=430
    )

    st.plotly_chart(fig_compare, use_container_width=True, theme=None, key=f"fig_compare_{route}_{metric_type}")
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Drivers Importance")

    if drivers_route.empty:
        st.info(f"No feature importance available for {route}.")
    else:
        def feature_group(x):
            if "lag" in x or "roll" in x:
                return "History"
            elif x in ["push_events_sum", "avg_sentiment_wavg"]:
                return "Push Factors"
            else:
                return "Weather"

        drivers_route = drivers_route.copy()
        drivers_route["Group"] = drivers_route["Feature"].apply(feature_group)

        value_col = "AbsCoefficient" if "AbsCoefficient" in drivers_route.columns else "Importance"
        drivers_route = drivers_route.sort_values(value_col, ascending=True)

        color_map = {
            "History": "#6366f1",
            "Push Factors": "#fb923c",
            "Weather": "#22c55e"
        }

        fig_drivers = px.bar(
            drivers_route,
            x=value_col,
            y="Feature",
            orientation="h",
            text=value_col,
            color="Group",
            color_discrete_map=color_map,
            title=f"Importance by Route — {route}"
        )

        fig_drivers.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig_drivers.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font_color="#1e293b",
            xaxis=dict(color="#1e293b", title="Importance"),
            yaxis=dict(color="#1e293b", title=""),
            legend=dict(font=dict(color="#1e293b")),
            legend_title="Feature group",
            height=430
        )

        st.plotly_chart(fig_drivers, use_container_width=True, theme=None, key=f"fig_drivers_{route}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---> μπλοκ 10.5 | Push factors vs detections
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Push Factors vs Detections")

if visuals_route.empty:
    st.info("No push factor data available for this route.")
else:
    fig_push = go.Figure()

    fig_push.add_trace(
        go.Scatter(
            x=visuals_route["year_month_label"],
            y=visuals_route["push_events_sum"],
            name="GDELT Push Events",
            mode="lines+markers",
            yaxis="y1"
        )
    )

    fig_push.add_trace(
        go.Scatter(
            x=visuals_route["year_month_label"],
            y=visuals_route["total_detections_sum"],
            name="Frontex Detections",
            mode="lines+markers",
            yaxis="y2"
        )
    )

    fig_push.update_layout(
        title=f"Push Events vs Detections — {route}",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font_color="#1e293b",
        height=420,
        yaxis=dict(
            title="Push Events",
            side="left"
        ),
        yaxis2=dict(
            title="Detections",
            overlaying="y",
            side="right"
        )
    )

    st.plotly_chart(fig_push, use_container_width=True, theme=None, key=f"fig_push_{route}")
st.markdown('</div>', unsafe_allow_html=True)

# ---> μπλοκ 11 | Forecast vs Actual detections
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Forecast vs Actual Detections")

fig_forecast = px.line(
    forecast_route,
    x="Month",
    y=["Actual_detections", "Predicted_detections"],
    markers=True,
    labels={
        "value": "Detections",
        "Month": "Month",
        "variable": "Series"
    },
    title=f"Actual vs Predicted — {route} ({best_model})"
)

fig_forecast.update_layout(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font_color="#1e293b",
    xaxis=dict(color="#1e293b"),
    yaxis=dict(color="#1e293b"),
    legend=dict(font=dict(color="#1e293b")),
    legend_title="",
    height=450
)

st.plotly_chart(fig_forecast, use_container_width=True, theme=None, key=f"fig_forecast_{route}")
st.markdown('</div>', unsafe_allow_html=True)

# ---> μπλοκ 9 | πίνακας αποτελεσμάτων
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Performance Overview Table")

show_cols = [
    "Route",
    "Best_Model",
    "MAE_best",
    "RMSE_best",
    "MAE_baseline",
    "RMSE_baseline",
    "MAE_improvement_%",
    "RMSE_improvement_%",
    "n_predictions"
]

table_df = dashboard[show_cols].round(2)

st.table(
    table_df.style
    .set_properties(**{
        "background-color": "#ffffff",
        "color": "#1e293b",
        "border-color": "#e2e8f0"
    })
)
st.markdown('</div>', unsafe_allow_html=True)

# ---> μπλοκ 10 | summary insight
st.markdown("<br>", unsafe_allow_html=True)

best_metric_improvement = mae_improvement if metric_type == "MAE" else rmse_improvement

if best_metric_improvement > 0:
    improvement_label = "better than baseline"
elif best_metric_improvement < 0:
    improvement_label = "worse than baseline"
else:
    improvement_label = "equal to baseline"

st.info(
    f"For **{route}**, the selected best model is **{best_model}**. "
    f"Based on **{metric_type}**, it is **{improvement_label}** "
    f"with an improvement of **{best_metric_improvement:.2f}%** versus the baseline."
)