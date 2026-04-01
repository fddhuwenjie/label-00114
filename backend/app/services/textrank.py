import re
import math
from collections import defaultdict
import time


class TextRankSummarizer:
    def __init__(self, max_sentences: int = 3, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-5):
        self.max_sentences = max_sentences
        self.damping = damping
        self.max_iter = max_iter
        self.tol = tol
        self.stop_words = self._get_stop_words()

    def _get_stop_words(self):
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'up', 'about', 'into', 'over', 'after', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'this', 'that', 'these',
            'those', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all',
            'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here',
            'there', 'then', 'once', 'if', 'because', 'as', 'until', 'while', 'of', '虽然', '但是',
            '的', '了', '和', '是', '在', '我', '有', '就', '不', '人', '都', '一', '一个', '上', '也',
            '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他',
            '而', '及', '与', '或', '之', '其', '于', '以', '为', '此', '乃', '仍', '何', '所', '故',
            '还', '又', '才', '再', '已', '给', '从', '该', '并', '本', '见', '后', '向', '它', '们',
            '比', '另', '得', '下', '吗', '吧', '呢', '啊', '哦', '嗯', '哼', '唉'
        }

    def _split_sentences(self, text: str):
        text = re.sub(r'\s+', ' ', text.strip())
        sentence_endings = r'[。！？.!?]+'
        sentences = re.split(sentence_endings, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _tokenize(self, text: str):
        text = text.lower()
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)
        words = [w for w in words if w not in self.stop_words and len(w) > 1]
        return words

    def _sentence_similarity(self, sent1_words, sent2_words):
        if not sent1_words or not sent2_words:
            return 0.0
        
        words1 = set(sent1_words)
        words2 = set(sent2_words)
        
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        
        common = words1.intersection(words2)
        return len(common) / (math.log(len(words1)) + math.log(len(words2)) + 1e-6)

    def _build_similarity_matrix(self, sentences_words):
        n = len(sentences_words)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self._sentence_similarity(sentences_words[i], sentences_words[j])
        
        return matrix

    def _pagerank(self, matrix):
        n = len(matrix)
        if n == 0:
            return []
        
        scores = [1.0 / n] * n
        
        for _ in range(self.max_iter):
            new_scores = [(1 - self.damping) / n] * n
            
            for j in range(n):
                row_sum = sum(matrix[j])
                if row_sum == 0:
                    continue
                for i in range(n):
                    new_scores[i] += self.damping * matrix[j][i] / row_sum * scores[j]
            
            diff = sum(abs(new_scores[i] - scores[i]) for i in range(n))
            scores = new_scores
            
            if diff < self.tol:
                break
        
        return scores

    def summarize(self, text: str):
        start_time = time.time()
        
        sentences = self._split_sentences(text)
        if len(sentences) <= self.max_sentences:
            return {
                'summary': ' '.join(sentences),
                'sentences': sentences,
                'generation_time_ms': int((time.time() - start_time) * 1000)
            }
        
        sentences_words = [self._tokenize(s) for s in sentences]
        matrix = self._build_similarity_matrix(sentences_words)
        scores = self._pagerank(matrix)
        
        scored_sentences = list(zip(scores, sentences, range(len(sentences))))
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        
        top_sentences = scored_sentences[:self.max_sentences]
        top_sentences.sort(key=lambda x: x[2])
        
        summary = ' '.join([s[1] for s in top_sentences])
        
        return {
            'summary': summary,
            'sentences': [s[1] for s in top_sentences],
            'generation_time_ms': int((time.time() - start_time) * 1000)
        }
