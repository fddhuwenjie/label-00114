import re
import math
import time
from typing import List, Tuple
from collections import defaultdict


class TextRankSummarizer:
    def __init__(self, d: float = 0.85, max_iter: int = 100, tol: float = 1e-4):
        self.d = d
        self.max_iter = max_iter
        self.tol = tol
        self.stopwords = self._load_stopwords()

    def _load_stopwords(self) -> set:
        return {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这",
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their", "mine", "yours", "hers", "ours", "theirs", "this", "that", "these", "those", "what", "which", "who", "whom", "whose", "where", "when", "why", "how", "all", "each", "every", "both", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just", "also", "now", "here", "there", "then", "once", "if", "because", "as", "until", "while", "of", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "from", "up", "down", "out", "off", "over", "under", "again", "further"
        }

    def _preprocess(self, text: str) -> Tuple[List[str], List[str]]:
        text = re.sub(r'\s+', ' ', text).strip()
        sentences = self._split_sentences(text)
        words_list = []
        for sent in sentences:
            words = self._tokenize(sent)
            words = [w for w in words if w.lower() not in self.stopwords and len(w) > 1]
            words_list.append(words)
        return sentences, words_list

    def _split_sentences(self, text: str) -> List[str]:
        sentences = []
        pattern = r'[。！？!?…]'
        parts = re.split(pattern, text)
        for part in parts:
            part = part.strip()
            if part:
                sentences.append(part)
        return sentences

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.split()

    def _cosine_similarity(self, vec1: List[str], vec2: List[str]) -> float:
        if not vec1 or not vec2:
            return 0.0
        set1 = set(vec1)
        set2 = set(vec2)
        intersection = len(set1 & set2)
        if intersection == 0:
            return 0.0
        return intersection / math.sqrt(len(set1) * len(set2))

    def _build_similarity_matrix(self, words_list: List[List[str]]) -> List[List[float]]:
        n = len(words_list)
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self._cosine_similarity(words_list[i], words_list[j])
        return matrix

    def _rank_sentences(self, matrix: List[List[float]]) -> List[float]:
        n = len(matrix)
        scores = [1.0] * n
        for _ in range(self.max_iter):
            new_scores = [0.0] * n
            for i in range(n):
                s = 0.0
                for j in range(n):
                    if i != j:
                        row_sum = sum(matrix[j])
                        if row_sum > 0:
                            s += (matrix[j][i] / row_sum) * scores[j]
                new_scores[i] = (1 - self.d) + self.d * s
            delta = max(abs(new_scores[i] - scores[i]) for i in range(n))
            scores = new_scores
            if delta < self.tol:
                break
        return scores

    def summarize(self, text: str, num_sentences: int = 3) -> Tuple[str, int]:
        start_time = time.time()
        if not text or not text.strip():
            return "", int((time.time() - start_time) * 1000)
        
        sentences, words_list = self._preprocess(text)
        
        if len(sentences) <= num_sentences:
            return "。".join(sentences) + "。", int((time.time() - start_time) * 1000)
        
        matrix = self._build_similarity_matrix(words_list)
        scores = self._rank_sentences(matrix)
        
        scored_sentences = [(i, scores[i], sentences[i]) for i in range(len(sentences))]
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = scored_sentences[:num_sentences]
        top_sentences.sort(key=lambda x: x[0])
        
        summary = "。".join([s[2] for s in top_sentences]) + "。"
        generation_time = int((time.time() - start_time) * 1000)
        
        return summary, generation_time
