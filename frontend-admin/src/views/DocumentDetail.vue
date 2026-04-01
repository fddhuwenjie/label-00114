<template>
  <div>
    <div class="page-header">
      <div>
        <button class="btn-back" @click="$router.push('/files')">
          ← 返回列表
        </button>
        <h1>文档详情</h1>
        <p>查看文档信息和 AI 生成摘要</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载文档信息中...</span>
    </div>

    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="btn-retry" @click="loadDocument">重试</button>
    </div>

    <div v-else-if="document">
      <div class="summary-card">
        <div class="summary-header">
          <span class="summary-icon">📝</span>
          <span class="summary-title">文档摘要</span>
          <span v-if="summaryData?.cached" class="badge-cached">已缓存</span>
        </div>
        <div class="summary-content">
          <p v-if="!summaryGenerating">{{ summaryData?.summary || '暂无摘要，请点击下方按钮生成' }}</p>
          <div v-else class="summary-loading">
            <div class="spinner"></div>
            <span>正在使用 TextRank 算法生成摘要...</span>
          </div>
        </div>
        <div class="summary-footer">
          <span v-if="summaryData?.generation_time_ms > 0" class="generation-time">
            生成耗时: {{ summaryData.generation_time_ms }}ms
          </span>
          <button 
            class="btn-regenerate" 
            @click="generateSummary(true)" 
            :disabled="summaryGenerating || document.status !== 'completed'"
          >
            🔄 {{ summaryData?.summary ? '重新生成' : '生成摘要' }}
          </button>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">基本信息</h3>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="label">文件名</span>
            <span class="value">{{ document.name }}</span>
          </div>
          <div class="detail-item">
            <span class="label">标准名</span>
            <span class="value">{{ document.standard_name || '-' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">分类</span>
            <span class="value"><span class="tag">{{ document.bucket }}</span></span>
          </div>
          <div class="detail-item">
            <span class="label">文件类型</span>
            <span class="value">{{ document.file_type?.toUpperCase() }}</span>
          </div>
          <div class="detail-item">
            <span class="label">处理状态</span>
            <span class="value"><span :class="['status', document.status]">{{ statusMap[document.status] }}</span></span>
          </div>
          <div class="detail-item">
            <span class="label">审核状态</span>
            <span class="value"><span :class="['status', document.review_status]">{{ reviewMap[document.review_status] }}</span></span>
          </div>
        </div>
      </div>

      <div class="card action-bar">
        <button @click="reviewFile('approve')" class="btn-approve">
          ✅ 通过审核
        </button>
        <button @click="reviewFile('reject')" class="btn-reject">
          ❌ 拒绝
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { documents, files } from '../api'
import { useToast } from '../composables/useToast'

const route = useRoute()
const toast = useToast()

const document = ref(null)
const summaryData = ref(null)
const summaryGenerating = ref(false)
const loading = ref(false)
const error = ref('')

const statusMap = { pending: '待处理', processing: '处理中', completed: '已完成', failed: '失败' }
const reviewMap = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }

const loadDocument = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await documents.get(route.params.id)
    document.value = data
    summaryData.value = {
      summary: data.summary,
      cached: true,
      generation_time_ms: 0
    }
    
    if (data.status === 'completed' && data.summary) {
      await generateSummary(false)
    }
  } catch (err) {
    error.value = '加载文档失败'
    toast.error('加载文档失败')
  } finally {
    loading.value = false
  }
}

const generateSummary = async (regenerate = false) => {
  if (document.value.status !== 'completed') {
    toast.info('请等待文件处理完成后再生成摘要')
    return
  }
  
  summaryGenerating.value = true
  try {
    const { data } = await documents.generateSummary(route.params.id, regenerate)
    summaryData.value = data
    if (regenerate) {
      toast.success(`摘要生成成功，耗时: ${data.generation_time_ms}ms`)
    }
  } catch (err) {
    toast.error('摘要生成失败')
  } finally {
    summaryGenerating.value = false
  }
}

const reviewFile = async (action) => {
  try {
    await files.review(route.params.id, action)
    toast.success(action === 'approve' ? '审核通过' : '已拒绝')
    document.value.review_status = action === 'approve' ? 'approved' : 'rejected'
  } catch (err) {
    toast.error('操作失败')
  }
}

onMounted(loadDocument)
</script>

<style scoped>
.page-header { margin-bottom: 24px; }
.btn-back { background: none; border: none; color: #6366f1; cursor: pointer; font-size: 14px; margin-bottom: 8px; padding: 0; }
.btn-back:hover { text-decoration: underline; }
h1 { font-size: 24px; color: #1e293b; }
p { color: #64748b; font-size: 14px; margin-top: 4px; }

.loading-state, .error-state {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 60px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #64748b;
}
.error-icon { font-size: 40px; }
.btn-retry { padding: 8px 20px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; }

.summary-card {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
  margin-bottom: 24px;
}
.summary-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.summary-icon { font-size: 28px; }
.summary-title { font-weight: 600; font-size: 18px; }
.badge-cached {
  background: rgba(255,255,255,0.2);
  padding: 5px 12px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: auto;
}
.summary-content {
  background: rgba(255,255,255,0.95);
  color: #1e293b;
  border-radius: 10px;
  padding: 20px;
  line-height: 1.7;
  margin-bottom: 16px;
  min-height: 70px;
}
.summary-content p { color: #334155; margin: 0; font-size: 15px; }
.summary-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #64748b;
}
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.summary-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.generation-time {
  font-size: 13px;
  opacity: 0.9;
}
.btn-regenerate {
  background: white;
  color: #6366f1;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-regenerate:hover:not(:disabled) {
  transform: translateY(-1px);
}
.btn-regenerate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 24px;
  margin-bottom: 24px;
}
.section-title {
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.detail-item .label {
  font-size: 13px;
  color: #64748b;
}
.detail-item .value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}
.tag {
  background: #e0e7ff;
  color: #4338ca;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  display: inline-block;
}
.status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  display: inline-block;
}
.status.pending { background: #f1f5f9; color: #64748b; }
.status.processing { background: #fef3c7; color: #92400e; }
.status.completed, .status.approved { background: #dcfce7; color: #166534; }
.status.failed, .status.rejected { background: #fee2e2; color: #991b1b; }

.action-bar {
  display: flex;
  gap: 16px;
}
.btn-approve, .btn-reject {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-approve:hover, .btn-reject:hover {
  transform: translateY(-1px);
}
.btn-approve { background: #dcfce7; color: #166534; }
.btn-reject { background: #fee2e2; color: #991b1b; }

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .action-bar {
    flex-direction: column;
  }
}
</style>
