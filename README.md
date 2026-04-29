# 📊 Wikipedia Edit Pattern Analysis

> Analysing contributor activity and collaboration patterns on Wikipedia articles using the Wikipedia API, Python, and network science.

**Author:** Amir Nazhan | [@Miaoricle](https://github.com/Miaoricle)  
**University:** Universiti Kuala Lumpur MIIT — Bachelor in Software Engineering  

---

## 🔍 What This Project Does

This tool fetches the **edit history** of any Wikipedia article and produces:

| Output | Description |
|--------|-------------|
| 🏆 Top Contributors Chart | Bar chart of the most active editors |
| 📅 Edit Timeline | Monthly edit activity over time |
| 🕸️ Collaboration Network | Graph of editors who co-edited in the same month |
| 🥧 Editor Types Pie | Split between registered users and anonymous (IP) editors |

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-FF6600?style=for-the-badge&logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=python&logoColor=white)

---

## 🚀 Getting Started

```bash
git clone https://github.com/Miaoricle/wikipedia-edit-analysis.git
cd wikipedia-edit-analysis
pip install -r requirements.txt
python wikipedia_analysis.py
```

Change the article on the last line of `wikipedia_analysis.py`:

```python
ARTICLE = "Machine learning"   # any Wikipedia page title
```

---

## 📁 Project Structure

```
wikipedia-edit-analysis/
├── wikipedia_analysis.py   # Main script
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

---

## 💡 Key Insights You Can Discover

- Which users dominate editing on a topic?
- Are edits clustered around specific time periods?
- How connected is the editing community?
- How much of the article is shaped by anonymous contributors?

---

## 📄 License

MIT License — free to use, modify, and share.
