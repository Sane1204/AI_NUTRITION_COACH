import streamlit as st
 
from app import (
    input_image_process,
    generate_model_response,
    parse_food_json,
    calculate_remaining_target,
    nutrition_calculator,
    recomended_food,
)
 

 
st.set_page_config(
    page_title="Nutrition Coach",
    page_icon="🥗",
    layout="wide",
)

 
st.markdown("""
<style>
/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
 
/* ── page max-width ── */
.block-container { max-width: 860px; padding-top: 2rem; }
 
/* ── page header ── */
.nc-header h1 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.15rem;
}
.nc-header p {
    color: #888;
    font-size: 0.875rem;
    margin-top: 0;
}
 
/* ── target input cards ── */
.target-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 1.25rem;
}
.target-card {
    background: white;
    border: 0.5px solid #e0e0e0;
    border-radius: 10px;
    padding: 12px 16px;
}
.target-card label {
    display: block;
    font-size: 11px;
    color: #999;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.target-card .val {
    font-size: 1.6rem;
    font-weight: 600;
    color: #111;
    line-height: 1.1;
}
.target-card .unit {
    font-size: 11px;
    color: #bbb;
    margin-top: 2px;
}
 
/* ── diet pills ── */
.diet-pills { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 1.25rem; }
.pill {
    padding: 6px 18px;
    border-radius: 100px;
    border: 0.5px solid #ddd;
    font-size: 0.8rem;
    cursor: pointer;
    display: inline-block;
}
.pill.active {
    background: #f0f0f0;
    border-color: #999;
    font-weight: 600;
}
 
/* ── progress bars ── */
.prog-wrap { margin-bottom: 14px; }
.prog-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #888;
    margin-bottom: 5px;
}
.prog-row strong { color: #111; }
.track {
    height: 6px;
    background: #eee;
    border-radius: 100px;
    overflow: hidden;
}
.fill { height: 100%; border-radius: 100px; }
 
/* ── metric cards (this meal) ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: #f7f7f7;
    border-radius: 8px;
    padding: 14px 16px;
}
.metric-card .m-label { font-size: 11px; color: #aaa; margin-bottom: 4px; }
.metric-card .m-val {
    font-size: 1.6rem;
    font-weight: 600;
    color: #111;
    line-height: 1.1;
}
.metric-card .m-unit { font-size: 11px; color: #bbb; }
 
/* ── detected food rows ── */
.food-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.food-table tr { border-bottom: 0.5px solid #f0f0f0; }
.food-table tr:last-child { border-bottom: none; }
.food-table td { padding: 9px 6px; color: #333; }
.food-table td:first-child { color: #555; }
.food-table td:last-child { text-align: right; }
.dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: middle;
}
.conf-badge {
    font-size: 11px;
    padding: 2px 9px;
    border-radius: 100px;
    font-weight: 500;
}
.conf-high { background: #eafbe7; color: #2a7a2a; }
.conf-med  { background: #fff7e0; color: #8a6a00; }
.conf-low  { background: #fdeaea; color: #9a2a2a; }
 
/* ── recommendation cards ── */
.rec-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 1.5rem;
}
.rec-card {
    background: white;
    border: 0.5px solid #e8e8e8;
    border-radius: 12px;
    padding: 14px 16px;
}
.rec-name { font-size: 0.95rem; font-weight: 600; color: #111; margin-bottom: 2px; }
.rec-serving { font-size: 11px; color: #aaa; margin-bottom: 8px; }
.rec-macros { display: flex; gap: 10px; font-size: 0.75rem; color: #777; flex-wrap: wrap; margin-bottom: 8px; }
.rec-macros strong { color: #333; }
.rec-reason {
    font-size: 0.75rem;
    color: #888;
    border-top: 0.5px solid #f0f0f0;
    padding-top: 8px;
}
 
/* ── disclaimer ── */
.disclaimer {
    background: #f9f9f9;
    border: 0.5px solid #eee;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.78rem;
    color: #999;
    line-height: 1.6;
    margin-top: 0.5rem;
}
 
/* ── section label ── */
.sec-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #aaa;
    margin-bottom: 10px;
}
 
/* ── Streamlit widget overrides ── */
div[data-testid="stFileUploader"] > div { border-radius: 12px !important; }
div[data-testid="stTabs"] button { font-size: 0.875rem !important; }
</style>
""", unsafe_allow_html=True)
 

 
ASSISTANT_PROMPT = """
You are a food image recognition assistant.
Your job:
- Identify visible food items in the image.
- Estimate the portion size in grams for each food item.
- Return ONLY valid JSON. No markdown, no explanations outside JSON.
 
Return format:
[
  {"food_name": "rice", "estimated_grams": 150, "confidence": "medium"},
  {"food_name": "paneer", "estimated_grams": 100, "confidence": "medium"}
]
 
Rules:
- Simple food names only.
- If unsure, still estimate but set confidence to "low".
- Do not calculate calories. Only identify food and estimate grams.
"""
 
