"""
Wikipedia Edit Pattern Analysis
================================
Author  : Amir Nazhan (@Miaoricle)
GitHub  : https://github.com/Miaoricle
Purpose : Analyse contributor activity and collaboration patterns
          on Wikipedia articles using the Wikipedia API.
"""

import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter, defaultdict
from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
MAX_REVISIONS  = 500


def fetch_revisions(article_title, limit=MAX_REVISIONS):
    print(f"\n📡 Fetching revisions for: \'{article_title}\' ...")
    params = {
        "action"  : "query",
        "titles"  : article_title,
        "prop"    : "revisions",
        "rvprop"  : "ids|timestamp|user|size|comment",
        "rvlimit" : limit,
        "format"  : "json",
    }
    response = requests.get(WIKIPEDIA_API, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    pages     = data["query"]["pages"]
    page      = next(iter(pages.values()))
    revisions = page.get("revisions", [])
    print(f"   ✅ {len(revisions)} revisions fetched.")
    return revisions


def build_dataframe(revisions):
    records = []
    for rev in revisions:
        records.append({
            "rev_id"    : rev.get("revid"),
            "parent_id" : rev.get("parentid"),
            "user"      : rev.get("user", "Anonymous"),
            "timestamp" : pd.to_datetime(rev.get("timestamp")),
            "size"      : rev.get("size", 0),
            "comment"   : rev.get("comment", ""),
        })
    df = pd.DataFrame(records)
    df["year"]  = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.to_period("M")
    df["size_change"] = df["size"].diff().fillna(0)
    return df


def analyse_contributors(df):
    stats = (
        df.groupby("user")
        .agg(
            edit_count   = ("rev_id", "count"),
            chars_added  = ("size_change", lambda x: x[x > 0].sum()),
            first_edit   = ("timestamp", "min"),
            last_edit    = ("timestamp", "max"),
        )
        .reset_index()
        .sort_values("edit_count", ascending=False)
    )
    stats["active_days"] = (stats["last_edit"] - stats["first_edit"]).dt.days
    return stats


def build_collaboration_network(df, top_n=30):
    print("\n🕸️  Building collaboration network ...")
    top_users = df["user"].value_counts().head(top_n).index.tolist()
    filtered = df[df["user"].isin(top_users)]
    monthly_editors = defaultdict(set)
    for _, row in filtered.iterrows():
        monthly_editors[str(row["month"])].add(row["user"])
    G = nx.Graph()
    G.add_nodes_from(top_users)
    for _, editors in monthly_editors.items():
        editors = list(editors)
        for i in range(len(editors)):
            for j in range(i + 1, len(editors)):
                u, v = editors[i], editors[j]
                if G.has_edge(u, v):
                    G[u][v]["weight"] += 1
                else:
                    G.add_edge(u, v, weight=1)
    print(f"   ✅ Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    return G


def plot_top_contributors(stats, article_title, top_n=15):
    top = stats.head(top_n)
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.Blues_r([i / top_n for i in range(top_n)])
    bars = ax.barh(top["user"][::-1], top["edit_count"][::-1], color=colors[::-1])
    ax.set_xlabel("Number of Edits", fontsize=12)
    ax.set_title(f"Top {top_n} Contributors — \'{article_title}\'", fontsize=14, fontweight="bold")
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_xlim(0, top["edit_count"].max() * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_contributors.png"), dpi=150)
    plt.close()


def plot_edit_timeline(df, article_title):
    monthly_counts = df.groupby("month").size().reset_index(name="edits")
    monthly_counts["month_str"] = monthly_counts["month"].astype(str)
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(monthly_counts["month_str"], monthly_counts["edits"],
            color="#58a6ff", linewidth=2, marker="o", markersize=4)
    ax.fill_between(monthly_counts["month_str"], monthly_counts["edits"], alpha=0.15, color="#58a6ff")
    step = max(1, len(monthly_counts) // 12)
    ax.set_xticks(monthly_counts["month_str"][::step])
    ax.set_xticklabels(monthly_counts["month_str"][::step], rotation=45, ha="right", fontsize=8)
    ax.set_title(f"Edit Activity Over Time — \'{article_title}\'", fontsize=14, fontweight="bold")
    ax.set_ylabel("Edits per Month")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "edit_timeline.png"), dpi=150)
    plt.close()


def plot_collaboration_network(G, article_title):
    if G.number_of_nodes() == 0:
        return
    degree_centrality = nx.degree_centrality(G)
    node_sizes  = [3000 * degree_centrality[n] + 300 for n in G.nodes()]
    edge_weights = [G[u][v]["weight"] for u, v in G.edges()]
    max_w = max(edge_weights) if edge_weights else 1
    edge_widths = [1 + 3 * (w / max_w) for w in edge_weights]
    pos = nx.spring_layout(G, seed=42, k=0.6)
    node_colors = [degree_centrality[n] for n in G.nodes()]
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    nx.draw_networkx_edges(G, pos, ax=ax, width=edge_widths, edge_color="#58a6ff", alpha=0.4)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=node_colors, cmap=plt.cm.plasma, alpha=0.9)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7, font_color="white", font_weight="bold")
    ax.set_title(f"Co-Editor Collaboration Network — \'{article_title}\'",
                 fontsize=14, fontweight="bold", color="white", pad=15)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "collaboration_network.png"), dpi=150, facecolor="#0d1117")
    plt.close()


