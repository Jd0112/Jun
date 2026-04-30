import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================
# Page setup
# =========================
st.set_page_config(page_title="Moving America", layout="wide")

# =========================
# Style
# =========================
st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
.main-title { font-size: 46px; font-weight: 800; margin-bottom: 0.2rem; }
.subtitle { font-size: 18px; color: #6b7280; margin-bottom: 1.5rem; }
.note-box {
    background-color: #fff7ed;
    border-left: 6px solid #f97316;
    padding: 1rem 1.2rem;
    border-radius: 14px;
    font-size: 15px;
    margin-bottom: 1.2rem;
}
.insight-box {
    background-color: #eef4ff;
    border-left: 6px solid #2563eb;
    padding: 1rem 1.2rem;
    border-radius: 14px;
    font-size: 16px;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.small-note {
    color: #6b7280;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Load data
# =========================
df = pd.read_csv("final_data.csv")
flows = pd.read_csv("migration_flows_clean.csv")

df["year"] = df["year"].astype(int)
flows["year"] = flows["year"].astype(int)

if "destination" not in df.columns and "state" in df.columns:
    df = df.rename(columns={"state": "destination"})

flows["flow"] = pd.to_numeric(flows["flow"], errors="coerce")
flows = flows.dropna(subset=["flow"])

years = sorted(df["year"].unique())
states = sorted(df["destination"].unique())
flow_years = sorted(flows["year"].unique())

# =========================
# State codes and coordinates
# =========================
state_codes = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN",
    "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

state_centers = {
    "Alabama": (32.8, -86.8), "Alaska": (61.4, -152.4), "Arizona": (33.7, -111.4),
    "Arkansas": (35.0, -92.4), "California": (36.1, -119.7), "Colorado": (39.1, -105.3),
    "Connecticut": (41.6, -72.7), "Delaware": (39.3, -75.5), "District of Columbia": (38.9, -77.0),
    "Florida": (27.8, -81.7), "Georgia": (33.0, -83.6), "Hawaii": (21.1, -157.5),
    "Idaho": (44.2, -114.5), "Illinois": (40.3, -89.0), "Indiana": (39.8, -86.3),
    "Iowa": (42.0, -93.2), "Kansas": (38.5, -96.7), "Kentucky": (37.7, -84.7),
    "Louisiana": (31.2, -91.9), "Maine": (44.7, -69.4), "Maryland": (39.1, -76.8),
    "Massachusetts": (42.2, -71.5), "Michigan": (43.3, -84.5), "Minnesota": (45.7, -93.9),
    "Mississippi": (32.7, -89.7), "Missouri": (38.5, -92.3), "Montana": (46.9, -110.5),
    "Nebraska": (41.1, -98.3), "Nevada": (38.3, -117.1), "New Hampshire": (43.5, -71.6),
    "New Jersey": (40.3, -74.5), "New Mexico": (34.8, -106.2), "New York": (42.2, -75.0),
    "North Carolina": (35.6, -79.8), "North Dakota": (47.5, -99.8), "Ohio": (40.4, -82.8),
    "Oklahoma": (35.6, -96.9), "Oregon": (44.0, -120.5), "Pennsylvania": (40.6, -77.2),
    "Rhode Island": (41.7, -71.5), "South Carolina": (33.9, -80.9), "South Dakota": (44.3, -100.2),
    "Tennessee": (35.7, -86.7), "Texas": (31.0, -99.9), "Utah": (39.3, -111.7),
    "Vermont": (44.0, -72.7), "Virginia": (37.8, -78.2), "Washington": (47.4, -121.5),
    "West Virginia": (38.5, -80.9), "Wisconsin": (44.5, -89.5), "Wyoming": (43.1, -107.3)
}

df["state_code"] = df["destination"].map(state_codes)

# =========================
# Sidebar
# =========================
st.sidebar.title("Controls")

global_year = st.sidebar.selectbox("Main year", years, index=len(years) - 1)

top_n = st.sidebar.slider(
    "Top N states",
    min_value=5,
    max_value=20,
    value=10,
    step=5
)

state_group = st.sidebar.selectbox(
    "State group for trend page",
    [
        "Default: CA, TX, FL, NY",
        "Sun Belt",
        "Coastal states",
        "High-growth states",
        "Custom"
    ]
)

show_tables = st.sidebar.checkbox("Show data tables", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Guide**

- Net migration = inflow − outflow  
- Negative net migration ≠ population decline  
- Big states can have both high inflow and high outflow  
- Trend colors are not political colors
""")

# =========================
# Header
# =========================
st.markdown('<div class="main-title">Moving America</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Interstate migration flows and labor market conditions across U.S. states.</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="note-box">
<b>Data note:</b> Net migration means <b>inflow minus outflow</b>. 
It does not measure total population change because it does not include births, deaths, or international immigration.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Migration Map",
    "Inflow vs Outflow",
    "State Trends",
    "Migration vs Unemployment",
    "Migration Network"
])

# =========================
# Helper
# =========================
def get_default_states(group):
    if group == "Sun Belt":
        return ["Texas", "Florida", "Arizona", "Georgia", "North Carolina"]
    elif group == "Coastal states":
        return ["California", "New York", "New Jersey", "Massachusetts", "Washington"]
    elif group == "High-growth states":
        return ["Texas", "Florida", "North Carolina", "South Carolina", "Arizona"]
    else:
        return ["California", "Texas", "Florida", "New York"]

# =========================
# Tab 1: Overview
# =========================
with tab1:
    st.subheader("Project Overview")


    st.markdown("""
<div class="note-box">
<b>Data limitation:</b><br>
The year <b>2020 is excluded</b> from this analysis because migration patterns during COVID-19 were highly abnormal. 
Travel restrictions, temporary relocations, and remote work created short-term movements that do not reflect stable trends. 
To keep the analysis comparable across years, this dashboard focuses on non-pandemic periods.
</div>
""", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="note-box">
    <b>Why this project?</b><br>
    People are moving across U.S. states in uneven ways. Some states attract many new residents,
    while others lose more people than they gain. This project uses migration and unemployment data
    to explore where people are moving, which states are gaining or losing residents, and whether
    labor market conditions help explain these patterns.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
    <b>Data sources:</b><br>
    - U.S. interstate migration flow data, cleaned into state-level inflow, outflow, and net migration measures.<br>
    - State-level unemployment data, merged by state and year.<br><br>
    <b>Key definition:</b> Net migration = inflow − outflow.
    A negative value means more people left the state than entered from other U.S. states.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Dashboard Roadmap")

    r1, r2, r3 = st.columns(3)

    with r1:
        st.markdown("""
        **Migration Map**  
        Shows which states are gaining or losing people geographically.
        """)

    with r2:
        st.markdown("""
        **State Trends**  
        Compares migration and unemployment patterns over time.
        """)

    with r3:
        st.markdown("""
        **Migration Network**  
        Shows the largest state-to-state migration flows.
        """)

    st.markdown("---")

    st.subheader(f"National Snapshot, {global_year}")

    df_year = df[df["year"] == global_year].copy()

    top_gain = df_year.loc[df_year["net_migration"].idxmax()]
    top_loss = df_year.loc[df_year["net_migration"].idxmin()]
    top_inflow = df_year.loc[df_year["inflow"].idxmax()]
    top_outflow = df_year.loc[df_year["outflow"].idxmax()]

    total_inflow = int(df_year["inflow"].sum())
    total_outflow = int(df_year["outflow"].sum())
    total_movement = total_inflow + total_outflow
    avg_unemp = df_year["unemployment_rate"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Inflow", f"{total_inflow:,}")
    c2.metric("Total Outflow", f"{total_outflow:,}")
    c3.metric("Total Movement", f"{total_movement:,}")
    c4.metric("Average Unemployment", f"{avg_unemp:.1f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Top Net Gain", top_gain["destination"], f"{int(top_gain['net_migration']):,}")
    c6.metric("Top Net Loss", top_loss["destination"], f"{int(top_loss['net_migration']):,}")
    c7.metric("Highest Inflow", top_inflow["destination"], f"{int(top_inflow['inflow']):,}")
    c8.metric("Highest Outflow", top_outflow["destination"], f"{int(top_outflow['outflow']):,}")

    st.markdown("""
    <div class="insight-box">
    <b>Main finding preview:</b> Migration is not simply about whether a state is popular.
    Large states can receive many movers and still show net outflow if even more people leave.
    This is why the dashboard separates inflow, outflow, and net migration.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        gain_df = df_year.sort_values("net_migration", ascending=False).head(top_n)
        fig_gain = px.bar(
            gain_df,
            x="net_migration",
            y="destination",
            orientation="h",
            title=f"Top {top_n} Net Migration Gain States",
            labels={"net_migration": "Net Migration", "destination": "State"},
            color_discrete_sequence=["#1b9e77"]
        )
        fig_gain.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_gain, use_container_width=True)

    with col2:
        loss_df = df_year.sort_values("net_migration", ascending=True).head(top_n)
        fig_loss = px.bar(
            loss_df,
            x="net_migration",
            y="destination",
            orientation="h",
            title=f"Top {top_n} Net Migration Loss States",
            labels={"net_migration": "Net Migration", "destination": "State"},
            color_discrete_sequence=["#d95f02"]
        )
        fig_loss.update_layout(yaxis={"categoryorder": "total descending"})
        st.plotly_chart(fig_loss, use_container_width=True)

    st.subheader("Inflow vs Outflow for High-Inflow States")

    major_states = df_year.sort_values("inflow", ascending=False).head(top_n)
    major_long = major_states.melt(
        id_vars=["destination"],
        value_vars=["inflow", "outflow"],
        var_name="Flow Type",
        value_name="People"
    )

    fig_compare = px.bar(
        major_long,
        x="destination",
        y="People",
        color="Flow Type",
        barmode="group",
        title=f"Inflow and Outflow Comparison, {global_year}",
        labels={"destination": "State"},
        color_discrete_map={
            "inflow": "#4C78A8",
            "outflow": "#72B7B2"
        }
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> The same state can be both a major destination and a major origin.
    That is why inflow and outflow should be read together.
    </div>
    """, unsafe_allow_html=True)

    if show_tables:
        st.subheader("Full State Table")
        st.dataframe(
            df_year[["destination", "inflow", "outflow", "net_migration", "unemployment_rate"]]
            .sort_values("net_migration", ascending=False),
            use_container_width=True
        )

# =========================
# Tab 2: Migration Map
# =========================
with tab2:
    st.subheader("Geographic View")

    metric_label = st.radio(
        "Map metric",
        ["Net Migration", "Inflow", "Outflow", "Unemployment Rate"],
        horizontal=True
    )

    metric_map = {
        "Net Migration": "net_migration",
        "Inflow": "inflow",
        "Outflow": "outflow",
        "Unemployment Rate": "unemployment_rate"
    }

    metric = metric_map[metric_label]
    map_df = df[df["year"] == global_year].copy()

    if metric == "net_migration":
        color_scale = [
            [0.0, "#d95f02"],
            [0.5, "#f7f7f7"],
            [1.0, "#1b9e77"]
        ]
        midpoint = 0
    else:
        color_scale = "Viridis"
        midpoint = None

    fig_map = px.choropleth(
        map_df,
        locations="state_code",
        locationmode="USA-states",
        color=metric,
        scope="usa",
        hover_name="destination",
        hover_data={
            "net_migration": ":,",
            "inflow": ":,",
            "outflow": ":,",
            "unemployment_rate": ":.1f",
            "state_code": False
        },
        color_continuous_scale=color_scale,
        color_continuous_midpoint=midpoint,
        title=f"{metric_label} by State, {global_year}"
    )

    fig_map.update_layout(height=650)
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> The net migration map uses a diverging color scale centered at zero. 
    Green shows net gain, while orange shows net loss, making gaining and losing states easier to compare.
    </div>
    """, unsafe_allow_html=True)

    if show_tables:
        st.dataframe(
            map_df[["destination", "inflow", "outflow", "net_migration", "unemployment_rate"]],
            use_container_width=True
        )

# =========================
# Tab 3: Inflow vs Outflow
# =========================
with tab3:
    st.subheader("Inflow vs Outflow")

    selected_state = st.selectbox(
        "Select a state",
        states,
        index=states.index("California") if "California" in states else 0
    )

    state_df = df[df["destination"] == selected_state].copy()
    selected_row = state_df[state_df["year"] == global_year].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inflow", f"{int(selected_row['inflow']):,}")
    c2.metric("Outflow", f"{int(selected_row['outflow']):,}")
    c3.metric("Net Migration", f"{int(selected_row['net_migration']):,}")
    c4.metric("Unemployment", f"{selected_row['unemployment_rate']:.1f}%")

    flow_long = state_df.melt(
        id_vars=["year", "destination"],
        value_vars=["inflow", "outflow", "net_migration"],
        var_name="Measure",
        value_name="People"
    )

    fig_state_flow = px.line(
        flow_long,
        x="year",
        y="People",
        color="Measure",
        markers=True,
        title=f"Inflow, Outflow, and Net Migration Over Time: {selected_state}",
        labels={"year": "Year"},
        color_discrete_map={
            "inflow": "#4C78A8",
            "outflow": "#72B7B2",
            "net_migration": "#F58518"
        }
    )
    fig_state_flow.update_xaxes(tickmode="array", tickvals=years)
    st.plotly_chart(fig_state_flow, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> This page shows the mechanism behind net migration. 
    Negative net migration happens when outflow is larger than inflow.
    </div>
    """, unsafe_allow_html=True)

    if show_tables:
        st.dataframe(
            state_df[["year", "inflow", "outflow", "net_migration", "unemployment_rate"]],
            use_container_width=True
        )

# =========================
# Tab 4: State Trends
# =========================
with tab4:
    st.subheader("State Trends")

    default_states = get_default_states(state_group)

    if state_group == "Custom":
        selected_states = st.multiselect(
            "Select states",
            states,
            default=["California", "Texas", "Florida", "New York"]
        )
    else:
        selected_states = default_states
        st.markdown(
            f"<div class='small-note'>Current group: <b>{state_group}</b> — {', '.join(selected_states)}</div>",
            unsafe_allow_html=True
        )

    trend_df = df[df["destination"].isin(selected_states)].copy()

    st.markdown("""
    <div class="small-note">
    Colors here are only used to distinguish states. They do not represent political categories.
    </div>
    """, unsafe_allow_html=True)

    fig_net = px.line(
        trend_df,
        x="year",
        y="net_migration",
        color="destination",
        markers=True,
        title="Net Migration Over Time",
        labels={"year": "Year", "net_migration": "Net Migration", "destination": "State"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_net.update_xaxes(tickmode="array", tickvals=years)
    st.plotly_chart(fig_net, use_container_width=True)

    fig_unemp = px.line(
        trend_df,
        x="year",
        y="unemployment_rate",
        color="destination",
        markers=True,
        title="Unemployment Rate Over Time",
        labels={"year": "Year", "unemployment_rate": "Unemployment Rate", "destination": "State"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_unemp.update_xaxes(tickmode="array", tickvals=years)
    st.plotly_chart(fig_unemp, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> State migration trends do not move in the same way. 
    Sun Belt states often show gains, while several coastal states show persistent net outflow.
    </div>
    """, unsafe_allow_html=True)

    if show_tables:
        summary = trend_df.groupby("destination").agg(
            avg_net_migration=("net_migration", "mean"),
            avg_inflow=("inflow", "mean"),
            avg_outflow=("outflow", "mean"),
            avg_unemployment=("unemployment_rate", "mean")
        ).reset_index()

        st.dataframe(summary, use_container_width=True)

# =========================
# Tab 5: Migration vs Unemployment
# =========================
with tab5:
    st.subheader("Migration vs Unemployment")

    scatter_df = df[df["year"] == global_year].copy()

    fig_scatter = px.scatter(
        scatter_df,
        x="unemployment_rate",
        y="net_migration",
        hover_name="destination",
        size="inflow",
        trendline="ols",
        title=f"Migration vs Unemployment, {global_year}",
        labels={
            "unemployment_rate": "Unemployment Rate",
            "net_migration": "Net Migration"
        },
        color_discrete_sequence=["#4C78A8"]
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    corr = scatter_df["unemployment_rate"].corr(scatter_df["net_migration"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Correlation", f"{corr:.2f}")
    c2.metric(
        "Highest Unemployment",
        scatter_df.loc[scatter_df["unemployment_rate"].idxmax(), "destination"]
    )
    c3.metric(
        "Lowest Unemployment",
        scatter_df.loc[scatter_df["unemployment_rate"].idxmin(), "destination"]
    )

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> The relationship between unemployment and net migration is weak in this view. 
    Migration is shaped by many factors, not labor market conditions alone.
    </div>
    """, unsafe_allow_html=True)

    if show_tables:
        st.dataframe(
            scatter_df[["destination", "unemployment_rate", "net_migration", "inflow", "outflow"]],
            use_container_width=True
        )

# =========================
# Tab 6: Migration Network
# =========================
with tab6:
    st.subheader("State-to-State Migration Network")

    network_year = global_year
    if network_year not in flow_years:
        network_year = max(flow_years)

    n_edges = st.slider(
        "Number of largest flows to show",
        min_value=25,
        max_value=200,
        value=100,
        step=25
    )

    flow_year = flows[flows["year"] == network_year].copy()
    flow_year = flow_year[flow_year["origin"] != flow_year["destination"]]
    flow_top = flow_year.sort_values("flow", ascending=False).head(n_edges)

    flow_top = flow_top[
        flow_top["origin"].isin(state_centers.keys()) &
        flow_top["destination"].isin(state_centers.keys())
    ].copy()

    fig_geo_net = go.Figure()

    if len(flow_top) > 0:
        max_flow = flow_top["flow"].max()

        for _, row in flow_top.iterrows():
            origin = row["origin"]
            dest = row["destination"]
            flow = row["flow"]

            lat1, lon1 = state_centers[origin]
            lat2, lon2 = state_centers[dest]

            width = 0.6 + 5 * (flow / max_flow)

            fig_geo_net.add_trace(go.Scattergeo(
                lon=[lon1, lon2],
                lat=[lat1, lat2],
                mode="lines",
                line=dict(width=width, color="rgba(76,120,168,0.45)"),
                hoverinfo="text",
                text=f"{origin} → {dest}<br>Flow: {flow:,.0f}",
                showlegend=False
            ))

        node_flow = {}
        for _, row in flow_top.iterrows():
            node_flow[row["origin"]] = node_flow.get(row["origin"], 0) + row["flow"]
            node_flow[row["destination"]] = node_flow.get(row["destination"], 0) + row["flow"]

        node_states = sorted(node_flow.keys())
        node_lats = [state_centers[s][0] for s in node_states]
        node_lons = [state_centers[s][1] for s in node_states]
        node_sizes = [
            8 + 25 * (node_flow[s] / max(node_flow.values()))
            for s in node_states
        ]

        fig_geo_net.add_trace(go.Scattergeo(
            lon=node_lons,
            lat=node_lats,
            mode="markers+text",
            text=[state_codes.get(s, s) for s in node_states],
            textposition="top center",
            marker=dict(
                size=node_sizes,
                color="#F58518",
                line=dict(width=1, color="white")
            ),
            hoverinfo="text",
            hovertext=[
                f"{s}<br>Total shown flow: {node_flow[s]:,.0f}"
                for s in node_states
            ],
            showlegend=False
        ))

    fig_geo_net.update_layout(
        title=f"Top {n_edges} State-to-State Migration Flows, {network_year}",
        height=720,
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="rgb(245,245,245)",
            subunitcolor="white",
            countrycolor="white",
            showlakes=True,
            lakecolor="white"
        )
    )

    st.plotly_chart(fig_geo_net, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> The network is arranged geographically. 
    This makes the flows easier to read because users can see both flow strength and location. 
    Thicker lines represent larger migration flows.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="small-note">
    Note: This page only shows the largest flows selected by the slider, so smaller state-to-state movements are filtered out.
    </div>
    """, unsafe_allow_html=True)

    if show_tables:
        st.subheader("Top State-to-State Flows")
        st.dataframe(
            flow_top[["origin", "destination", "flow"]].head(20),
            use_container_width=True
        )
