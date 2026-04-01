import re
import math
from collections import defaultdict
import time


class TextRankSummarizer:
    def __init__(self):
        self.damping = 0.85
        self.max_iter = 50
        self.tol = 1e-5
        self.stop_words = self._get_stop_words()

    def _get_stop_words(self):
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '他', '她', '它', '们', '这个', '那个', '什么', '怎么',
            '为什么', '哪', '哪里', '谁', '多少', '几', '啊', '吧', '呢', '吗', '呀',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'we', 'us',
            'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her', 'i', 'me', 'my', 'as',
            'if', 'when', 'than', 'because', 'while', 'until', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up',
            'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 's', 't', 'can', 'just', 'don', 'now'
        }

    def _split_sentences(self, text):
        text = text.replace('\n', ' ')
        sentences = re.split(r'[。！？；.!?;]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _tokenize(self, sentence):
        words = re.findall(r'[\w\u4e00-\u9fa5]+', sentence.lower())
        words = [w for w in words if w not in self.stop_words and len(w) > 1]
        return words

    def _cosine_similarity(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0
        
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        
        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        
        if not denominator:
            return 0.0
        return numerator / denominator

    def _build_similarity_matrix(self, sentences):
        n = len(sentences)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            vec_i = defaultdict(int)
            for word in self._tokenize(sentences[i]):
                vec_i[word] += 1
            
            for j in range(i + 1, n):
                vec_j = defaultdict(int)
                for word in self._tokenize(sentences[j]):
                    vec_j[word] += 1
                
                similarity = self._cosine_similarity(vec_i, vec_j)
                matrix[i][j] = similarity
                matrix[j][i] = similarity
        
        return matrix

    def _rank_sentences(self, matrix):
        n = len(matrix)
        scores = [1.0] * n
        
        for _ in range(self.max_iter):
            prev_scores = scores.copy()
            
            for i in range(n):
                sum_sim = 0.0
                for j in range(n):
                    if i != j and sum(matrix[j]) > 0:
                        sum_sim += matrix[j][i] / sum(matrix[j]) * scores[j]
                
                scores[i] = (1 - self.damping) + self.damping * sum_sim
            
            if sum(abs(scores[i] - prev_scores[i]) for i in range(n)) < self.tol:
                break
        
        return scores

    def summarize(self, text, num_sentences=3):
        start_time = time.time()
        
        sentences = self._split_sentences(text)
        if len(sentences) <= num_sentences:
            summary = '。'.join(sentences) + '。' if sentences else ''
            generation_time = int((time.time() - start_time) * 1000)
            return {
                'summary': summary,
                'num_sentences': len(sentences),
                'generation_time_ms': generation_time
            }
        
        similarity_matrix = self._build_similarity_matrix(sentences)
        scores = self._rank_sentences(similarity_matrix)
        
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        top_indices = sorted(ranked_indices[:num_sentences])
        
        summary = '。'.join([sentences[i] for i in top_indices]) + '。'
        generation_time = int((time.time() - start_time) * 1000)
        
        return {
            'summary': summary,
            'num_sentences': num_sentences,
            'generation_time_ms': generation_time
        }
