from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "youth_unemp.csv"
REQUIRED_COLUMNS = {
    "sex",
    "age",
    "employment_status",
    "education_level",
    "region",
    "urban_rural",
}


st.set_page_config(
    page_title="Youth Employment Intelligence — Ghana",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: #0B1220;
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stMain"] {
        background: #0B1220;
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] {
        background: #111827;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #FFFFFF;
        color: #17324D !important;
        border-radius: 8px;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #17324D !important;
    }

    [data-testid="stSidebar"] [role="listbox"] {
        background: #FFFFFF;
    }

    [data-testid="stSidebar"] [role="option"] {
        color: #17324D !important;
    }

    .stMarkdown p,
    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: #FFFFFF !important;
    }

    [data-testid="stMain"] [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] label {
        color: #FFFFFF !important;
    }

    h1,
    h2,
    h3,
    h4 {
        color: #FFFFFF !important;
    }

    [data-testid="stTextInput"] input {
        background: #FFFFFF;
        color: #17324D;
        border: 1px solid #AEBBC8;
        border-radius: 8px;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #627386;
        opacity: 1;
    }

    [data-testid="stAlert"] {
        background: #162235;
        color: #FFFFFF;
        border-color: #334155;
    }

    [data-testid="stAlert"] p {
        color: #FFFFFF !important;
    }

    .dashboard-header {
        background: linear-gradient(135deg, #17324D 0%, #234D70 100%);
        border-radius: 18px;
        padding: 2rem 2.25rem;
        margin: 0 0 1.5rem 0;
        box-shadow: 0 8px 24px rgba(23, 50, 77, 0.16);
    }

    .dashboard-title {
        color: #FFFFFF !important;
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        margin: 0;
    }

    .dashboard-subtitle {
        color: #FFFFFF !important;
        font-size: 1rem;
        font-weight: 500;
        margin: 0.45rem 0 0 0;
    }

    h3 {
        color: #FFFFFF;
        font-weight: 700;
        margin-top: 2rem;
    }

    [data-testid="stMetric"] {
        background: #162235;
        border: 1px solid #334155;
        border-top: 4px solid #D4A72C;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 4px 14px rgba(23, 50, 77, 0.07);
    }

    [data-testid="stMetricLabel"] {
        color: #FFFFFF;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF;
        font-weight: 800;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
    }

    .stDownloadButton button {
        background: #D4A72C;
        color: #17324D;
        border: none;
        border-radius: 8px;
        font-weight: 700;
    }

    .stDownloadButton button:hover {
        background: #F2C94C;
        color: #17324D;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="dashboard-header">
        <p class="dashboard-title">YOUTH EMPLOYMENT INTELLIGENCE</p>
        <p class="dashboard-subtitle">Ghana | Youth aged 15–35</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def load_dataset() -> pd.DataFrame | None:
    """Load the local CSV, or let the user upload it if it is not present."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)

    uploaded_file = st.file_uploader(
        "Upload your cleaned youth dataset (CSV)",
        type="csv",
    )
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)

    st.info(
        "Place your CSV at data/youth_unemp.csv "
        "or upload it above to continue."
    )
    return None


def calculate_kpis(data: pd.DataFrame) -> dict[str, int | float]:
    """Calculate overview counts and the labour-force unemployment rate."""
    employment_counts = data["employment_status"].value_counts()
    employed = int(employment_counts.get("Employed", 0))
    unemployed = int(employment_counts.get("Unemployed", 0))
    not_in_labor_force = int(employment_counts.get("Not in Labor Force", 0))
    labor_force = employed + unemployed
    unemployment_rate = (unemployed / labor_force * 100) if labor_force else 0.0

    return {
        "total_youth": len(data),
        "employed": employed,
        "unemployed": unemployed,
        "not_in_labor_force": not_in_labor_force,
        "unemployment_rate": unemployment_rate,
    }


def calculate_group_rates(
    data: pd.DataFrame, group_column: str, group_order: list[str]
) -> pd.DataFrame:
    """Calculate observed labour-force unemployment rates by group."""
    rows = []
    for group in group_order:
        group_data = data[data[group_column] == group]
        employed = (group_data["employment_status"] == "Employed").sum()
        unemployed = (group_data["employment_status"] == "Unemployed").sum()
        labor_force = employed + unemployed

        if labor_force:
            rows.append(
                {
                    group_column: group,
                    "unemployment_rate": unemployed / labor_force * 100,
                    "labor_force": labor_force,
                }
            )

    return pd.DataFrame(rows)


def calculate_age_education_rates(
    data: pd.DataFrame, age_order: list[str], education_order: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate rates and labour-force counts for every age-education cell."""
    rates = pd.DataFrame(index=age_order, columns=education_order, dtype=float)
    labor_force = pd.DataFrame(index=age_order, columns=education_order, dtype=float)

    for age_group in age_order:
        for education in education_order:
            cell = data[
                (data["age_group"] == age_group)
                & (data["education_level"] == education)
            ]
            employed = (cell["employment_status"] == "Employed").sum()
            unemployed = (cell["employment_status"] == "Unemployed").sum()
            denominator = employed + unemployed

            if denominator:
                rates.loc[age_group, education] = unemployed / denominator * 100
                labor_force.loc[age_group, education] = denominator

    return rates, labor_force


def build_observed_insights(
    age_rates: pd.DataFrame,
    education_rates: pd.DataFrame,
    gender_rates: pd.DataFrame,
    region_rates: pd.DataFrame,
) -> list[str]:
    """Create concise, descriptive insights from the currently filtered data."""
    insights = []

    if not age_rates.empty:
        youngest = age_rates.loc[age_rates["unemployment_rate"].idxmax()]
        oldest = age_rates.loc[age_rates["unemployment_rate"].idxmin()]
        insights.append(
            f"The highest observed age-group unemployment rate is "
            f"{youngest['unemployment_rate']:.2f}% for {youngest['age_group']}; "
            f"the lowest is {oldest['unemployment_rate']:.2f}% for "
            f"{oldest['age_group']}."
        )

    if not education_rates.empty:
        highest_education = education_rates.loc[
            education_rates["unemployment_rate"].idxmax()
        ]
        lowest_education = education_rates.loc[
            education_rates["unemployment_rate"].idxmin()
        ]
        insights.append(
            f"Across education levels, the observed rate ranges from "
            f"{lowest_education['unemployment_rate']:.2f}% for "
            f"{lowest_education['education_level']} to "
            f"{highest_education['unemployment_rate']:.2f}% for "
            f"{highest_education['education_level']}."
        )

    if len(gender_rates) > 1:
        higher_gender = gender_rates.loc[gender_rates["unemployment_rate"].idxmax()]
        lower_gender = gender_rates.loc[gender_rates["unemployment_rate"].idxmin()]
        gap = higher_gender["unemployment_rate"] - lower_gender["unemployment_rate"]
        insights.append(
            f"The observed gender difference is {gap:.2f} percentage points: "
            f"{higher_gender['sex']} is higher than {lower_gender['sex']} in "
            f"the filtered data."
        )

    if not region_rates.empty:
        highest_region = region_rates.iloc[0]
        lowest_region = region_rates.iloc[-1]
        insights.append(
            f"Regional observed rates range from "
            f"{lowest_region['unemployment_rate']:.2f}% in {lowest_region['region']} "
            f"to {highest_region['unemployment_rate']:.2f}% in "
            f"{highest_region['region']}."
        )

    return insights


def add_age_group(data: pd.DataFrame) -> pd.DataFrame:
    """Create the project age bands from the numeric age column."""
    result = data.copy()
    result["age_group"] = pd.cut(
        pd.to_numeric(result["age"], errors="coerce"),
        bins=[14, 19, 24, 29, 35],
        labels=["15–19", "20–24", "25–29", "30–35"],
    )
    return result


def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    """Show sidebar filters and return the rows matching the selections."""
    st.sidebar.header("Filters")

    gender = st.sidebar.selectbox(
        "Gender",
        ["All"] + sorted(data["sex"].dropna().unique().tolist()),
    )
    age_group = st.sidebar.selectbox(
        "Age Group",
        ["All"] + ["15–19", "20–24", "25–29", "30–35"],
    )
    education = st.sidebar.selectbox(
        "Education Level",
        ["All"] + sorted(data["education_level"].dropna().unique().tolist()),
    )
    region = st.sidebar.selectbox(
        "Region",
        ["All"] + sorted(data["region"].dropna().unique().tolist()),
    )
    urban_rural = st.sidebar.selectbox(
        "Urban/Rural",
        ["All"] + sorted(data["urban_rural"].dropna().unique().tolist()),
    )

    filtered = data.copy()
    if gender != "All":
        filtered = filtered[filtered["sex"] == gender]
    if age_group != "All":
        filtered = filtered[filtered["age_group"] == age_group]
    if education != "All":
        filtered = filtered[filtered["education_level"] == education]
    if region != "All":
        filtered = filtered[filtered["region"] == region]
    if urban_rural != "All":
        filtered = filtered[filtered["urban_rural"] == urban_rural]

    return filtered


df = load_dataset()

if df is not None:
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        st.error(
            "The dataset is missing these required columns: "
            + ", ".join(sorted(missing_columns))
        )
    else:
        st.success(f"Dataset loaded successfully: {len(df):,} rows")

        df = add_age_group(df)
        filtered_df = apply_filters(df)
        st.caption(f"Showing {len(filtered_df):,} of {len(df):,} youth records")

        kpis = calculate_kpis(filtered_df)
        st.write("### Overview")
        kpi_columns = st.columns(5)
        kpi_columns[0].metric("Total Youth", f"{kpis['total_youth']:,}")
        kpi_columns[1].metric("Employed", f"{kpis['employed']:,}")
        kpi_columns[2].metric("Unemployed", f"{kpis['unemployed']:,}")
        kpi_columns[3].metric(
            "Not in Labor Force", f"{kpis['not_in_labor_force']:,}"
        )
        kpi_columns[4].metric(
            "Unemployment Rate", f"{kpis['unemployment_rate']:.2f}%"
        )
        st.caption(
            "Unemployment rate = Unemployed ÷ (Employed + Unemployed). "
            "Not in Labor Force is excluded from the denominator."
        )

        age_order = ["15–19", "20–24", "25–29", "30–35"]
        age_rates = calculate_group_rates(filtered_df, "age_group", age_order)
        st.write("### Age Analysis")
        st.caption(
            "Observed labour-force unemployment rate by age group. "
            "This chart describes association, not causation."
        )
        if age_rates.empty:
            st.warning("There are no labour-force records for the selected filters.")
        else:
            age_chart = px.bar(
                age_rates,
                x="age_group",
                y="unemployment_rate",
                text="unemployment_rate",
                labels={
                    "age_group": "Age Group",
                    "unemployment_rate": "Unemployment Rate (%)",
                },
                color_discrete_sequence=["#D4A72C"],
            )
            age_chart.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside",
                textfont_color="#FFFFFF",
                hovertemplate=(
                    "Age group: %{x}<br>"
                    "Observed rate: %{y:.2f}%<br>"
                    "Labour force: %{customdata:,}<extra></extra>"
                ),
                customdata=age_rates["labor_force"],
            )
            age_chart.update_layout(
                yaxis_title="Unemployment Rate (%)",
                xaxis_title=None,
                font={"family": "Inter, sans-serif", "color": "#FFFFFF"},
                paper_bgcolor="#0B1220",
                plot_bgcolor="#0B1220",
                xaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
                yaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
                yaxis_range=[0, max(35, age_rates["unemployment_rate"].max() + 5)],
                showlegend=False,
            )
            st.plotly_chart(age_chart, use_container_width=True)

        education_order = ["Primary", "JHS", "SHS", "Tertiary"]
        education_rates = calculate_group_rates(
            filtered_df, "education_level", education_order
        )
        st.write("### Education Analysis")
        st.caption(
            "Observed labour-force unemployment rate by education level. "
            "This chart describes association, not causation."
        )
        if education_rates.empty:
            st.warning("There are no education records for the selected filters.")
        else:
            education_chart = px.bar(
                education_rates,
                x="education_level",
                y="unemployment_rate",
                text="unemployment_rate",
                labels={
                    "education_level": "Education Level",
                    "unemployment_rate": "Unemployment Rate (%)",
                },
                color_discrete_sequence=["#17324D"],
            )
            education_chart.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside",
                textfont_color="#FFFFFF",
                hovertemplate=(
                    "Education: %{x}<br>"
                    "Observed rate: %{y:.2f}%<br>"
                    "Labour force: %{customdata:,}<extra></extra>"
                ),
                customdata=education_rates["labor_force"],
            )
            education_chart.update_layout(
                yaxis_title="Unemployment Rate (%)",
                xaxis_title=None,
                font={"family": "Inter, sans-serif", "color": "#FFFFFF"},
                paper_bgcolor="#0B1220",
                plot_bgcolor="#0B1220",
                xaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
                yaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
                yaxis_range=[
                    0,
                    max(35, education_rates["unemployment_rate"].max() + 5),
                ],
                showlegend=False,
            )
            st.plotly_chart(education_chart, use_container_width=True)

        gender_order = ["Female", "Male"]
        gender_rates = calculate_group_rates(filtered_df, "sex", gender_order)
        st.write("### Gender Analysis")
        st.caption(
            "Observed labour-force unemployment rate by gender. "
            "This chart describes association, not causation."
        )
        if gender_rates.empty:
            st.warning("There are no gender records for the selected filters.")
        else:
            gender_chart = px.bar(
                gender_rates,
                x="sex",
                y="unemployment_rate",
                text="unemployment_rate",
                labels={
                    "sex": "Gender",
                    "unemployment_rate": "Unemployment Rate (%)",
                },
                color_discrete_sequence=["#7A263A"],
            )
            gender_chart.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside",
                textfont_color="#FFFFFF",
                hovertemplate=(
                    "Gender: %{x}<br>"
                    "Observed rate: %{y:.2f}%<br>"
                    "Labour force: %{customdata:,}<extra></extra>"
                ),
                customdata=gender_rates["labor_force"],
            )
            gender_chart.update_layout(
                yaxis_title="Unemployment Rate (%)",
                xaxis_title=None,
                font={"family": "Inter, sans-serif", "color": "#FFFFFF"},
                paper_bgcolor="#0B1220",
                plot_bgcolor="#0B1220",
                xaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
                yaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
                yaxis_range=[0, max(35, gender_rates["unemployment_rate"].max() + 5)],
                showlegend=False,
            )
            st.plotly_chart(gender_chart, use_container_width=True)

        region_order = sorted(filtered_df["region"].dropna().unique().tolist())
        region_rates = calculate_group_rates(
            filtered_df, "region", region_order
        ).sort_values("unemployment_rate", ascending=False)
        st.write("### Regional Analysis")
        st.caption(
            "Observed labour-force unemployment rate across regions. "
            "This chart describes association, not causation."
        )
        if region_rates.empty:
            st.warning("There are no regional records for the selected filters.")
        else:
            region_chart = px.bar(
                region_rates,
                x="unemployment_rate",
                y="region",
                text="unemployment_rate",
                orientation="h",
                labels={
                    "region": "Region",
                    "unemployment_rate": "Unemployment Rate (%)",
                },
                color_discrete_sequence=["#D4A72C"],
            )
            region_chart.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside",
                textfont_color="#FFFFFF",
                hovertemplate=(
                    "Region: %{y}<br>"
                    "Observed rate: %{x:.2f}%<br>"
                    "Labour force: %{customdata:,}<extra></extra>"
                ),
                customdata=region_rates["labor_force"],
            )
            region_chart.update_layout(
                xaxis_title="Unemployment Rate (%)",
                yaxis_title=None,
                font={"family": "Inter, sans-serif", "color": "#FFFFFF"},
                paper_bgcolor="#0B1220",
                plot_bgcolor="#0B1220",
                xaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
                xaxis_range=[
                    0,
                    max(35, region_rates["unemployment_rate"].max() + 5),
                ],
                showlegend=False,
                yaxis={
                    "categoryorder": "total ascending",
                    "gridcolor": "#334155",
                    "zerolinecolor": "#64748B",
                },
            )
            st.plotly_chart(region_chart, use_container_width=True)

        age_education_rates, age_education_labor_force = (
            calculate_age_education_rates(
                filtered_df, age_order, education_order
            )
        )
        st.write("### Age × Education Analysis")
        st.caption(
            "Observed labour-force unemployment rate by age group and education "
            "level. This chart describes association, not causation."
        )
        heatmap = px.imshow(
            age_education_rates,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale=["#F7F3E8", "#D4A72C", "#17324D"],
            labels={
                "x": "Education Level",
                "y": "Age Group",
                "color": "Unemployment Rate (%)",
            },
        )
        heatmap.update_traces(
            texttemplate="%{z:.2f}%",
            hovertemplate=(
                "Age group: %{y}<br>"
                "Education: %{x}<br>"
                "Observed rate: %{z:.2f}%<br>"
                "Labour force: %{customdata:.0f}<extra></extra>"
            ),
            customdata=age_education_labor_force.to_numpy(),
        )
        heatmap.update_layout(
            xaxis_title="Education Level",
            yaxis_title="Age Group",
            font={"family": "Inter, sans-serif", "color": "#FFFFFF"},
            paper_bgcolor="#0B1220",
            plot_bgcolor="#0B1220",
            xaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
            yaxis={"gridcolor": "#334155", "zerolinecolor": "#64748B"},
            coloraxis_colorbar={
                "title": {"text": "Rate (%)", "font": {"color": "#FFFFFF"}},
                "tickfont": {"color": "#FFFFFF"},
            },
        )
        st.plotly_chart(heatmap, use_container_width=True)

        st.write("### Observed Insights")
        st.caption(
            "These statements summarize patterns in the selected data. "
            "They describe association and should not be interpreted as causal evidence."
        )
        insights = build_observed_insights(
            age_rates, education_rates, gender_rates, region_rates
        )
        for insight in insights:
            st.markdown(f"- {insight}")

        st.write("### Data Explorer")
        st.caption(
            "Search the currently filtered records, inspect the results, "
            "or download them as a CSV file."
        )
        search_term = st.text_input(
            "Search records",
            placeholder="Example: Ashanti, Female, Unemployed, or 25",
        )

        explorer_df = filtered_df.copy()
        if search_term.strip():
            search_text = search_term.strip().lower()
            matches = explorer_df.astype(str).apply(
                lambda column: column.str.lower().str.contains(
                    search_text, na=False
                )
            )
            explorer_df = explorer_df[matches.any(axis=1)]

        st.caption(f"Showing {len(explorer_df):,} matching records")
        st.dataframe(
            explorer_df,
            width="stretch"
        )
        st.download_button(
            label="Download filtered data as CSV",
            data=explorer_df.to_csv(index=False).encode("utf-8"),
            file_name="youth_employment_filtered.csv",
            mime="text/csv",
        )
