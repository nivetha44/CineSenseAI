"""
Merge all 6 pipeline notebooks into a single master Jupyter notebook: Nivetha_CineSenseAI.ipynb
"""

import json
import os
import shutil

NOTEBOOK_DIR = "notebooks"
NOTEBOOKS = [
    "01_data_understanding.ipynb",
    "02_data_cleaning.ipynb",
    "03_eda.ipynb",
    "04_feature_engineering.ipynb",
    "05_recommendation_model.ipynb",
    "06_model_evaluation.ipynb"
]

def merge_notebooks():
    merged_cells = []
    
    # Title cell
    title_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# CineSenseAI — Complete Machine Learning & Recommendation Pipeline\n",
            "\n",
            "**Author:** Nivetha  \n",
            "**Repository:** [https://github.com/nivetha44/CineSenseAI](https://github.com/nivetha44/CineSenseAI)  \n",
            "**Live Application:** [https://cinesense-ai.onrender.com](https://cinesense-ai.onrender.com)  \n",
            "\n",
            "---\n",
            "\n",
            "This master notebook integrates the complete end-to-end data-to-product pipeline:\n",
            "1. **Data Understanding & Ingestion** (MovieLens 100k)\n",
            "2. **Data Cleaning & Normalization**\n",
            "3. **Exploratory Data Analysis (EDA)**\n",
            "4. **Feature Engineering & TF-IDF Soup Construction**\n",
            "5. **Hybrid Recommendation Engine (Content + Bayesian Prior + Collaborative Correlation)**\n",
            "6. **Quantitative Offline Model Evaluation (Precision@K, Recall@K, Hit Rate@K, Catalog Coverage)**\n"
        ]
    }
    merged_cells.append(title_cell)

    for idx, nb_file in enumerate(NOTEBOOKS, 1):
        nb_path = os.path.join(NOTEBOOK_DIR, nb_file)
        with open(nb_path, "r", encoding="utf-8") as f:
            nb_data = json.load(f)
            cells = nb_data.get("cells", [])

            # Add divider
            divider_cell = {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "\n",
                    "---\n",
                    f"## Phase {idx}: {nb_file.replace('.ipynb', '').replace('_', ' ').title()}\n",
                    "---\n"
                ]
            }
            merged_cells.append(divider_cell)
            merged_cells.extend(cells)

    master_notebook = {
        "cells": merged_cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    out_path = "Nivetha_CineSenseAI.ipynb"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(master_notebook, f, indent=2)
    print(f"Created {out_path} with {len(merged_cells)} cells.")

    # Also copy to Nivetha_CineSense.ipynb
    shutil.copyfile(out_path, "Nivetha_CineSense.ipynb")
    print("Created copy Nivetha_CineSense.ipynb")

if __name__ == "__main__":
    merge_notebooks()
