# scraper.py

import requests
from bs4 import BeautifulSoup
import re
import json
import spacy
import joblib
import time
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

nlp = spacy.load("en_core_web_sm")

def scrape_karkidi_jobs(keyword="data science", pages=2):
    headers = {'User-Agent': 'Mozilla/5.0'}
    base_url = "https://www.karkidi.com/Find-Jobs/{page}/all/India?search={query}"
    jobs_list = []
    seen = set()
    for page in range(1, pages + 1):
        url = base_url.format(page=page, query=keyword.replace(' ', '%20'))
        print(f"Scraping page: {page}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        job_blocks = soup.find_all("div", class_="ads-details")
        for job in job_blocks:
            try:
                title = job.find("h4").get_text(strip=True)
                company = job.find("a", href=lambda x: x and "Employer-Profile" in x).get_text(strip=True)
                location = job.find("p").get_text(strip=True)
                experience = job.find("p", class_="emp-exp").get_text(strip=True)
                key_skills_tag = job.find("span", string="Key Skills")
                skills = key_skills_tag.find_next("p").get_text(strip=True) if key_skills_tag else ""
                summary_tag = job.find("span", string="Summary")
                summary = summary_tag.find_next("p").get_text(strip=True) if summary_tag else ""
                
                job_id = (title, company, location)
                if job_id in seen:
                    continue
                seen.add(job_id)
                
                jobs_list.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "experience": experience,
                    "summary": summary,
                    "skills": skills,
                    "date_posted": datetime.now().strftime("%Y-%m-%d")
                })
            except Exception as e:
                print(f"Error parsing job block: {e}")
                continue
        time.sleep(1)
    return jobs_list

def preprocess_skills(skills):
    if isinstance(skills, str):
        skills = [s.strip() for s in re.split(r'[;,]', skills) if s.strip()]
    doc = nlp(" ".join(skills))
    return [token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop]

def vectorize_jobs(job_data):
    cleaned = [" ".join(preprocess_skills(job['skills'])) for job in job_data]
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(cleaned)
    return X, vectorizer

def cluster_jobs(X, n_clusters=8):
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X)
    return model, labels

def save_model(vectorizer, model):
    joblib.dump(vectorizer, 'vectorizer.pkl')
    joblib.dump(model, 'model.pkl')

def load_model():
    return joblib.load('vectorizer.pkl'), joblib.load('model.pkl')

def classify_new_job(job_skills):
    vectorizer, model = load_model()
    X_new = vectorizer.transform([" ".join(preprocess_skills(job_skills))])
    return model.predict(X_new)[0]

def run_pipeline(keyword="data science", pages=2, n_clusters=8):
    jobs = scrape_karkidi_jobs(keyword=keyword, pages=pages)
    if not jobs:
        print("No jobs scraped.")
        return []
    X, vectorizer = vectorize_jobs(jobs)
    model, labels = cluster_jobs(X, n_clusters=n_clusters)
    for job, label in zip(jobs, labels):
        job["cluster"] = int(label)
    save_model(vectorizer, model)
    with open("clustered_jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)
    print(f"Processed {len(jobs)} jobs and saved clustered_jobs.json")
    return jobs
