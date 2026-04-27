import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from pyvis.network import Network

# =========================
# Page setup
# =========================
st.set_page_config(page_title="Moving America", layout="wide")

# =========================
# Style
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.main-title {
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 0.2rem;
}
.subtitle {
    font-size: 18px;
    color: #6b7280;
    margin-bottom: 1.5rem;
}
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
</style>
""", unsafe_allow_html=True)

# =========================
# Load data
# =========================
df = pd.read_csv("final_data.csv")
flows = pd.read_csv("migration_flows_clean.csv")

df["year"] = df["year"].astype(int)
flows["year"] = flows["year"].astype(int)

# make sure correct column names exist
if "destination" not in df.columns and "state" in df.columns:
    df = df.rename(columns={"state": "destination"})

if "flow" not in flows.columns:
    possible_flow_cols = [c for c in flows.columns if c.lower() in ["value", "people", "migration"]]
    if possible_flow_cols:
        flows = flows.rename(columns={possible_flow_cols[0]: "flow"})

flows["flow"] = pd.to_numeric(flows["flow"], errors="coerce")
flows = flows.dropna(subset=["flow"])

years = sorted(df["year"].unique())
states = sorted(df["destination"].unique())
flow_years = sorted(flows["year"].unique())

# state abbreviation for Plotly map
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

df["state_code"] = df["destination"].map(state_codes)

# =========================
# Sidebar
# =========================
st.sidebar.title("Controls")

global_year = st.sidebar.selectbox(
    "Main year",
    years,
    index=len(years) - 1
)

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
    <b>Key takeaway:</b> Large states can attract many movers and still show net outflow. 
    California and New York receive many people, but more people leave them.
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
            labels={"net_migration": "Net Migration", "destination": "State"}
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
            labels={"net_migration": "Net Migration", "destination": "State"}
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
        labels={"destination": "State"}
    )
    st.plotly_chart(fig_compare, use_container_width=True)

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
        color_continuous_midpoint=0 if metric == "net_migration" else None,
        title=f"{metric_label} by State, {global_year}"
    )

    fig_map.update_layout(height=600)
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
    <b>Key takeaway:</b> This map is showing <b>{metric_label}</b>. 
    Switching the metric helps separate the size of movement from the balance of movement.
    </div>
    """, unsafe_allow_html=True)

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
        labels={"year": "Year"}
    )
    fig_state_flow.update_xaxes(tickmode="array", tickvals=years)
    st.plotly_chart(fig_state_flow, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> This page explains the mechanism behind net migration. 
    A state has negative net migration when outflow is larger than inflow.
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

    selected_states = st.multiselect(
        "Select states",
        states,
        default=default_states
    )

    trend_df = df[df["destination"].isin(selected_states)].copy()

    fig_net = px.line(
        trend_df,
        x="year",
        y="net_migration",
        color="destination",
        markers=True,
        title="Net Migration Over Time",
        labels={"year": "Year", "net_migration": "Net Migration", "destination": "State"}
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
        labels={"year": "Year", "unemployment_rate": "Unemployment Rate", "destination": "State"}
    )
    fig_unemp.update_xaxes(tickmode="array", tickvals=years)
    st.plotly_chart(fig_unemp, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> Migration trends differ across states even when unemployment moves in similar ways. 
    This suggests migration is shaped by more than labor market conditions.
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
        }
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
    <b>Key takeaway:</b> The relationship is weak. 
    Unemployment may matter, but housing costs, taxes, climate, family ties, and remote work may also shape migration.
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

    net = Network(
        height="700px",
        width="100%",
        bgcolor="white",
        font_color="black",
        directed=True
    )

    nodes = sorted(set(flow_top["origin"]) | set(flow_top["destination"]))

    for node in nodes:
        total_flow = flow_top.loc[
            (flow_top["origin"] == node) | (flow_top["destination"] == node),
            "flow"
        ].sum()

        net.add_node(
            node,
            label=node,
            title=f"{node}<br>Total shown flow: {total_flow:,.0f}",
            value=float(total_flow)
        )

    for _, row in flow_top.iterrows():
        net.add_edge(
            row["origin"],
            row["destination"],
            value=float(row["flow"]),
            title=f"{row['origin']} → {row['destination']}: {row['flow']:,.0f}"
        )

    net.repulsion(node_distance=180, spring_length=150)
    net.save_graph("migration_network.html")

    with open("migration_network.html", "r", encoding="utf-8") as f:
        html = f.read()

    components.html(html, height=750, scrolling=True)

    st.markdown("""
    <div class="insight-box">
    <b>Key takeaway:</b> The network highlights the largest state-to-state migration flows. 
    Large states often appear as hubs because they both send and receive many movers.
    </div>
    """, unsafe_allow_html=True)

    if show_tables:
        st.subheader("Top State-to-State Flows")
        st.dataframe(
            flow_top[["origin", "destination", "flow"]].head(20),
            use_container_width=True
        )