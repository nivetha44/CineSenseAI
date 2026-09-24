# CineSenseAI — Recommendation Methodology & Algorithm Design

## 1. Problem Formulation
Movie recommendation platforms face a fundamental trilemma:
1. **Accuracy**: Recommendations must align with the user's authentic taste.
2. **Catalog Diversity & Serendipity**: The recommender must avoid only outputting the same 10 blockbusters (popularity bias).
3. **Transparency & Trust**: Users want to know *why* a film appeared in their feed rather than receiving predictions from an opaque black box.

CineSenseAI addresses this through a **Hybrid Explainable Recommendation Framework**.

---

## 2. Feature Engineering & Representation

Each movie $m_i$ is mapped to a composite textual and metadata document:
$$\text{Soup}(m_i) = 2 \times \text{Genres}(m_i) + 2 \times \text{Director}(m_i) + \text{Cast}(m_i) + \text{Tags}(m_i) + \text{Plot}(m_i) + \text{Decade}(m_i)$$

Key considerations:
- **Genre & Directorial Boosting**: Genres and directorship are repeated to amplify their term frequency weight relative to free-form synopsis words.
- **Bi-gram Tokenization**: Captures key phrases such as "science fiction", "time travel", "dark comedy", and "twist ending".
- **TF-IDF Weighting**: Down-weights universal filler tokens and accentuates discriminating thematic terminology:
  $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

---

## 3. Similarity Calculation

Cosine similarity measures the angle between query vector $\mathbf{q}$ and item vector $\mathbf{v}_i$:
$$\text{Sim}_{\text{content}}(\mathbf{q}, \mathbf{v}_i) = \frac{\mathbf{q} \cdot \mathbf{v}_i}{\|\mathbf{q}\|_2 \|\mathbf{v}_i\|_2}$$

Because all TF-IDF vectors in the CSR matrix are pre-normalized to unit Euclidean length ($\|\mathbf{v}\|_2 = 1$), cosine similarity simplifies to the matrix dot product:
$$\mathbf{S}_{\text{content}} = \mathbf{M}_{\text{tfidf}} \mathbf{q}^T$$

---

## 4. Collaborative Affinity & Rating Prior

### 4.1 Item-Item Collaborative Correlation
To incorporate crowd wisdom without requiring user registration, CineSenseAI constructs an item-item correlation matrix from user-rating patterns:
- Ratings are mean-centered per user: $r'_{u,i} = r_{u,i} - \bar{r}_u$.
- Pairwise cosine similarity is computed between item rating vectors:
  $$S_{\text{collab}}(i, j) = \frac{\sum_{u \in U_{ij}} r'_{u,i} r'_{u,j}}{\sqrt{\sum_{u \in U_i} (r'_{u,i})^2} \sqrt{\sum_{u \in U_j} (r'_{u,j})^2}}$$

### 4.2 Bayesian Prior (IMDb Weighted Score)
To prevent movies with 1 review of 5.0 from outranking verified classics, we apply empirical Bayes smoothing:
$$WR(i) = \frac{v_i}{v_i + m} R_i + \frac{m}{v_i + m} C$$
- $v_i$: number of reviews for movie $i$
- $m$: threshold minimum reviews ($m=10$)
- $R_i$: sample mean rating of movie $i$
- $C$: global catalog average rating ($C = 3.50$)

---

## 5. Transparent Scoring Formula

Candidate movies are ranked according to a multi-objective scoring function:
$$\text{FinalScore}(i) = w_c \cdot S_{\text{content}}(i) + w_r \cdot \left(\frac{WR(i)}{5.0}\right) + w_p \cdot P_{\text{norm}}(i) + w_{\text{collab}} \cdot \max(0, S_{\text{collab}}(i))$$

**Default Production Weights:**
- $w_c = 0.55$: Content metadata similarity
- $w_r = 0.25$: Bayesian rating quality
- $w_p = 0.10$: Normalized popularity volume ($\log(v_i + 1) / \log(v_{\max} + 1)$)
- $w_{\text{collab}} = 0.10$: Item-item collaborative affinity

Users and system evaluators can adjust these weights in real-time through the UI to inspect how recommendations evolve.

---

## 6. Explainable AI (XAI) Engine

Rather than displaying static AI badges, CineSenseAI computes real matching factors:
1. **Genre Intersection**: Exact set intersection $\text{Genres}(m_{\text{seed}}) \cap \text{Genres}(m_{\text{candidate}})$.
2. **Directorial & Cast Overlap**: Identifies matching directors or actors.
3. **Community Tag Overlap**: Identifies shared thematic tags (e.g., "mindfuck", "pixar", "superhero").
4. **Collaborative Confirmation**: Verifies if audience co-rating affinity exceeds $0.20$.
