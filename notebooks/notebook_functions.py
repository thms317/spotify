import ast
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from IPython.display import display
from wordcloud import WordCloud


def show(
    df_stats: pd.DataFrame,
    n: int | None = None,
    column: str | None = None,
    sort_values: bool = False,
) -> None:
    """Display the DataFrame in a stylized format, focusing on key columns."""
    df_stats.style.set_table_styles(
        [{"selector": "th", "props": [("font-size", "12pt")]}]
    ).background_gradient(cmap="viridis")
    column_list = ["name", "artist", "album", "added_by", "added_at"]
    if column:
        column_list = [column, *column_list]
    df_display = df_stats[column_list]
    if sort_values:
        df_display = df_display.sort_values(by=column, ascending=False)
    display(df_display.head(n)) if n else display(df_display)


def count_all_items(df_stats: pd.DataFrame, count_what: str) -> pd.Series:
    """Count the occurrences of each item (artists or genres) in the DataFrame."""
    df_stats_copy = df_stats.copy()
    df_stats_copy[count_what] = df_stats_copy[count_what].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    all_items = []
    for sublist in df_stats_copy[count_what]:
        for item in sublist:
            if isinstance(item, list):  # Nested list
                all_items.extend(item)
            else:
                all_items.append(item)
    item_counts = Counter(all_items)
    return pd.Series(item_counts).sort_values(ascending=False)


def top_items_added_by(
    df_stats: pd.DataFrame, count_what: str, n: int = 5
) -> dict[str, dict[str, int | pd.Series]]:
    """Get the top N items (artists or genres) added by each contributor."""
    contributors_stats = {}
    for person in df_stats["added_by"].unique():
        person_df_copy = df_stats[df_stats["added_by"] == person].copy()
        person_df_copy[count_what] = person_df_copy[count_what].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
        all_person_items = []
        for sublist in person_df_copy[count_what]:
            for item in sublist:
                if isinstance(item, list):
                    all_person_items.extend(item)
                else:
                    all_person_items.append(item)
        items_count = Counter(all_person_items)
        top_items = pd.Series(items_count).sort_values(ascending=False)
        total_unique_items = len(set(all_person_items))
        contributors_stats[person] = {
            "total_items": total_unique_items,
            "top_items": top_items.head(n),
            "top_items_all": top_items,
        }
    return contributors_stats


def create_wordcloud_from_series(data: pd.Series, title: str | None = None) -> None:
    """Generate a word cloud from a pandas Series where each value is a count."""
    # Creating a word cloud
    wordcloud = WordCloud(
        width=800, height=600, background_color="white"
    ).generate_from_frequencies(data)

    # Plotting the WordCloud
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    # Add title in the left upper corner above the plot, in red
    if title:
        plt.text(
            0.5,
            1.05,
            title,
            horizontalalignment="center",
            verticalalignment="top",
            fontsize=30,
            color="red",
            bbox={"facecolor": "white", "alpha": 0.7},
            transform=plt.gca().transAxes,
        )


def create_boxplot(df: pd.DataFrame, column: str, print_top: bool = False) -> None:
    """
    Create an interactive Plotly plot for a specified column in a DataFrame.

    Parameters
    ----------
    df (DataFrame): The DataFrame containing the data.
    column_of_interest (str): The column name for which the plot will be created.
    adder_column (str): The column name indicating who added the track.
    """
    # Creating a Plotly figure
    fig = go.Figure()

    # Get list of adders
    adders = df["added_by"].unique()

    # Add track info to DataFrame
    df["track_info"] = df["name"] + " by " + df["artist"]

    # Define color palette for the plots
    color_palette = px.colors.qualitative.Plotly

    # Adding boxplots and scatter plots for each adder
    for i, adder in enumerate(adders, 1):
        # Filter by adder
        df_adder = df[df["added_by"] == adder]

        # Create boxplot
        fig.add_trace(
            go.Box(
                y=df_adder[column],
                name=adder,
                boxpoints=False,
                x=[i] * len(df_adder),
                hoverinfo="none",
                marker_color=color_palette[i % len(color_palette)],
            )
        )

        # Create scatter plot points with jitter
        jittered_x = np.random.Generator(np.random.PCG64()).normal(i, 0.1, size=len(df_adder))
        fig.add_trace(
            go.Scatter(
                x=jittered_x,
                y=df_adder[column],
                mode="markers",
                name=f"{adder} points",
                text=df_adder["track_info"],
                marker={"size": 6, "color": "grey", "opacity": 0.5},
            )
        )

        # Depict top tracks by the column of interest
        if print_top:
            print(f"Top 5 {column} added by {adder}:")
            show(df_adder, n=5, column=column, sort_values=True)

    # Update layout
    fig.update_layout(
        title=column,
        xaxis={
            "title": "Added By",
            "tickmode": "array",
            "tickvals": list(range(1, len(adders) + 1)),
            "ticktext": adders,
        },
        yaxis={"title": column},
        showlegend=False,
    )

    # Show plot
    fig.show()