st.markdown("""
<div class="nc-header">
  <h1>🥗 Nutrition Coach</h1>
  <p>Snap a meal · get instant macro breakdown · personalised food recommendations</p>
</div>
""", unsafe_allow_html=True)
 
st.divider()
 

left_col, right_col = st.columns([1, 1.6], gap="large")
 
with left_col:
    st.markdown('<div class="sec-label">Meal photo</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload food image",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        uploaded_file.seek(0)
        st.image(uploaded_file, width='stretch')
        uploaded_file.seek(0)
 
with right_col:
    st.markdown('<div class="sec-label">Daily macro targets</div>', unsafe_allow_html=True)
 
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        target_calories = st.number_input("Calories", min_value=0, value=1900, step=50, label_visibility="visible")
    with c2:
        target_protein = st.number_input("Protein (g)", min_value=0, value=130, step=5, label_visibility="visible")
    with c3:
        target_carbs = st.number_input("Carbs (g)", min_value=0, value=200, step=5, label_visibility="visible")
    with c4:
        target_fat = st.number_input("Fat (g)", min_value=0, value=55, step=5, label_visibility="visible")
 
    st.markdown('<div class="sec-label" style="margin-top:1rem;">Diet preference</div>', unsafe_allow_html=True)
    diet_type = st.radio(
        "Diet",
        options=["any", "vegetarian", "vegetarian_no_egg"],
        format_func=lambda x: {"any": "Any", "vegetarian": "Vegetarian", "vegetarian_no_egg": "Vegetarian (no egg)"}[x],
        horizontal=True,
        label_visibility="collapsed",
    )
 
    st.markdown("<br>", unsafe_allow_html=True)
    analyse_btn = st.button("✦ Analyse meal", type="primary", width='stretch')
 

if analyse_btn:
    if uploaded_file is None:
        st.error("Please upload a food image first.")
        st.stop()
 
    with st.spinner("Identifying foods and calculating macros…"):
        try:
            uploaded_file.seek(0)
            encoded_image = input_image_process(uploaded_file)
            uploaded_file.seek(0)
 
            raw_output = generate_model_response(
                encoded_image,
                "Identify the food items in this image and estimate portion sizes in grams.",
                ASSISTANT_PROMPT,
            )
 
            detected = parse_food_json(raw_output)
 
            if not detected:
                st.error("Could not parse food items from the image response.")
                with st.expander("Raw model output"):
                    st.code(raw_output)
                st.stop()
 
            nutrition_result = nutrition_calculator(detected)
            targets = {"calories": target_calories, "protein": target_protein,
                       "carbs": target_carbs, "fat": target_fat}
            remaining = calculate_remaining_target(nutrition_result["totals"], targets)
            recommendations = recomended_food(remaining, diet_type)
 
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()
 
    # Store in session state so results persist
    st.session_state["nutrition_result"] = nutrition_result
    st.session_state["remaining"] = remaining
    st.session_state["recommendations"] = recommendations
    st.session_state["raw_output"] = raw_output
 

 
if "nutrition_result" in st.session_state:
    nutrition_result = st.session_state["nutrition_result"]
    remaining       = st.session_state["remaining"]
    recommendations = st.session_state["recommendations"]
    raw_output      = st.session_state["raw_output"]
    totals          = nutrition_result["totals"]
 
    st.divider()
 
    tab_foods, tab_macros, tab_recs = st.tabs(["🔍 Detected foods", "📊 Macro breakdown", "✨ Recommendations"])
 
 
    with tab_foods:
        items = nutrition_result.get("items", [])
 
        if items:
            dot_colors = ["#639922", "#D85A30", "#378ADD", "#BA7517", "#7F77DD", "#1D9E75"]
            rows_html = ""
            for i, item in enumerate(items):
                color = dot_colors[i % len(dot_colors)]
                name  = item.get("food_name", item.get("name", "Unknown"))
                grams = item.get("estimated_grams", item.get("grams", "—"))
                conf  = item.get("confidence", "medium").lower()
                conf_class = {"high": "conf-high", "medium": "conf-med", "low": "conf-low"}.get(conf, "conf-med")
                rows_html += f"""
                <tr>
                  <td><span class="dot" style="background:{color}"></span>{name}</td>
                  <td>{grams}g</td>
                  <td><span class="conf-badge {conf_class}">{conf}</span></td>
                </tr>"""
 
            st.markdown(f"""
            <table class="food-table">
              <thead>
                <tr>
                  <td style="color:#aaa;font-size:11px;padding-bottom:6px;">Food item</td>
                  <td style="color:#aaa;font-size:11px;padding-bottom:6px;">Portion</td>
                  <td style="color:#aaa;font-size:11px;padding-bottom:6px;text-align:right;">Confidence</td>
                </tr>
              </thead>
              <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("No foods matched the local dataset.")
 
        if nutrition_result.get("unknown_items"):
            with st.expander(f"⚠ {len(nutrition_result['unknown_items'])} items not found in dataset"):
                st.dataframe(nutrition_result["unknown_items"], width='stretch')
 
        with st.expander("Raw model output"):
            st.code(raw_output)
 
    
    with tab_macros:
        st.markdown('<div class="sec-label">This meal</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card">
            <div class="m-label">Calories</div>
            <div class="m-val">{totals['calories']}</div>
            <div class="m-unit">kcal</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Protein</div>
            <div class="m-val">{totals['protein']}</div>
            <div class="m-unit">g</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Carbs</div>
            <div class="m-val">{totals['carbs']}</div>
            <div class="m-unit">g</div>
          </div>
          <div class="metric-card">
            <div class="m-label">Fat</div>
            <div class="m-val">{totals['fat']}</div>
            <div class="m-unit">g</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
 
        st.markdown('<div class="sec-label" style="margin-top:1.25rem;">Remaining daily targets</div>', unsafe_allow_html=True)
 
        def progress_bar(label, consumed, target, color):
            pct = min(int((consumed / target) * 100), 100) if target > 0 else 0
            left = max(target - consumed, 0)
            return f"""
            <div class="prog-wrap">
              <div class="prog-row">
                <span>{label}</span>
                <span><strong>{left}</strong> / {target} left</span>
              </div>
              <div class="track"><div class="fill" style="width:{pct}%;background:{color};"></div></div>
            </div>"""
 
        cal_consumed  = target_calories - remaining["calories"]
        prot_consumed = target_protein  - remaining["protein"]
        carb_consumed = target_carbs    - remaining["carbs"]
        fat_consumed  = target_fat      - remaining["fat"]
 
        st.markdown(
            progress_bar("Calories", cal_consumed,  target_calories, "#639922") +
            progress_bar("Protein",  prot_consumed, target_protein,  "#378ADD") +
            progress_bar("Carbs",    carb_consumed, target_carbs,    "#BA7517") +
            progress_bar("Fat",      fat_consumed,  target_fat,      "#D85A30"),
            unsafe_allow_html=True,
        )
 
    
    with tab_recs:
        if recommendations:
            # Render 2-column card grid in pairs
            for i in range(0, len(recommendations), 2):
                pair = recommendations[i:i+2]
                cards_html = ""
                for food in pair:
                    cards_html += f"""
                    <div class="rec-card">
                      <div class="rec-name">{food['name']}</div>
                      <div class="rec-serving">{food['serving']}</div>
                      <div class="rec-macros">
                        <span><strong>{food['calories']}</strong> kcal</span>
                        <span><strong>{food['protein']}g</strong> protein</span>
                        <span><strong>{food['carbs']}g</strong> carbs</span>
                        <span><strong>{food['fat']}g</strong> fat</span>
                      </div>
                      <div class="rec-reason">{food['reason']}</div>
                    </div>"""
                st.markdown(f'<div class="rec-grid">{cards_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No recommendations found. Try adjusting your macro targets.")
 
    
    st.markdown("""
    <div class="disclaimer">
      ℹ Nutritional values are estimates based on general food data. Actual amounts vary by preparation,
      portion size, and ingredients. For precise dietary guidance consult a qualified nutritionist or
      healthcare provider.
    </div>
    """, unsafe_allow_html=True)