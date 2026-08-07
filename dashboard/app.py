"""
Pyrenee Capital - Deal Pipeline Dashboard (Flask)
Runs on port 5000. Read-only view of the deal database.
"""

from flask import Flask, render_template, jsonify, request
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.pipeline import (
    get_pipeline_summary, get_top_targets, get_universe_stats,
    get_lp_pipeline, search_companies,
)
from analytics.pension_metrics import pension_dashboard_data

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    stats   = get_universe_stats()
    summary = get_pipeline_summary()
    targets = get_top_targets(20)
    lps     = get_lp_pipeline()
    return render_template("index.html",
                           stats=stats, summary=summary,
                           targets=targets, lps=lps)


@app.route("/api/stats")
def api_stats():
    return jsonify(get_universe_stats())


@app.route("/api/pipeline")
def api_pipeline():
    return jsonify(get_top_targets(50))


@app.route("/api/lps")
def api_lps():
    return jsonify(get_lp_pipeline())


@app.route("/pension")
def pension():
    data = pension_dashboard_data()
    return render_template("pension.html", d=data, data_json=json.dumps(data, ensure_ascii=False))


@app.route("/api/pension")
def api_pension():
    return jsonify(pension_dashboard_data())


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "")
    if not q:
        return jsonify([])
    return jsonify(search_companies(q))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
