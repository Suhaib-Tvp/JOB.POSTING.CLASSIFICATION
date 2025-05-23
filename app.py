# app.py

from flask import Flask, jsonify, request
from scraper import run_pipeline, classify_new_job

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape_jobs():
    keyword = request.args.get('keyword', 'data science')
    pages = int(request.args.get('pages', 2))
    clusters = int(request.args.get('clusters', 8))
    jobs = run_pipeline(keyword, pages, clusters)
    return jsonify(jobs)

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    skills = data.get("skills", "")
    if not skills:
        return jsonify({"error": "No skills provided"}), 400
    cluster = classify_new_job(skills)
    return jsonify({"cluster": int(cluster)})

if __name__ == "__main__":
    app.run(debug=True)
