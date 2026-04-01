<template>
  <div>
    <div class="page-header">
      <div>
        <button @click="goBack" class="btn-back">← 返回</button>
        <h1>{{ file?.original_name }}</h1>
        <p class="subtitle">{{ file?.standard_name || '-' }}</p>
      </div>
    </div>

    <div v-if="loading" class="loading-card">
      <div class="spinner"></div>
      <p>加载文档详情中...</p>
    </div>

    <div v-else-if="file">
      <div class="summary-card">
        <div class="summary-header">
          <div class="summary-title">
            <span class="icon">📝</span>
            <span>文档摘要</span>
          </div>
          <button @click="regenerateSummary" :disabled="generating" class="btn-regenerate">
            {{ generating ? '生成中...' : '🔄 重新生成' }}
          </button>
        </div>
        <div v-if="summary" class="summary-content">
          <p>{{ summary }}</p>
        </div>
        <div v-else class="summary-empty">
          <p>暂无摘要，点击"重新生成"按钮生成</p>
        </div>
        <div v-if="generationTime > 0" class="summary-footer">
          <span class="generation-time">生成耗时: {{ generationTime }}ms</span>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-card">
          <h3>基本信息</h3>
          <div class="info-row">
            <span class="label">文件类型</span>
            <span class="tag">{{ file.file_type }}</span>
          </div>
          <div class="info-row">
            <span class="label">分类</span>
            <span class="tag">{{ file.bucket }}</span>
          </div>
          <div class="info-row">
            <span class="label">处理状态</span>
            <span :class="['status', file.process_status]">{{ statusMap[file.process_status] }}</span>
          </div>
          <div class="info-row">
            <span class="label">审核状态</span>
            <span :class="['status', file.review_status]">{{ reviewMap[file.review_status] }}</span>
          </div>
          <div class="info-row">
            <span class="label">上传时间</span>
            <span>{{ formatDate(file.created_at) }}</span>
          </div>
        </div>

        <div class="info-card">
          <h3>标签信息</h3>
          <div class="tags-list">
            <span v-for="tag in tags" :key="tag.id" class="tag-item">
              {{ tag.tag_name }}: {{ tag.tag_value }}
            </span>
          </div>
          <div v-if="!tags.length" class="empty-tags">
            暂无标签
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { files, documents } from '../api'
import { useToast } from '../composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const file = ref(null)
const tags = ref([])
const summary = ref('')
const loading = ref(true)
const generating = ref(false)
const generationTime = ref(0)

const statusMap = { pending: '待处理', processing: '处理中', completed: '已完成', failed: '失败' }
const reviewMap = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }

const goBack = () => {
  router.push('/files')
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const loadFile = async () => {
  loading.value = true
  try {
    const { data } = await files.get(route.params.id)
    file.value = data.file
    tags.value = data.tags
    summary.value = data.file.summary || ''
  } catch {
    toast.error('加载文档详情失败')
  } finally {
    loading.value = false
  }
}

const regenerateSummary = async () => {
  generating.value = true
  try {
    const { data } = await documents.generateSummary(route.params.id, true)
    summary.value = data.summary
    generationTime.value = data.generation_time_ms
    toast.success(data.regenerated ? '摘要生成成功' : '使用缓存摘要')
  } catch {
    toast.error('摘要生成失败')
  } finally {
    generating.value = false
  }
}

onMounted(loadFile)
</script>

<style scoped>
.page-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 24px;
}
.btn-back {
  background: none;
  border: none;
  color: #6366f1;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 12px;
  padding: 0;
}
.btn-back:hover {
  text-decoration: underline;
}
h1 {
  font-size: 24px;
  color: #1e293b;
  margin-bottom: 4px;
  word-break: break-all;
}
.subtitle {
  color: #64748b;
  font-size: 14px;
}
.loading-card {
  background: white;
  padding: 60px;
  border-radius: 12px;
  text-align: center;
  color: #64748b;
  border: 1px solid #e2e8f0;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.summary-card {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  color: white;
}
.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.summary-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}
.icon {
  font-size: 20px;
}
.btn-regenerate {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}
.btn-regenerate:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}
.btn-regenerate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.summary-content {
  background: rgba(255, 255, 255, 0.15);
  padding: 16px;
  border-radius: 8px;
  line-height: 1.8;
}
.summary-empty {
  background: rgba(255, 255, 255, 0.1);
  padding: 24px;
  border-radius: 8px;
  text-align: center;
  opacity: 0.8;
}
.summary-footer {
  margin-top: 12px;
  text-align: right;
  font-size: 12px;
  opacity: 0.8;
}
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.info-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.info-card h3 {
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}
.label {
  color: #64748b;
  font-size: 14px;
}
.tag {
  background: #e0e7ff;
  color: #4338ca;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}
.status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}
.status.pending { background: #f1f5f9; color: #64748b; }
.status.processing { background: #fef3c7; color: #92400e; }
.status.completed, .status.approved { background: #dcfce7; color: #166534; }
.status.failed, .status.rejected { background: #fee2e2; color: #991b1b; }
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag-item {
  background: #f8fafc;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  border: 1px solid #e2e8f0;
}
.empty-tags {
  color: #94a3b8;
  text-align: center;
  padding: 20px;
}
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  .summary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
