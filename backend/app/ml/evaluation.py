"""
CineSenseAI Model Evaluation Protocol
Evaluates Popularity Baseline, Content-Based, and Hybrid models on held-out user interactions.
Computes: Precision@K, Recall@K, Hit Rate@K, Catalog Coverage, and Intra-List Diversity.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.ml.recommender import RecommendationEngine


def run_evaluation(data_dir: str = "data/processed", sample_users: int = 150) -> Dict[str, Any]:
    print("Initializing recommender for evaluation...")
    engine = RecommendationEngine(data_dir=data_dir)
    engine.initialize()

    ratings_path = "data/raw/ml-latest-small/ratings.csv"
    ratings = pd.read_csv(ratings_path)

    # Filter to active users with at least 20 ratings
    user_counts = ratings.groupby("userId").size()
    eligible_users = user_counts[user_counts >= 20].index.values

    # Sample users for fast reproducible evaluation
    np.random.seed(42)
    eval_user_ids = np.random.choice(eligible_users, size=min(sample_users, len(eligible_users)), replace=False)

    print(f"Evaluating {len(eval_user_ids)} users with held-out preference sets...")

    # Data structures for metrics
    models = ["Popularity Baseline", "Content-Based", "Hybrid (CineSenseAI)"]
    metrics = {
        m: {
            "p5_list": [],
            "p10_list": [],
            "r10_list": [],
            "hit_list": [],
            "recommended_items": set(),
            "diversity_list": []
        }
        for m in models
    }

    # Precompute popular top-10 items for baseline
    top_popular_mids = [m["movieId"] for m in engine.get_curated_section("popular", limit=20)]

    for u_idx, uid in enumerate(eval_user_ids):
        u_ratings = ratings[ratings["userId"] == uid].sort_values("timestamp")
        
        # Positive interactions (rating >= 3.5 or >= 4.0)
        positives = u_ratings[u_ratings["rating"] >= 4.0]
        if len(positives) < 5:
            positives = u_ratings[u_ratings["rating"] >= 3.5]
        if len(positives) < 4:
            continue

        # Split 80% train, 20% test
        n_test = max(1, int(len(positives) * 0.25))
        train_pos = positives.iloc[:-n_test]
        test_pos = positives.iloc[-n_test:]
        
        test_mids = set(test_pos["movieId"].values)
        train_mids = list(train_pos["movieId"].values)

        if not test_mids or not train_mids:
            continue

        # 1. Popularity Baseline Recommendations (exclude train)
        pop_recs = [m for m in top_popular_mids if m not in train_mids][:10]
        
        # 2. Content-Based Recommendations (w_content=1.0, w_collab=0.0)
        cb_rec_objs = engine.recommend_for_user_profile(
            liked_movie_ids=train_mids[-5:],
            preferred_genres=[],
            top_k=10,
            w_content=1.0,
            w_rating=0.0,
            w_popularity=0.0,
            w_collab=0.0
        )
        cb_recs = [r["movieId"] for r in cb_rec_objs]

        # 3. Hybrid Recommendations (CineSenseAI balanced weights)
        hybrid_rec_objs = engine.recommend_for_user_profile(
            liked_movie_ids=train_mids[-5:],
            preferred_genres=[],
            top_k=10,
            w_content=0.55,
            w_rating=0.25,
            w_popularity=0.10,
            w_collab=0.10
        )
        hybrid_recs = [r["movieId"] for r in hybrid_rec_objs]

        rec_dict = {
            "Popularity Baseline": pop_recs,
            "Content-Based": cb_recs,
            "Hybrid (CineSenseAI)": hybrid_recs
        }

        # Calculate metrics for each model
        for m_name, rec_list in rec_dict.items():
            if not rec_list:
                continue

            # Update catalog coverage set
            metrics[m_name]["recommended_items"].update(rec_list)

            # Precision@5
            hits_5 = len(set(rec_list[:5]).intersection(test_mids))
            metrics[m_name]["p5_list"].append(hits_5 / 5.0)

            # Precision@10 & Recall@10
            hits_10 = len(set(rec_list[:10]).intersection(test_mids))
            metrics[m_name]["p10_list"].append(hits_10 / 10.0)
            metrics[m_name]["r10_list"].append(hits_10 / len(test_mids))
            metrics[m_name]["hit_list"].append(1.0 if hits_10 > 0 else 0.0)

            # Diversity (Mean Pairwise Cosine Distance of TF-IDF vectors)
            if len(rec_list) >= 2:
                valid_indices = [engine.movie_id_to_idx[mid] for mid in rec_list if mid in engine.movie_id_to_idx]
                if len(valid_indices) >= 2:
                    sub_matrix = engine.tfidf_matrix[valid_indices]
                    sim_mat = cosine_similarity(sub_matrix)
                    # Pairwise distance = 1 - sim
                    triu_indices = np.triu_indices(len(valid_indices), k=1)
                    pairwise_distances = 1.0 - sim_mat[triu_indices]
                    metrics[m_name]["diversity_list"].append(float(np.mean(pairwise_distances)))

    total_catalog_size = len(engine.movies_df)

    results = {
        "evaluation_info": {
            "users_evaluated": len(metrics["Hybrid (CineSenseAI)"]["p10_list"]),
            "catalog_size": total_catalog_size,
            "protocol": "Held-out test set (25% positive user ratings withheld, threshold >= 3.5-4.0)"
        },
        "models": []
    }

    for m_name in models:
        p5 = float(np.mean(metrics[m_name]["p5_list"])) if metrics[m_name]["p5_list"] else 0.0
        p10 = float(np.mean(metrics[m_name]["p10_list"])) if metrics[m_name]["p10_list"] else 0.0
        r10 = float(np.mean(metrics[m_name]["r10_list"])) if metrics[m_name]["r10_list"] else 0.0
        hit = float(np.mean(metrics[m_name]["hit_list"])) if metrics[m_name]["hit_list"] else 0.0
        cov = float(len(metrics[m_name]["recommended_items"]) / total_catalog_size * 100)
        div = float(np.mean(metrics[m_name]["diversity_list"])) if metrics[m_name]["diversity_list"] else 0.0

        model_entry = {
            "name": m_name,
            "precision_at_5": round(p5, 4),
            "precision_at_10": round(p10, 4),
            "recall_at_10": round(r10, 4),
            "hit_rate_at_10": round(hit, 4),
            "catalog_coverage_pct": round(cov, 2),
            "intra_list_diversity": round(div, 4),
            "unique_items_recommended": len(metrics[m_name]["recommended_items"])
        }
        results["models"].append(model_entry)
        print(f"\n[{m_name}]")
        print(f"  Precision@5:  {p5:.4f}")
        print(f"  Precision@10: {p10:.4f}")
        print(f"  Recall@10:    {r10:.4f}")
        print(f"  Hit Rate@10:  {hit * 100:.1f}%")
        print(f"  Coverage:     {cov:.2f}% ({len(metrics[m_name]['recommended_items'])} movies)")
        print(f"  Diversity:    {div:.4f}")

    eval_out_path = os.path.join(data_dir, "evaluation_results.json")
    with open(eval_out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved evaluation results to {eval_out_path}")
    return results


if __name__ == "__main__":
    run_evaluation()
