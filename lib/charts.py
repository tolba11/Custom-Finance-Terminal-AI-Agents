"""Plotly chart builders — dark mode, green/red split at baseline."""
import pandas as pd
import plotly.graph_objects as go

GREEN = "#16c784"
RED = "#ea3943"

CHART_VIEWS = ["Performance", "Price", "Candlestick", "Area"]


def split_traces(index, values, baseline):
    """Split a series into above/below-baseline segments with interpolated
    zero crossings. Returns (above_x, above_y, below_x, below_y)."""
    ax, ay, bx, by = [], [], [], []
    vals = list(values)
    idx = list(index)
    prev_v, prev_x = None, None
    for x, v in zip(idx, vals):
        if prev_v is not None and (prev_v - baseline) * (v - baseline) < 0:
            # linear interpolation of crossing point
            frac = (baseline - prev_v) / (v - prev_v)
            try:
                cx = prev_x + (x - prev_x) * frac
            except TypeError:
                cx = x
            ax.append(cx); ay.append(baseline)
            bx.append(cx); by.append(baseline)
        if v >= baseline:
            ax.append(x); ay.append(v)
            bx.append(x); by.append(None)
        else:
            ax.append(x); ay.append(None)
            bx.append(x); by.append(v)
        prev_v, prev_x = v, x
    return ax, ay, bx, by


def _return_badge(fig, x, y, pct):
    color = GREEN if pct >= 0 else RED
    fig.add_annotation(
        x=x, y=y, text=f"{pct:+.2f}%",
        showarrow=False, xanchor="left", xshift=8,
        font=dict(color="#161b26", size=13),
        bgcolor=color, borderpad=4, opacity=0.95,
    )


def render_price_chart(df: pd.DataFrame, view: str = "Performance",
                       baseline_price: float = None, height: int = 480,
                       show_volume: bool = False) -> go.Figure:
    """Main chart with 4 views. For 1D intraday, pass baseline_price =
    yesterday's close so overnight gaps read correctly."""
    fig = go.Figure()
    if df is None or df.empty or "Close" not in df:
        fig.update_layout(template="plotly_dark", height=height)
        return fig

    closes = df["Close"]
    start = baseline_price if baseline_price else float(closes.iloc[0])
    last = float(closes.iloc[-1])
    pct = (last - start) / start * 100 if start else 0.0

    if view == "Performance":
        perf = (closes / start - 1) * 100
        ax, ay, bx, by = split_traces(perf.index, perf.values, 0.0)
        fig.add_trace(go.Scatter(x=ax, y=ay, mode="lines",
                                 line=dict(color=GREEN, width=2), name="Above"))
        fig.add_trace(go.Scatter(x=bx, y=by, mode="lines",
                                 line=dict(color=RED, width=2), name="Below"))
        fig.add_hline(y=0, line_dash="dot", line_color="#5c6575", line_width=1)
        _return_badge(fig, perf.index[-1], float(perf.iloc[-1]), pct)
        fig.update_yaxes(ticksuffix="%")
    elif view == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color=GREEN, decreasing_line_color=RED,
            name="OHLC",
        ))
        fig.update_layout(xaxis_rangeslider_visible=False)
        _return_badge(fig, df.index[-1], last, pct)
    elif view == "Area":
        ax, ay, bx, by = split_traces(closes.index, closes.values, start)
        fig.add_trace(go.Scatter(x=ax, y=ay, mode="lines", fill="tonexty",
                                 line=dict(color=GREEN, width=2),
                                 fillcolor="rgba(34,197,94,0.15)", name="Above"))
        fig.add_trace(go.Scatter(x=bx, y=by, mode="lines", fill="tonexty",
                                 line=dict(color=RED, width=2),
                                 fillcolor="rgba(239,68,68,0.15)", name="Below"))
        fig.add_hline(y=start, line_dash="dot", line_color="#5c6575", line_width=1)
        _return_badge(fig, closes.index[-1], last, pct)
    else:  # Price
        color = GREEN if last >= start else RED
        fig.add_trace(go.Scatter(x=closes.index, y=closes.values, mode="lines",
                                 line=dict(color=color, width=2), name="Close"))
        if baseline_price:
            fig.add_hline(y=baseline_price, line_dash="dot",
                          line_color="#5c6575", line_width=1,
                          annotation_text="Prev close")
        _return_badge(fig, closes.index[-1], last, pct)

    if show_volume and "Volume" in df and view != "Candlestick":
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], yaxis="y2",
                             marker_color="#252c3b", opacity=0.5, name="Volume"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right",
                                      showgrid=False, visible=False))

    fig.update_layout(
        template="plotly_dark", height=height, showlegend=False,
        margin=dict(l=10, r=60, t=20, b=10),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    # hide non-trading gaps for intraday
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])]
                     if not getattr(df.index, "freqstr", None) else None)
    return fig


def render_sparkline(closes: pd.Series, baseline: float = None,
                     height: int = 60) -> go.Figure:
    """Tiny green/red sparkline split at the baseline (period start or
    prev close for 1D)."""
    fig = go.Figure()
    if closes is None or len(closes) == 0:
        fig.update_layout(template="plotly_dark", height=height)
        return fig
    base = baseline if baseline else float(closes.iloc[0])
    ax, ay, bx, by = split_traces(closes.index, closes.values, base)
    fig.add_trace(go.Scatter(x=ax, y=ay, mode="lines",
                             line=dict(color=GREEN, width=1.5)))
    fig.add_trace(go.Scatter(x=bx, y=by, mode="lines",
                             line=dict(color=RED, width=1.5)))
    fig.add_hline(y=base, line_color="#313a4d", line_width=0.5, line_dash="dot")
    fig.update_layout(
        template="plotly_dark", height=height, showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_gauge(score: float, title: str, subtitle: str = "",
                 bands: str = "redgreen", height: int = 260) -> go.Figure:
    """0-100 gauge with needle. bands='redgreen' (low bad) or 'risk'
    (low conservative -> high very aggressive)."""
    if bands == "risk":
        steps = [
            dict(range=[0, 25], color="#bbf7d0"),
            dict(range=[25, 50], color="#fde68a"),
            dict(range=[50, 75], color="#fdba74"),
            dict(range=[75, 100], color="#fecaca"),
        ]
    else:
        steps = [
            dict(range=[0, 33], color="#fecaca"),
            dict(range=[33, 66], color="#fde68a"),
            dict(range=[66, 100], color="#bbf7d0"),
        ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score),
        title=dict(text=title, font=dict(size=15)),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1),
            bar=dict(color="#dee3ea", thickness=0.25),
            steps=steps,
            threshold=dict(line=dict(color="#dee3ea", width=3),
                           thickness=0.85, value=score),
        ),
        number=dict(font=dict(size=34)),
    ))
    if subtitle:
        fig.add_annotation(x=0.5, y=-0.08, text=subtitle, showarrow=False,
                           font=dict(size=11, color="#8a93a6"),
                           xref="paper", yref="paper")
    fig.update_layout(template="plotly_dark", height=height,
                      margin=dict(l=25, r=25, t=45, b=25),
                      paper_bgcolor="rgba(0,0,0,0)")
    return fig
