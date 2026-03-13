<template>
  <div>
    <div class="page-header">
      <h1>审核确认</h1>
      <p class="subtitle">确认AI生成的分类和标签</p>
    </div>

    <div v-if="list.length" class="review-list">
      <div v-for="f in list" :key="f.id" class="review-card">
        <div class="file-info">
          <div class="file-name">{{ f.name }}</div>
          <div class="file-meta"><span class="tag">{{ f.bucket }}</span></div>
        </div>
        <div class="suggestion">
          <label>AI建议标准名</label>
          <div class="value">{{ f.standard_name || '未生成' }}</div>
        </div>
        <div class="actions">
          <button class="btn-approve" @click="review(f.id, 'approve')">✓ 通过</button>
          <button class="btn-reject" @click="review(f.id, 'reject')">✗ 拒绝</button>
        </div>
      </div>
    </div>
    <div v-else class="empty-card"><p>🎉 所有文件已审核完成</p></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { files } from '../api'
import { useToast } from '../composables/useToast'
const toast = useToast()
const list = ref([])
const load = async () => {
  try {
    const { data } = await files.list({ status: 'completed' })
    list.value = (data.files || []).filter(f => f.review_status === 'pending')
  } catch { toast.error('加载审核列表失败'); list.value = [] }
}
const review = async (id, action) => {
  try {
    await files.review(id, action)
    toast.success(action === 'approve' ? '已通过审核' : '已拒绝')
    load()
  } catch { toast.error('审核操作失败') }
}
onMounted(load)
</script>

<style scoped>
.page-header { background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 24px; }
h1 { font-size: 24px; color: #1e293b; }
.subtitle { color: #64748b; }
.review-list { display: flex; flex-direction: column; gap: 16px; }
.review-card { background: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; }
.file-info { margin-bottom: 16px; }
.file-name { font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }
.tag { background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
.suggestion { margin-bottom: 16px; }
.suggestion label { font-size: 12px; color: #64748b; text-transform: uppercase; }
.suggestion .value { margin-top: 8px; padding: 12px; background: #f8fafc; border-radius: 8px; font-family: monospace; }
.actions { display: flex; gap: 12px; }
.btn-approve { padding: 10px 20px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; }
.btn-reject { padding: 10px 20px; background: #f1f5f9; color: #64748b; border: none; border-radius: 8px; cursor: pointer; }
.empty-card { background: white; padding: 60px; border-radius: 12px; text-align: center; color: #64748b; }
</style>
