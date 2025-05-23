import requests
from bs4 import BeautifulSoup
import spacy
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from datetime import datetime

import en_core_web_sm
nlp = en_core_web_sm.load()

def scrape_karkidi_jobs(keyword="data science", pages=2):
    pass

def preprocess_skills(skills):
    pass

def vectorize_jobs(job_data):
    pass

def cluster_jobs(X, n_clusters=8):
    pass

def save_model(vectorizer, model):
    pass

def load_model():
    pass

def classify_new_job(job_skills):
    pass

def run_pipeline(keyword="data science", pages=2, n_clusters=8):
    pass
