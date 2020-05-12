from collections import Counter, defaultdict
from typing import Dict, List

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from emoji import UNICODE_EMOJI
from plotly.subplots import make_subplots
from wordcloud import WordCloud

from constants.column_names import (
    TOTAL,
    RAW_TEXT,
    TIMESTAMP,
    SENTIMENT_SCORE,
    ENTITIES,
    WORD_COUNT,
    HOUR,
    DAY,
    SENDER,
    SENTIMENT_LABEL,
    PROFANITY_LABEL,
    CLEANED_TEXT,
    EMOTION_LABEL,
)
from constants.profanity_labels import PROFANE, QUESTIONABLE, CLEAN
from constants.topic_labels import PARTICIPANTS_LABEL, SIMPLIFIED_LABELS
from datautils.stopwords import stopwords
from utils import random_color


class Graph:
    def __init__(
        self,
        df: pd.DataFrame = None,
        dfs: List[pd.DataFrame] = None,
        participants: List[str] = None,
        color_map: Dict = None,
        media_counter: Dict = None,
        title_size: float = 24.0,
        font_size: float = 18,
    ):
        self.df = df
        self.dfs = dfs
        self.participants = participants
        self.color_map = color_map
        self.media_counter = media_counter
        self.title_size = title_size
        self.font_size = font_size
        self.title_dict = {"size": title_size}
        self.font_dict = {"size": font_size}
        self.hide_axis_dict = {
            "showgrid": False,
            "showticklabels": False,
            "zeroline": False,
        }

    def pie_charts(self) -> go.Figure:
        # @title Frequency Analysis
        # @markdown What stories do the numbers tell?

        # Find out who initiates contact the most. We'll just say the first person to
        # text after 4 am on any given day is the initiator (even if it's a conversation continuing from the day before)
        initiator_dict = defaultdict(int)
        previous_timestamp = pd.Timestamp("1960-01-01T12")
        for timestamp, sender in self.df[[TIMESTAMP, SENDER]].values:
            if timestamp.date() == previous_timestamp.date():
                continue
            if timestamp.hour >= 4:
                initiator_dict[sender] += 1
            previous_timestamp = timestamp

        # Find the number of emojis each person texts
        emoji_counts = defaultdict(int)
        for i_df, participant in zip(self.dfs, self.participants):
            c = Counter(" ".join(i_df[RAW_TEXT].values))
            emoji_count = 0
            for char, count in c.items():
                if char in UNICODE_EMOJI:
                    emoji_count += count
            emoji_counts[participant] = emoji_count

        # Count the number of profane messages
        swear_count = defaultdict(int)
        for i_df, alias in zip(self.dfs, self.participants):
            try:
                swear_count[alias] = i_df[PROFANITY_LABEL].value_counts()[
                    PROFANE
                ]
            except KeyError:
                swear_count[alias] = 0

        # Figure setup
        specs = [
            [{"type": "pie"}, {"type": "pie"}],
            [{"type": "pie"}, {"type": "pie"}],
        ]
        fig = make_subplots(rows=2, cols=2, specs=specs)

        # Define pie charts
        pull_values = [0.03] * len(self.participants)
        fig.add_trace(
            go.Pie(
                title="Emojis Used 🙂",
                labels=list(emoji_counts.keys()),
                values=list(emoji_counts.values()),
            ),
            1,
            1,
        )

        fig.add_trace(
            go.Pie(
                title="Media Sent 🎥",
                labels=list(self.media_counter.keys()),
                values=list(self.media_counter.values()),
            ),
            1,
            2,
        )

        fig.add_trace(
            go.Pie(
                title="Conversations Initiated 🥇",
                labels=list(initiator_dict.keys()),
                values=list(initiator_dict.values()),
            ),
            2,
            1,
        )

        fig.add_trace(
            go.Pie(
                title="Swearing 🤬",
                labels=list(swear_count.keys()),
                values=list(swear_count.values()),
            ),
            2,
            2,
        )

        if self.color_map:
            fig.update_traces(marker_colors=list(self.color_map.values()))

        fig.update_traces(
            hoverinfo="label+percent",
            textinfo="label+value",
            textposition="inside",
            textfont_size=self.font_size,
            pull=pull_values,
            hole=0.4,
            titlefont=self.title_dict,
        )
        fig.update_layout(
            title_x=0.5,
            title_font={"size": self.title_size * 1.5},
            showlegend=False,
            annotations=[
                dict(text="🍩", x=0.501, y=0.5, font_size=50, showarrow=False)
            ],
            height=1200,
        )

        fig = go.Figure(fig)
        return fig

    def daily_messages(self) -> go.Figure:
        fig = go.Figure()

        for i_df, alias in zip(self.dfs, self.participants):
            messages_day = (
                i_df.groupby(pd.Grouper(key=TIMESTAMP, freq="D"))
                .count()
                .reset_index()
            )
            fig.add_trace(
                go.Bar(
                    x=messages_day[TIMESTAMP],
                    y=messages_day[RAW_TEXT],
                    name=alias,
                )
            )

        if self.color_map:
            for alias, color in self.color_map.items():
                fig.update_traces(selector={"name": alias}, marker_color=color)

        fig.update_layout(
            barmode="stack",
            title="Number of Daily Messages 🗓️",
            title_x=0.5,
            title_font=self.title_dict,
            font=self.font_dict,
            hovermode="x",
        )

        return fig

    def word_distribution(self) -> go.Figure:
        fig = go.Figure()

        for i_df, alias in zip(self.dfs, self.participants):
            word_count_distribution = (
                i_df.groupby(WORD_COUNT).count().reset_index()
            )
            fig.add_trace(
                go.Bar(
                    x=word_count_distribution[WORD_COUNT],
                    y=word_count_distribution[RAW_TEXT],
                    name=alias,
                )
            )

        if self.color_map:
            for alias, color in self.color_map.items():
                fig.update_traces(selector={"name": alias}, marker_color=color)

        fig.update_layout(
            barmode="stack",
            title="Word Count Distribution 🧮",
            title_x=0.5,
            title_font=self.title_dict,
            font=self.font_dict,
            xaxis_title="Word Count",
            yaxis_title="Messages",
            hovermode="x",
            height=600,
        )

        return fig

    def word_cloud(self):
        wc = WordCloud(
            stopwords=stopwords(),
            max_words=2500,
            color_func=lambda word, font_size, position, orientation, random_state, font_path: random_color(),
        )
        wc.generate_from_frequencies(
            pd.Series(
                np.concatenate(self.df[CLEANED_TEXT].values)
            ).value_counts()
        )

        word_list = []
        freq_list = []
        fontsize_list = []
        position_list = []
        orientation_list = []
        color_list = []
        for (word, freq), fontsize, position, orientation, color in wc.layout_:
            word_list.append(word)
            freq_list.append(freq)
            fontsize_list.append(fontsize)
            position_list.append(position)
            orientation_list.append(orientation)
            color_list.append(color)

        # get the positions
        x = []
        y = []
        for i in position_list:
            x.append(i[0])
            y.append(i[1])

        # get the relative occurrence frequencies
        new_freq_list = []
        for i in freq_list:
            new_freq_list.append(i * 100)

        trace = go.Scatter(
            x=x,
            y=y,
            textfont=dict(size=new_freq_list, color=color_list),
            hoverinfo="text",
            hovertext=[
                "{} {:.2f}%".format(w, f * 100)
                for w, f in zip(word_list, freq_list)
            ],
            mode="text",
            text=word_list,
        )

        layout = go.Layout(
            xaxis=self.hide_axis_dict,
            yaxis=self.hide_axis_dict,
            title="Word Cloud ☁️",
            titlefont_size=self.title_size,
            title_x=0.5,
        )

        fig = go.Figure(data=[trace], layout=layout)

        return fig

    def time_heat_map(self) -> go.Figure:
        time_tuples = []
        for i in range(24):
            for j in range(7):
                time_tuples.append((i, j))

        messages_per_time_slot = (
            self.df.groupby([HOUR, DAY])
            .count()
            .reindex(time_tuples)
            .unstack()[RAW_TEXT]
        )

        times = [
            "0:00",
            "1:00",
            "2:00",
            "3:00",
            "4:00",
            "5:00",
            "6:00",
            "7:00",
            "8:00",
            "9:00",
            "10:00",
            "11:00",
            "12:00",
            "13:00",
            "14:00",
            "15:00",
            "16:00",
            "17:00",
            "18:00",
            "19:00",
            "20:00",
            "21:00",
            "22:00",
            "23:00",
        ]

        weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        fig = go.Figure(
            go.Heatmap(
                x=weekdays,
                y=times,
                z=messages_per_time_slot,
                colorbar={"title": "Number of Texts"},
                colorscale="YlOrRd",
                hoverongaps=False,
                hovertemplate="Day: %{x}<br>Time: %{y}<br>Number of Texts: %{z}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Messaging Time ⌚",
            title_x=0.5,
            title_font=self.title_dict,
            font=self.font_dict,
            height=600,
        )

        return fig

    def emotion_tree_map(self) -> go.Figure:
        # @title Sentiment Analysis
        # @markdown So now that we have established some patterns, what other insights can we glean?
        color_dict = {
            "(?)": "#",
            "❔": "#f1ffe7",
            "anger": "#ef553b",
            "anticipation": "#f49d37",
            "disgust": "#8faf00",
            "emotion": "#533a71",
            "fear": "#000000",
            "joy": "#00cc96",
            "sadness": "#3e92cc",
            "surprise": "#eac435",
            "trust": "#4f3824",
        }

        # colors = df.apply((lambda x: f(x.col_1, x.col_2), axis=1)
        self.df[TOTAL] = TOTAL
        fig = px.treemap(
            self.df,
            path=[TOTAL, SENDER, EMOTION_LABEL, SENTIMENT_LABEL, RAW_TEXT],
            color="Emotion Label",
            color_discrete_map=color_dict,
        )

        fig.update_traces(
            textfont_size=self.font_size,
            hovertemplate="Number of Messages: %{value}<extra></extra>",
        )
        fig.update_layout(
            title="Emotion Breakdown 💐",
            title_x=0.5,
            title_font=self.title_dict,
            showlegend=False,
            height=700,
        )

        return fig

    def sentiment_over_time(self) -> go.Figure:
        # @markdown How have our interactions changed over time? What do the peaks and troughs correspond to here?
        fig = go.Figure()

        for i_df, alias in zip(self.dfs, self.participants):
            sentiment_day = (
                i_df.groupby(pd.Grouper(key=TIMESTAMP, freq="D"))
                .mean()
                .reset_index()
            )
            fig.add_trace(
                go.Scatter(
                    x=sentiment_day[TIMESTAMP],
                    y=sentiment_day[SENTIMENT_SCORE],
                    name=alias,
                    mode="lines+markers",
                    connectgaps=True,
                )
            )

        if self.color_map:
            for alias, color in self.color_map.items():
                fig.update_traces(selector={"name": alias}, marker_color=color)

        fig.add_shape(
            # Line Horizontal
            type="line",
            x0=self.df[TIMESTAMP][0],
            x1=self.df[TIMESTAMP][len(self.df) - 1],
            y0=0,
            y1=0,
            line=dict(color="gray", width=2, dash="dashdot"),
        )

        fig.update_layout(
            title="Sentiment over Time ⌚",
            title_x=0.5,
            title_font=self.title_dict,
            yaxis_title="Positivity",
            font=self.font_dict,
            hovermode="x unified",
        )

        return fig

    def profanity_sunburst(self) -> go.Figure:
        color_dict = {
            "(?)": "#",
            PROFANE: "#dc493a",
            CLEAN: "#e3ebff",
            QUESTIONABLE: "#f3ffb9",
        }

        self.df[TOTAL] = TOTAL
        fig = px.sunburst(
            self.df,
            path=[TOTAL, SENDER, PROFANITY_LABEL, RAW_TEXT],
            color=PROFANITY_LABEL,
            color_discrete_map=color_dict,
        )

        fig.update_traces(
            textfont_size=self.font_size,
            hovertemplate="Number of Messages: %{value} <br> %{label} <extra></extra>",
        )
        fig.update_layout(
            title="Profanity Breakdown 🤬",
            title_x=0.5,
            title_font=self.title_dict,
            showlegend=False,
            height=700,
        )
        return fig

    def topic_graph(self) -> go.Figure:
        # @title Topic Analysis
        # @markdown What are the things you commonly talk about? What are things you've been avoiding? \
        # @markdown Note that the **entity extraction is shaky** because the sentences are so small,
        # but should still be good enough to give a general idea about the topics discussed \
        # @markdown \
        # @markdown The *Topic Graph* is the most informative and comprehensive visualizations,
        # but I've also included some word clouds if graphs aren't your thing.
        # The generated graph will be slightly different each time

        topic_graph = nx.Graph()
        entity_label = "entity_label"
        weight = "weight"

        # Let's generate a graph of the topics discussed
        topic_graph.add_nodes_from(
            self.participants, entity_label=PARTICIPANTS_LABEL
        )
        for i_df, participant in zip(self.dfs, self.participants):
            for entities in i_df[ENTITIES].values:
                for text, label in entities.items():
                    topic_graph.add_node(text, entity_label=label)
                    if topic_graph.has_edge(participant, text):
                        topic_graph[participant][text][weight] += 1
                    else:
                        topic_graph.add_edge(participant, text, weight=1)

        # Remove isolated nodes (can happen when there's an incorrect number of senders)
        topic_graph.remove_nodes_from(list(nx.isolates(topic_graph)))

        # Map each entity label to some random color
        topic_color_map = {
            label: random_color() for label in SIMPLIFIED_LABELS
        }

        # Generate the positions for node plotting based on edge weights
        node_positions = nx.spring_layout(topic_graph)

        # Generate the edge plot
        edge_x = []
        edge_y = []
        for edge in topic_graph.edges():
            x0, y0 = node_positions[edge[0]]
            x1, y1 = node_positions[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            name="Talks about",
            hoverinfo="none",
            mode="lines",
        )

        # Function for mapping node weights to sizes
        def map_size(weight_degree: int) -> int:
            if weight_degree == 1:
                return 10
            elif weight_degree <= 10:
                return 20
            elif weight_degree <= 100:
                return 30
            else:
                return 40

        node_traces = []
        for label in SIMPLIFIED_LABELS:
            node_x = []
            node_y = []
            for node in topic_graph.nodes():
                if label != topic_graph.nodes[node][entity_label]:
                    continue
                x, y = node_positions[node]
                node_x.append(x)
                node_y.append(y)

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                name=label,
                mode="markers",
                hoverinfo="text",
                marker={"color": topic_color_map[label], "line_width": 2},
            )

            node_colors, node_weights, node_text = [], [], []
            for adjacencies in topic_graph.adjacency():
                node_weight = 0
                if topic_graph.nodes[adjacencies[0]][entity_label] != label:
                    continue
                for adjacency in adjacencies[1].values():
                    node_weight += adjacency[weight]
                node_weights.append(node_weight)
                node_text.append(
                    "<b>{}</b> <br>Discussion Frequency: {}".format(
                        adjacencies[0], node_weight
                    )
                )

            node_trace.marker.size = list(
                map(lambda m: map_size(m), node_weights)
            )
            node_trace.text = node_text
            node_traces.append(node_trace)

        fig = go.Figure(
            data=[edge_trace, *node_traces],
            layout=go.Layout(
                title="<br>Topic Graph 📚",
                titlefont_size=self.title_size,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                height=750,
                annotations=[
                    dict(
                        text="To learn how these were extracted, checkout "
                        "<a href='https://spacy.io/usage/linguistic-features/#named-entities'>Spacy</a>",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.005,
                        y=-0.002,
                    )
                ],
                xaxis=self.hide_axis_dict,
                yaxis=self.hide_axis_dict,
            ),
        )

        return fig
