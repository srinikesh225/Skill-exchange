"""Skill taxonomy seed.

Each entry carries both persisted fields (name, category, aliases, related) and
*generator* attributes used to synthesise an internally-consistent demo dataset:

  base_popularity : 0-1  overall prevalence of the skill in the market
  industries      : list of industries that request the skill
  trend           : monthly multiplicative demand factor over the 12-month window
                    (>1 growing, 1.0 stable, <1 declining) — drives real growth rates
  supply_maturity : 0-1  how established local training for the skill is
                    (new skills are low -> the gap engine finds real shortages)

Skill names are real technology/skill names (not fabricated credibility). The
demand/supply numbers derived from them are clearly-labelled synthetic demo data.
"""

from __future__ import annotations

# Industry vocabulary reused by the district profiles.
INDUSTRIES = [
    "IT & Software",
    "Cloud & Data",
    "Cybersecurity",
    "Fintech & BFSI",
    "Manufacturing",
    "Automotive",
    "Healthcare & Pharma",
    "Retail & E-commerce",
    "Telecom",
    "Energy & Utilities",
    "Construction",
    "AgriTech",
    "Logistics",
]

SKILLS: list[dict] = [
    # --- Programming languages ---
    {"name": "Python", "category": "Programming", "aliases": ["python programming", "python developer", "python 3", "python scripting"], "related": ["Machine Learning", "Data Engineering"], "base_popularity": 0.95, "industries": ["IT & Software", "Cloud & Data", "Fintech & BFSI"], "trend": 1.012, "supply_maturity": 0.85},
    {"name": "Java", "category": "Programming", "aliases": ["java programming", "core java", "java developer", "j2ee"], "related": ["Spring Boot", "Microservices"], "base_popularity": 0.82, "industries": ["IT & Software", "Fintech & BFSI"], "trend": 1.002, "supply_maturity": 0.92},
    {"name": "JavaScript", "category": "Programming", "aliases": ["js", "es6", "javascript developer"], "related": ["React", "Node.js", "TypeScript"], "base_popularity": 0.8, "industries": ["IT & Software", "Retail & E-commerce"], "trend": 1.006, "supply_maturity": 0.8},
    {"name": "TypeScript", "category": "Programming", "aliases": ["ts", "typescript developer"], "related": ["React", "Node.js"], "base_popularity": 0.55, "industries": ["IT & Software", "Retail & E-commerce"], "trend": 1.02, "supply_maturity": 0.5},
    {"name": "C++", "category": "Programming", "aliases": ["cpp", "c plus plus"], "related": ["Embedded Systems"], "base_popularity": 0.45, "industries": ["Manufacturing", "Automotive", "IT & Software"], "trend": 0.997, "supply_maturity": 0.8},
    {"name": "SQL", "category": "Data", "aliases": ["sql queries", "structured query language", "pl/sql", "t-sql"], "related": ["Data Engineering", "Power BI"], "base_popularity": 0.88, "industries": ["IT & Software", "Cloud & Data", "Fintech & BFSI"], "trend": 1.004, "supply_maturity": 0.88},

    # --- Web / app ---
    {"name": "React", "category": "Web Development", "aliases": ["react.js", "reactjs", "react developer"], "related": ["JavaScript", "TypeScript", "Next.js"], "base_popularity": 0.62, "industries": ["IT & Software", "Retail & E-commerce"], "trend": 1.015, "supply_maturity": 0.6},
    {"name": "Node.js", "category": "Web Development", "aliases": ["nodejs", "node", "express.js"], "related": ["JavaScript", "APIs"], "base_popularity": 0.5, "industries": ["IT & Software", "Retail & E-commerce"], "trend": 1.01, "supply_maturity": 0.62},
    {"name": "Next.js", "category": "Web Development", "aliases": ["nextjs", "next js"], "related": ["React", "TypeScript"], "base_popularity": 0.28, "industries": ["IT & Software"], "trend": 1.028, "supply_maturity": 0.35},
    {"name": "APIs", "category": "Web Development", "aliases": ["rest api", "restful apis", "api development", "graphql"], "related": ["Microservices", "Node.js"], "base_popularity": 0.6, "industries": ["IT & Software", "Fintech & BFSI"], "trend": 1.01, "supply_maturity": 0.6},

    # --- Cloud & DevOps ---
    {"name": "AWS", "category": "Cloud", "aliases": ["amazon web services", "aws cloud", "aws ec2", "aws s3"], "related": ["Docker", "Kubernetes", "Cloud Security"], "base_popularity": 0.68, "industries": ["Cloud & Data", "IT & Software"], "trend": 1.022, "supply_maturity": 0.55},
    {"name": "Azure", "category": "Cloud", "aliases": ["microsoft azure", "azure cloud"], "related": ["Docker", "Kubernetes"], "base_popularity": 0.5, "industries": ["Cloud & Data", "IT & Software", "Fintech & BFSI"], "trend": 1.02, "supply_maturity": 0.5},
    {"name": "Docker", "category": "DevOps", "aliases": ["containers", "containerisation", "containerization"], "related": ["Kubernetes", "CI/CD"], "base_popularity": 0.52, "industries": ["Cloud & Data", "IT & Software"], "trend": 1.018, "supply_maturity": 0.5},
    {"name": "Kubernetes", "category": "DevOps", "aliases": ["k8s", "kube"], "related": ["Docker", "Cloud Security"], "base_popularity": 0.4, "industries": ["Cloud & Data", "IT & Software"], "trend": 1.03, "supply_maturity": 0.35},
    {"name": "CI/CD", "category": "DevOps", "aliases": ["continuous integration", "jenkins", "github actions", "devops pipelines"], "related": ["Docker", "Kubernetes"], "base_popularity": 0.42, "industries": ["IT & Software", "Cloud & Data"], "trend": 1.016, "supply_maturity": 0.45},

    # --- Data / AI ---
    {"name": "Machine Learning", "category": "Data & AI", "aliases": ["ml", "machine-learning", "predictive modelling", "predictive modeling"], "related": ["Python", "Deep Learning"], "base_popularity": 0.55, "industries": ["Cloud & Data", "IT & Software", "Healthcare & Pharma"], "trend": 1.03, "supply_maturity": 0.45},
    {"name": "Deep Learning", "category": "Data & AI", "aliases": ["neural networks", "dl", "cnn", "transformers"], "related": ["Machine Learning", "Generative AI"], "base_popularity": 0.3, "industries": ["Cloud & Data", "IT & Software"], "trend": 1.04, "supply_maturity": 0.3},
    {"name": "Generative AI", "category": "Data & AI", "aliases": ["genai", "gen ai", "llm", "llms", "large language models", "prompt engineering", "gpt"], "related": ["RAG", "Vector Databases", "Machine Learning"], "base_popularity": 0.22, "industries": ["IT & Software", "Cloud & Data", "Fintech & BFSI"], "trend": 1.075, "supply_maturity": 0.15},
    {"name": "RAG", "category": "Data & AI", "aliases": ["retrieval augmented generation", "retrieval-augmented generation"], "related": ["Generative AI", "Vector Databases"], "base_popularity": 0.12, "industries": ["IT & Software", "Cloud & Data"], "trend": 1.08, "supply_maturity": 0.1},
    {"name": "Vector Databases", "category": "Data & AI", "aliases": ["vector db", "pgvector", "pinecone", "embeddings database"], "related": ["RAG", "Generative AI"], "base_popularity": 0.1, "industries": ["Cloud & Data", "IT & Software"], "trend": 1.07, "supply_maturity": 0.1},
    {"name": "MLOps", "category": "Data & AI", "aliases": ["ml ops", "model deployment", "mlflow"], "related": ["Machine Learning", "CI/CD"], "base_popularity": 0.16, "industries": ["Cloud & Data", "IT & Software"], "trend": 1.05, "supply_maturity": 0.2},
    {"name": "Data Engineering", "category": "Data & AI", "aliases": ["data engineer", "etl", "data pipelines", "spark", "airflow"], "related": ["SQL", "Python", "AWS"], "base_popularity": 0.42, "industries": ["Cloud & Data", "Fintech & BFSI"], "trend": 1.035, "supply_maturity": 0.35},
    {"name": "Data Science", "category": "Data & AI", "aliases": ["data scientist", "statistical modelling", "analytics"], "related": ["Python", "Machine Learning", "SQL"], "base_popularity": 0.44, "industries": ["Cloud & Data", "Fintech & BFSI", "Healthcare & Pharma"], "trend": 1.02, "supply_maturity": 0.45},
    {"name": "Power BI", "category": "Data & AI", "aliases": ["powerbi", "business intelligence", "tableau", "data visualization"], "related": ["SQL", "Data Science"], "base_popularity": 0.4, "industries": ["Fintech & BFSI", "Retail & E-commerce", "IT & Software"], "trend": 1.01, "supply_maturity": 0.6},

    # --- Security ---
    {"name": "Cybersecurity", "category": "Security", "aliases": ["cyber security", "information security", "infosec", "soc analyst"], "related": ["Network Security", "Cloud Security"], "base_popularity": 0.38, "industries": ["Cybersecurity", "Fintech & BFSI", "IT & Software"], "trend": 1.045, "supply_maturity": 0.3},
    {"name": "Network Security", "category": "Security", "aliases": ["network defense", "firewall", "ids/ips"], "related": ["Cybersecurity"], "base_popularity": 0.24, "industries": ["Cybersecurity", "Telecom"], "trend": 1.025, "supply_maturity": 0.35},
    {"name": "Cloud Security", "category": "Security", "aliases": ["devsecops", "cloud sec", "cspm"], "related": ["AWS", "Cybersecurity", "Kubernetes"], "base_popularity": 0.16, "industries": ["Cybersecurity", "Cloud & Data", "Fintech & BFSI"], "trend": 1.06, "supply_maturity": 0.12},
    {"name": "Ethical Hacking", "category": "Security", "aliases": ["penetration testing", "pentesting", "vapt"], "related": ["Cybersecurity", "Network Security"], "base_popularity": 0.18, "industries": ["Cybersecurity"], "trend": 1.03, "supply_maturity": 0.3},

    # --- Hardware / embedded / manufacturing ---
    {"name": "IoT", "category": "Embedded & Hardware", "aliases": ["internet of things", "iot devices", "sensors"], "related": ["Embedded Systems", "Machine Learning"], "base_popularity": 0.24, "industries": ["Manufacturing", "Automotive", "Energy & Utilities", "AgriTech"], "trend": 1.025, "supply_maturity": 0.35},
    {"name": "Embedded Systems", "category": "Embedded & Hardware", "aliases": ["embedded c", "firmware", "microcontrollers", "rtos"], "related": ["C++", "IoT"], "base_popularity": 0.26, "industries": ["Manufacturing", "Automotive", "Telecom"], "trend": 1.008, "supply_maturity": 0.55},
    {"name": "PLC & SCADA", "category": "Embedded & Hardware", "aliases": ["plc programming", "scada", "industrial automation"], "related": ["Embedded Systems"], "base_popularity": 0.2, "industries": ["Manufacturing", "Energy & Utilities"], "trend": 1.006, "supply_maturity": 0.6},
    {"name": "CAD/CAM", "category": "Engineering", "aliases": ["autocad", "solidworks", "catia", "cad"], "related": ["CNC Machining"], "base_popularity": 0.28, "industries": ["Manufacturing", "Automotive", "Construction"], "trend": 1.0, "supply_maturity": 0.7},
    {"name": "CNC Machining", "category": "Engineering", "aliases": ["cnc operator", "cnc programming", "machining"], "related": ["CAD/CAM"], "base_popularity": 0.24, "industries": ["Manufacturing", "Automotive"], "trend": 0.998, "supply_maturity": 0.72},
    {"name": "Welding", "category": "Skilled Trades", "aliases": ["arc welding", "mig welding", "tig welding", "welder"], "related": ["CNC Machining"], "base_popularity": 0.3, "industries": ["Manufacturing", "Construction", "Automotive"], "trend": 0.996, "supply_maturity": 0.78},
    {"name": "Electrical Wiring", "category": "Skilled Trades", "aliases": ["electrician", "electrical maintenance", "wiring"], "related": ["Solar PV Installation"], "base_popularity": 0.34, "industries": ["Construction", "Energy & Utilities", "Manufacturing"], "trend": 1.0, "supply_maturity": 0.8},

    # --- Energy / green ---
    {"name": "Solar PV Installation", "category": "Green Skills", "aliases": ["solar panel installation", "rooftop solar", "solar technician"], "related": ["Electrical Wiring"], "base_popularity": 0.16, "industries": ["Energy & Utilities", "Construction"], "trend": 1.05, "supply_maturity": 0.3},
    {"name": "EV Servicing", "category": "Green Skills", "aliases": ["electric vehicle maintenance", "ev technician", "battery systems"], "related": ["Embedded Systems"], "base_popularity": 0.14, "industries": ["Automotive", "Energy & Utilities"], "trend": 1.06, "supply_maturity": 0.2},

    # --- Healthcare ---
    {"name": "Medical Coding", "category": "Healthcare", "aliases": ["icd coding", "clinical coding", "medical billing"], "related": [], "base_popularity": 0.2, "industries": ["Healthcare & Pharma"], "trend": 1.02, "supply_maturity": 0.5},
    {"name": "Phlebotomy", "category": "Healthcare", "aliases": ["blood collection", "lab technician"], "related": [], "base_popularity": 0.18, "industries": ["Healthcare & Pharma"], "trend": 1.01, "supply_maturity": 0.6},
    {"name": "Nursing Assistance", "category": "Healthcare", "aliases": ["gnm", "patient care", "healthcare assistant"], "related": [], "base_popularity": 0.26, "industries": ["Healthcare & Pharma"], "trend": 1.02, "supply_maturity": 0.65},

    # --- Business / services ---
    {"name": "Digital Marketing", "category": "Business", "aliases": ["seo", "sem", "social media marketing", "performance marketing"], "related": ["Data Science"], "base_popularity": 0.36, "industries": ["Retail & E-commerce", "IT & Software"], "trend": 1.015, "supply_maturity": 0.55},
    {"name": "Financial Analysis", "category": "Business", "aliases": ["financial modelling", "equity research", "fp&a"], "related": ["Power BI"], "base_popularity": 0.3, "industries": ["Fintech & BFSI"], "trend": 1.008, "supply_maturity": 0.6},
    {"name": "Accounting", "category": "Business", "aliases": ["tally", "gst", "bookkeeping", "accounts"], "related": ["Financial Analysis"], "base_popularity": 0.38, "industries": ["Fintech & BFSI", "Retail & E-commerce"], "trend": 0.999, "supply_maturity": 0.82},
    {"name": "Supply Chain Management", "category": "Business", "aliases": ["logistics management", "scm", "warehouse management"], "related": ["Data Science"], "base_popularity": 0.26, "industries": ["Logistics", "Retail & E-commerce", "Manufacturing"], "trend": 1.012, "supply_maturity": 0.55},

    # --- Legacy / declining (to demonstrate obsolescence detection) ---
    {"name": "Basic Office Tools", "category": "Foundational", "aliases": ["ms office", "ms word", "ms excel basics", "data entry"], "related": [], "base_popularity": 0.4, "industries": ["Retail & E-commerce", "IT & Software"], "trend": 0.985, "supply_maturity": 0.95},
    {"name": "Basic Web Design", "category": "Foundational", "aliases": ["html", "css", "static websites", "basic javascript"], "related": ["JavaScript"], "base_popularity": 0.3, "industries": ["IT & Software"], "trend": 0.975, "supply_maturity": 0.9},
    {"name": "Manual Testing", "category": "Foundational", "aliases": ["qa manual", "test cases", "black box testing"], "related": ["CI/CD"], "base_popularity": 0.28, "industries": ["IT & Software"], "trend": 0.98, "supply_maturity": 0.85},
]


def skill_names() -> list[str]:
    return [s["name"] for s in SKILLS]
