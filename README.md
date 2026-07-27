# 4CT — Four Color Theorem / Теорема о четырёх красках

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21514884.svg)](https://doi.org/10.5281/zenodo.21514884)
[![GitHub last commit](https://img.shields.io/github/last-commit/Vasilii-Kostin/4CT)](https://github.com/Vasilii-Kostin/4CT/commits/main)


---

## 🇬🇧 English

### About the Project

This project presents a **constructive proof of the Four Color Theorem** and an **explicit algorithm** for coloring planar graphs with 4 colors. Unlike the classic proof (Appel & Haken, 1977), which relies on computer-assisted verification of thousands of configurations, this approach is:

- **Human-verifiable** — the proof is based on a single, locally-checkable mechanism: **forced chains**.
- **Algorithmic** — it provides a deterministic, polynomial-time algorithm for 4‑coloring any planar graph.
- **Visual** — the algorithm shows exactly which structures require the fourth color.

The key idea is that **in any planar graph, the only reason 3 colors are not enough is the presence of forced chains**. By finding and eliminating these chains, the graph becomes 3-colorable. The fourth color is used only for vertices involved in these structures.

### What's Inside

- **`4_color.py`** — the complete Python implementation of the algorithm.
- **Website** — a full static site with theory and an example walkthrough: [vasilii-kostin.github.io/4CT](https://vasilii-kostin.github.io/4CT/)
- **Example graph** — `graph_35_03.json` (35 vertices, 95 edges) with full analysis and images.
- **Images** — visualizations of the original graph, 4‑color vertices, and all detected structures (K₄, odd stars, forced chains).

### How It Works

1. **Find all K₄** — complete graphs on 4 vertices.
2. **Find all odd stars** — a center connected to all vertices of an odd cycle.
3. **Find all forced chains** — sequences of triangles that force specific colors.
4. **Build an edge participation table** — each edge gets a score based on how many structures it belongs to.
5. **Split edges** — remove the edge with the highest score, rebuild the structures, and repeat.
6. **Color the sea** — once all structures are destroyed, the remaining graph is 3‑colorable.
7. **Color the islands** — assign the 4th color to the vertices that were part of the structures.

### Example

Run the algorithm on the included graph:

```bash
python 4_color.py graph_35_03.json