def plot_editor_types(df, article_title):
    anon_mask = df["user"].str.match(r"^\d{1,3}(\.\d{1,3}){3}$")
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie([( ~anon_mask).sum(), anon_mask.sum()],
           labels=["Registered Users", "Anonymous (IP)"],
           colors=["#58a6ff", "#f78166"], autopct="%1.1f%%",
           startangle=140, pctdistance=0.82, wedgeprops=dict(width=0.5))
    ax.set_title(f"Editor Types — \'{article_title}\'", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "editor_types.png"), dpi=150)
    plt.close()


def print_summary(df, stats, G, article_title):
    anon_mask  = df["user"].str.match(r"^\d{1,3}(\.\d{1,3}){3}$")
    date_range = f"{df['timestamp'].min().date()} → {df['timestamp'].max().date()}"
    print("\n" + "═" * 55)
    print(f"  📊  ANALYSIS SUMMARY: \'{article_title}\'")
    print("═" * 55)
    print(f"  Total revisions analysed : {len(df)}")
    print(f"  Unique contributors      : {df['user'].nunique()}")
    print(f"  Anonymous edits          : {anon_mask.sum()} ({anon_mask.mean()*100:.1f}%)")
    print(f"  Date range               : {date_range}")
    print(f"  Network nodes / edges    : {G.number_of_nodes()} / {G.number_of_edges()}")
    print("─" * 55)
    print("  🏆  Top 5 Contributors:")
    for i, row in stats.head(5).iterrows():
        print(f"     {stats.index.get_loc(i)+1}. {row['user'][:30]:<30} {row['edit_count']} edits")
    print("═" * 55)


def run_analysis(article_title="Python (programming language)"):
    print("=" * 55)
    print("  Wikipedia Edit Pattern Analyser")
    print("  by Amir Nazhan | github.com/Miaoricle")
    print("=" * 55)
    revisions = fetch_revisions(article_title)
    df        = build_dataframe(revisions)
    stats     = analyse_contributors(df)
    G         = build_collaboration_network(df)
    print("\n📊 Generating visualisations ...")
    plot_top_contributors(stats, article_title)
    plot_edit_timeline(df, article_title)
    plot_collaboration_network(G, article_title)
    plot_editor_types(df, article_title)
    print_summary(df, stats, G, article_title)
    print(f"\n✅ All outputs saved to /outputs/\n")
    return df, stats, G


if __name__ == "__main__":
    ARTICLE = "Artificial intelligence"
    run_analysis(ARTICLE)
