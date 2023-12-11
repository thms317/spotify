import ast
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display
from wordcloud import WordCloud


def show(df_stats: pd.DataFrame, n: int | None = None) -> None:
    """Display the DataFrame in a stylized format, focusing on key columns."""
    df_stats.style.set_table_styles(
        [{"selector": "th", "props": [("font-size", "12pt")]}]
    ).background_gradient(cmap="viridis")
    df_display = df_stats[["name", "artist", "album", "added_by", "added_at"]]
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
