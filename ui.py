"""Premium visual system for the Streamlit product layer."""

from __future__ import annotations

import html

import altair as alt
import streamlit as st

TERRACOTTA = "#C75236"
CHARCOAL = "#29251F"
MUTED = "#756B60"


def inject_global_styles() -> None:
    """Apply the requested warm editorial identity without changing behavior."""

    st.html(
        """
        <style>
        :root { --ivory:#f7f1e7; --paper:#fffaf3; --sand:#efe3d2; --terracotta:#c75236; --crimson:#8f2d22; --charcoal:#29251f; --muted:#756b60; --line:rgba(91,68,48,.15); }
        html { scroll-behavior:smooth; }
        body, [data-testid="stAppViewContainer"] { color:var(--charcoal); background:radial-gradient(circle at 92% 4%,rgba(236,169,141,.20),transparent 24rem),radial-gradient(circle at 4% 52%,rgba(216,185,142,.17),transparent 30rem),linear-gradient(180deg,#fbf7f0 0%,var(--ivory) 48%,#f4ebdf 100%); }
        [data-testid="stAppViewContainer"]::before { content:"";position:fixed;inset:0;pointer-events:none;opacity:.16;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.13'/%3E%3C/svg%3E"); }
        [data-testid="stHeader"] { background:rgba(251,247,240,.76);backdrop-filter:blur(16px);border-bottom:1px solid var(--line); }
        [data-testid="stMainBlockContainer"] { max-width:1280px;padding-top:2.2rem;padding-bottom:5rem; }
        [data-testid="stSidebar"] { box-shadow:18px 0 50px rgba(66,46,30,.06); }
        h1,h2,h3 { color:var(--charcoal);letter-spacing:-.035em;font-family:Manrope,Inter,ui-sans-serif,system-ui,sans-serif; }
        h1 { font-size:clamp(2.2rem,5vw,4.6rem);line-height:.98;font-weight:650; } h2 { font-weight:620; } p,label,[data-testid="stCaptionContainer"] { line-height:1.65; }
        [data-testid="stMetric"] { background:rgba(255,250,243,.72);border:1px solid var(--line)!important;box-shadow:0 12px 35px rgba(72,48,30,.055);min-width:168px;transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }
        [data-testid="stMetric"]:hover { transform:translateY(-3px);border-color:rgba(199,82,54,.36)!important;box-shadow:0 18px 40px rgba(72,48,30,.09); }
        [data-testid="stMetricValue"] { color:var(--crimson);letter-spacing:-.045em; }
        [data-testid="stVerticalBlockBorderWrapper"] { background:rgba(255,250,243,.64);border-color:var(--line)!important;box-shadow:0 14px 45px rgba(69,45,27,.045);backdrop-filter:blur(8px); }
        .stButton button,.stDownloadButton button,[data-testid="stPageLink"] a { transition:transform .18s ease,box-shadow .18s ease,background .18s ease;font-weight:650;letter-spacing:-.01em; }
        .stButton button:hover,.stDownloadButton button:hover,[data-testid="stPageLink"] a:hover { transform:translateY(-2px);box-shadow:0 10px 24px rgba(143,45,34,.16); }
        button:focus-visible,a:focus-visible,input:focus-visible { outline:3px solid rgba(199,82,54,.35)!important;outline-offset:3px; }
        [data-testid="stFileUploaderDropzone"] { background:rgba(239,227,210,.48);border:1.5px dashed rgba(169,66,43,.38);min-height:150px;transition:background .2s ease,border-color .2s ease; }
        [data-testid="stFileUploaderDropzone"]:hover { background:rgba(236,169,141,.13);border-color:var(--terracotta); }
        [data-testid="stFileUploaderDropzone"] button { background:#8f2d22!important;color:#fff!important;border:1px solid #8f2d22!important;box-shadow:0 5px 14px rgba(143,45,34,.18); }
        [data-testid="stFileUploaderDropzone"] button:hover { background:#76231b!important;color:#fff!important;border-color:#76231b!important; }
        [data-testid="stFileUploaderDropzone"] button * { color:#fff!important;fill:#fff!important; }
        [data-testid="stFileUploaderDropzone"] small { color:#5f554b!important;opacity:1!important; }
        [data-testid="stDataFrame"] { border-radius:14px;overflow:hidden;border:1px solid var(--line); }
        .editorial-kicker { color:var(--terracotta);font-size:.72rem;font-weight:750;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.55rem; }
        .editorial-intro { max-width:790px;margin:.1rem 0 2rem;animation:rise-in .55s both ease-out; }
        .editorial-intro h1 { font-size:clamp(2.25rem,4.6vw,4.1rem);margin:0 0 .8rem; }
        .editorial-intro p { color:var(--muted);font-size:1.06rem;max-width:680px; }
        .hero-copy h1 { font-size:clamp(3rem,6.4vw,6.2rem);line-height:.91;margin:.4rem 0 1.2rem;max-width:780px; }
        .hero-copy h1 em { color:var(--terracotta);font-style:normal; }
        .hero-copy p { color:var(--muted);font-size:1.12rem;max-width:610px; }
        .hero-proof { display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1.6rem; }
        .hero-proof span { padding:.42rem .7rem;border:1px solid var(--line);border-radius:999px;font-size:.76rem;color:#66594d;background:rgba(255,250,243,.65); }
        .sentinel-visual { position:relative;min-height:430px;display:grid;place-items:center;isolation:isolate; }
        .sentinel-orbit { position:absolute;width:360px;height:360px;border:1px solid rgba(169,66,43,.18);border-radius:50%;animation:breathe 6s ease-in-out infinite; }
        .sentinel-orbit::after { content:"";position:absolute;width:10px;height:10px;background:var(--terracotta);border-radius:50%;top:38px;left:55px;box-shadow:0 0 0 8px rgba(199,82,54,.10);animation:orbit 12s linear infinite;transform-origin:125px 142px; }
        .signal-card { position:absolute;width:190px;padding:1rem 1.05rem;border-radius:16px;background:rgba(255,250,243,.9);border:1px solid var(--line);box-shadow:0 20px 55px rgba(74,48,28,.12);animation:float 5.4s ease-in-out infinite; }
        .signal-card small { display:block;color:var(--muted);font-size:.65rem;letter-spacing:.11em;text-transform:uppercase; }.signal-card strong { display:block;font-size:1.45rem;margin-top:.25rem;color:var(--charcoal); }.signal-card b { color:var(--terracotta);font-size:.75rem;font-weight:650; }
        .signal-a { top:34px;right:4px; }.signal-b { left:0;top:170px;animation-delay:-1.7s; }.signal-c { bottom:25px;right:25px;animation-delay:-3.1s;border-left:3px solid var(--terracotta); }
        .core-mark { width:138px;height:138px;border-radius:38% 62% 58% 42%;display:grid;place-items:center;background:linear-gradient(145deg,#c75236,#96351f);color:white;box-shadow:0 30px 70px rgba(143,45,34,.25);animation:morph 8s ease-in-out infinite; }.core-mark span { font-size:2.7rem;font-weight:280; }
        .workflow-strip { display:grid;grid-template-columns:repeat(5,1fr);gap:.8rem;align-items:center;margin:2.5rem 0 3.5rem; }
        .workflow-stage { position:relative;padding:1rem .6rem;border-top:1px solid var(--line);animation:rise-in .6s both ease-out; }.workflow-stage::after { content:"";position:absolute;top:-3px;left:0;height:5px;width:5px;background:var(--terracotta);border-radius:50%;animation:pulse 2.8s infinite; }.workflow-stage small { color:var(--terracotta);font-weight:750;letter-spacing:.12em; }.workflow-stage strong { display:block;margin-top:.45rem; }.workflow-stage p { color:var(--muted);font-size:.78rem;margin:.25rem 0 0;line-height:1.35; }
        @keyframes rise-in { from { opacity:0;transform:translateY(14px); } to { opacity:1;transform:none; } } @keyframes float { 0%,100% { transform:translateY(0) rotate(-.5deg); } 50% { transform:translateY(-11px) rotate(.7deg); } } @keyframes breathe { 0%,100% { transform:scale(.96);opacity:.65; } 50% { transform:scale(1.03);opacity:1; } } @keyframes morph { 0%,100% { border-radius:38% 62% 58% 42%; } 50% { border-radius:59% 41% 38% 62%; } } @keyframes orbit { to { transform:rotate(360deg); } } @keyframes pulse { 0%,100% { box-shadow:0 0 0 0 rgba(199,82,54,.25); } 50% { box-shadow:0 0 0 8px transparent; } }
        @media (max-width:760px) { [data-testid="stMainBlockContainer"] { padding-top:1.4rem; }.hero-copy h1 { font-size:clamp(2.65rem,14vw,4.2rem); }.sentinel-visual { min-height:350px;transform:scale(.86);margin:-1rem; }.workflow-strip { grid-template-columns:1fr;gap:.15rem; }.workflow-stage { padding-left:1rem;border-top:0;border-left:1px solid var(--line); }.workflow-stage::after { top:1.35rem;left:-3px; } }
        @media (prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } *,*::before,*::after { animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important; } }
        </style>
        """
    )


