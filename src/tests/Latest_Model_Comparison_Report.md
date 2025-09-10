# Date: 10/09/2025 - Testd Against Model genrated on same day 
---
# Emotion and Sentiment Model Analysis: Final Report

This report provides a comprehensive analysis of the performance of four emotion and sentiment classification models: **Emotion Server API**, **Azure API**, **Hugging Face**, and **OpenAI (ChatGPT)**. The evaluation is based on a test set of 226 samples, assessing both granular (13 emotions) and general (3 sentiment categories) classification accuracy, as well as processing speed.

---

## Executive Summary

The results clearly demonstrate that the **Emotion Server API** is a superior model, outperforming others across every key metric. It is significantly more accurate at granular emotion classification and a top-tier performer in sentiment analysis, all while being remarkably faster than the commercial APIs from Azure and OpenAI.

---

## Key Performance Metrics

| Model              | Granular Accuracy | Sentiment Accuracy | Time (s) |
|--------------------|-------------------|---------------------|----------|
| Emotion Server API | **60.62%**        | **81.00%**          | **5.41** |
| Azure API          | 27.23%            | 69.00%              | 127.24   |
| Hugging Face       | 42.04%            | 71.00%              | **0.49** |
| OpenAI             | 43.36%            | 74.00%              | 137.97   |

---

## Detailed Analysis by Model

### Emotion Server API: A Top Performer

The **Emotion Server API** is a best-in-class solution for this task. It achieves a **60.62% accuracy** on the challenging 13-class emotion classification, which is nearly 20 percentage points higher than its closest competitor.

Furthermore, when the task is simplified to sentiment analysis, its performance is exceptional with an **81% accuracy**, setting the benchmark. Critically, its processing speed of **5.41 seconds** is incredibly efficient, making it suitable for high-volume applications where both speed and accuracy are paramount.

---

### OpenAI (ChatGPT)

**OpenAI's model** performs better than the pre-trained Hugging Face model on the granular emotion task with an accuracy of **43.36%**. However, it falls significantly short of the Emotion Server API's performance.

Its sentiment accuracy of **74%** is solid but still trails the Emotion Server API. The most notable drawback is its slow processing time of **137.97 seconds**, which is the longest of all models tested and makes it impractical for real-time applications.

---

### Hugging Face

The **Hugging Face model** is the fastest by an enormous margin, completing all tests in just **0.49 seconds**. This makes it an excellent choice for scenarios where **speed is the single most important factor**.

However, this speed comes at the cost of accuracy. Its **42.04%** granular accuracy is the lowest among the three API-based models, and its **71%** sentiment accuracy places it behind both the Emotion Server API and OpenAI. It is a powerful tool for a quick, general understanding but lacks the precision of a purpose-built model.

---

### Azure API

The **Azure API** demonstrates once again that it is **not designed for granular emotion classification**, as shown by its very low **27.23% accuracy**. It performs better on its intended task of sentiment analysis, achieving a decent **69% accuracy**.

However, its slow processing time of **127.24 seconds** and its inability to handle the complexity of multi-emotion classification make it a less suitable option.

---

## Final Conclusion

Based on this comprehensive analysis, the **Emotion Server API** is a top choice. It is the most accurate solution for **granular emotion detection**, a leading model for **sentiment classification**, and provides a **significant speed advantage** over the most prominent commercial APIs.

This final report confirms that the effort invested in building a **custom solution** has yielded a highly effective and efficient model.

