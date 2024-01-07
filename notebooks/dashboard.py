import pandas as pd
import plotly.express as px
import streamlit as st
from notebook_functions import (
    average_per_person,
    count_all_items,
    create_2d_scatter_plot,
    create_boxplot,
    create_wordcloud_from_series,
    sort_dataframe,
    top_items_added_by,
    transform_track_duration,
)

df_stats = pd.read_csv("./data/playlist_stats_clean.csv")

st.title("Pallen 2023")

# Total number of tracks
st.metric(label="Number of Tracks in Pallen 2023", value=len(df_stats))

# Tracks added by each person
added_by_count = df_stats["added_by"].value_counts()
fig = px.bar(
    added_by_count,
    title="Number of Tracks Added by Each Person",
    labels={"index": "Added By", "value": "Number of Tracks"},
)
st.plotly_chart(fig)

# Tracks added per month
df_stats["added_at"] = pd.to_datetime(df_stats["added_at"])
df_stats["month_added"] = df_stats["added_at"].dt.month
# Group by month and added_by, then count the number of tracks
grouped_df = df_stats.groupby(["month_added", "added_by"]).size().reset_index(name="tracks")
# Creating a stacked bar chart
fig = px.bar(
    grouped_df,
    x="month_added",
    y="tracks",
    color="added_by",
    title="Number of Tracks Added by Each Person Per Month",
    labels={"month_added": "Month", "tracks": "Number of Tracks"},
    category_orders={"month_added": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
)
st.plotly_chart(fig)

# Tracks per release date
df_stats["release_date"] = pd.to_datetime(df_stats["release_date"])
df_stats["month_released"] = df_stats["release_date"].dt.month
# Group by 'year_month' and count the number of tracks
grouped_df = df_stats.groupby("month_released").size().reset_index(name="tracks")
# Creating a bar chart
fig = px.bar(
    grouped_df,
    x="month_released",
    y="tracks",
    title="Number of Tracks Released Per Month/Year",
    labels={"month_released": "Month Released", "tracks": "Number of Tracks"},
)
st.plotly_chart(fig)

# Artists
total_artist_counts = count_all_items(df_stats, count_what="artist_names")
st.metric(label="Total unique artists", value=len(total_artist_counts))

# Artists Wordcloud
fig = create_wordcloud_from_series(total_artist_counts[:40], title="TOP ARTISTS")
st.pyplot(fig)

# Artists Wordcloud per person
total_artist_counts_by = top_items_added_by(df_stats, count_what="artist_names")
for name in df_stats["added_by"].unique():
    st.metric(
        label=f"Total unique artists added by {name}",
        value=total_artist_counts_by[name]["total_items"],
    )
    fig = create_wordcloud_from_series(
        total_artist_counts_by[name]["top_items_all"][:20],  # type: ignore  # noqa: PGH003
        title=f"TOP ARTISTS\n({name})",
    )
    st.pyplot(fig)

# Genres
total_genres_counts = count_all_items(df_stats, count_what="artists_genres")
st.metric(label="Total unique genres", value=len(total_genres_counts))

fig = create_wordcloud_from_series(total_genres_counts[:40], title="TOP GENRES")
st.pyplot(fig)

# Genres Wordcloud per person
total_genres_counts_by = top_items_added_by(df_stats, count_what="artists_genres")
for name in df_stats["added_by"].unique():
    st.metric(
        label=f"Total unique genres added by {name}",
        value=total_genres_counts_by[name]["total_items"],
    )
    fig = create_wordcloud_from_series(
        total_genres_counts_by[name]["top_items_all"][:20],  # type: ignore  # noqa: PGH003
        title=f"TOP GENRES\n({name})",
    )
    st.pyplot(fig)

# Track Duration
fig = create_boxplot(df_stats, "duration_ms")
st.plotly_chart(fig)
# Average
avg = average_per_person(df_stats, "duration_ms")
for name, value in avg.items():
    st.metric(
        label=f"Average track duration added by {name}",
        value=transform_track_duration(float(value)),
    )
# Depict head/tail of dataframe
df_stats_sorted = sort_dataframe(df_stats, "duration_ms", "duration")
st.dataframe(df_stats_sorted)


# Track popularity
fig = create_boxplot(df_stats, "track_popularity")
st.plotly_chart(fig)
# Average
avg = average_per_person(df_stats, "track_popularity")
for name, value in avg.items():
    st.metric(
        label=f"Average track popularity added by {name}",
        value=value,
    )
# Depict head/tail of dataframe
df_stats_sorted = sort_dataframe(df_stats, "track_popularity")
st.dataframe(df_stats_sorted)

# Artist popularity
fig = create_boxplot(df_stats, "artists_avg_popularity")
st.plotly_chart(fig)
# Average
avg = average_per_person(df_stats, "artists_avg_popularity")
for name, value in avg.items():
    st.metric(
        label=f"Average artist popularity added by {name}",
        value=value,
    )
# Depict head/tail of dataframe
df_stats_sorted = sort_dataframe(df_stats, "artists_avg_popularity")
st.dataframe(df_stats_sorted)

# Energy
fig = create_boxplot(df_stats, "energy")
st.plotly_chart(fig)
# Average
avg = average_per_person(df_stats, "energy")
for name, value in avg.items():
    st.metric(
        label=f"Average track energy added by {name}",
        value=value,
    )
# Depict head/tail of dataframe
df_stats_sorted = sort_dataframe(df_stats, "energy")
st.dataframe(df_stats_sorted)

# Acousticness
fig = create_boxplot(df_stats, "acousticness")
st.plotly_chart(fig)
# Average
avg = average_per_person(df_stats, "acousticness")
for name, value in avg.items():
    st.metric(
        label=f"Average track acousticness added by {name}",
        value=value,
    )
# Depict head/tail of dataframe
df_stats_sorted = sort_dataframe(df_stats, "acousticness")
st.dataframe(df_stats_sorted)

# Instrumentalness
fig = create_boxplot(df_stats, "instrumentalness")
st.plotly_chart(fig)
# Average
avg = average_per_person(df_stats, "instrumentalness")
for name, value in avg.items():
    st.metric(
        label=f"Average track instrumentalness added by {name}",
        value=value,
    )
# Depict head/tail of dataframe
df_stats_sorted = sort_dataframe(df_stats, "instrumentalness")
st.dataframe(df_stats_sorted)

# Tempo
fig = create_boxplot(df_stats, "tempo")
st.plotly_chart(fig)
# Average
avg = average_per_person(df_stats, "tempo")
for name, value in avg.items():
    st.metric(
        label=f"Average track tempo added by {name}",
        value=value,
    )
# Depict head/tail of dataframe
df_stats_sorted = sort_dataframe(df_stats, "tempo")
st.dataframe(df_stats_sorted)

# 2D Scatter plot
fig = create_2d_scatter_plot(
    df_stats, "artists_avg_popularity", "duration_ms", "track_info", "added_by"
)
st.plotly_chart(fig)

# 3voor12 overlap percentage
st.metric(
    label="BONUS: Overlap with 3voor12 Song van het Jaar 2023",
    value="21%",
)

# 3voor12 overlap table
df_overlap = pd.read_csv("./data/3voor12_overlap.csv", index_col="Unnamed: 0")
st.dataframe(df_overlap)