def render_page_intro(kicker: str, title: str, description: str) -> None:
    st.html(f'<section class="editorial-intro"><div class="editorial-kicker">{html.escape(kicker)}</div><h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></section>')


def render_hero() -> None:
    """Render a product-specific hero with a native navigation CTA."""

    left, right = st.columns([1.25, .85], vertical_alignment="center")
    with left:
        st.html("""<section class="hero-copy" aria-labelledby="sentinel-hero-title"><div class="editorial-kicker">Predict earlier · act smarter</div><h1 id="sentinel-hero-title">See stockouts <em>before</em> shelves go quiet.</h1><p>SupplyChain Sentinel turns live inventory, demand momentum and supplier lead times into clear seven-day risk signals—and tells your team exactly what to do next.</p><div class="hero-proof" aria-label="Product capabilities"><span>7-day early warning</span><span>Transparent risk scoring</span><span>Action-ready decisions</span></div></section>""")
        st.page_link("app_pages/data_workspace.py", label="Analyze your inventory", icon=":material/arrow_forward:")
    with right:
        st.html("""<div class="sentinel-visual" role="img" aria-label="Inventory signals flowing into a stockout risk decision"><div class="sentinel-orbit"></div><div class="core-mark"><span>82</span></div><div class="signal-card signal-a"><small>Demand velocity</small><strong>+28%</strong><b>Promotion lift detected</b></div><div class="signal-card signal-b"><small>Inventory cover</small><strong>4.2 days</strong><b>Below supplier lead time</b></div><div class="signal-card signal-c"><small>Recommended action</small><strong>Expedite</strong><b>Replenish 640 units</b></div></div>""")


def render_workflow() -> None:
    labels = [("01 · INPUT","Inventory","Upload operational history"),("02 · PROCESS","Clean","Validate and engineer signals"),("03 · INTELLIGENCE","Predict","Estimate seven-day risk"),("04 · RESULT","Prioritize","Score every product 0–100"),("05 · ACTION","Respond","Expedite, transfer or monitor")]
    cards = "".join(f'<div class="workflow-stage" style="animation-delay:{index * .08}s"><small>{small}</small><strong>{title}</strong><p>{copy}</p></div>' for index, (small, title, copy) in enumerate(labels))
    st.html(f'<section class="workflow-strip" aria-label="How SupplyChain Sentinel works">{cards}</section>')


def style_chart(chart: alt.Chart) -> alt.Chart:
    return chart.configure_view(strokeOpacity=0).configure_axis(gridColor="#E7D9C8",domainColor="#CDBAA5",labelColor=MUTED,titleColor=CHARCOAL).configure_legend(labelColor=MUTED,titleColor=CHARCOAL)
