<template>
  <div>
    <div class="header">
      <div>
        <h1>文件管理</h1>
        <p>上传和管理知识库文件</p>
      </div>
      <label class="btn-upload">
        📤 上传文件
        <input type="file" multiple @change="upload" hidden />
      </label>
    </div>

    <div class="filters">
      <select v-model="filter.bucket" @change="load">
        <option value="">全部分类</option>
        <option value="方案">方案</option>
        <option value="彩页">彩页</option>
        <option value="视频">视频</option>
        <option value="安装包">安装包</option>
      </select>
      <select v-model="filter.status" @change="load">
        <option value="">全部状态</option>
        <option value="pending">待处理</option>
        <option value="processing">处理中</option>
        <option value="completed">已完成</option>
        <option value="failed">失败</option>
      </select>
      <button @click="load" class="btn-refresh">🔄 刷新</button>
    </div>

    <div class="card">
      <table v-if="list.length">
        <thead>
          <tr>
            <th>文件名</th>
            <th>标准名</th>
            <th>分类</th>
            <th>状态</th>
            <th>审核</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in list" :key="f.id">
            <td>{{ f.name }}</td>
            <td>{{ f.standard_name || '-' }}</td>
            <td><span class="tag">{{ f.bucket }}</span></td>
            <td><span :class="['status', f.status]">{{ statusMap[f.status] }}</span></td>
            <td><span :class="['status', f.review_status]">{{ reviewMap[f.review_status] }}</span></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">暂无文件，请上传</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { files } from '../api'

const list = ref([])
const filter = reactive({ bucket: '', status: '' })
const statusMap = { pending: '待处理', processing: '处理中', completed: '已完成', failed: '失败' }
const reviewMap = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }

const load = async () => {
  const params = {}
  if (filter.bucket) params.bucket = filter.bucket
  if (filter.status) params.status = filter.status
  try {
    const { data } = await files.list(params)
    list.value = data.files || []
  } catch (e) {
    console.error('Failed to load files:', e)
    list.value = []
  }
}

const upload = async (e) => {
  const fd = new FormData()
  for (const f of e.target.files) fd.append('files', f)
  await files.upload(fd)
  e.target.value = ''
  setTimeout(load, 500)
}

onMounted(load)
</script>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
h1 { font-size: 24px; color: #1e293b; }
p { color: #64748b; font-size: 14px; margin-top: 4px; }
.btn-upload {
  padding: 10px 20px;
  background: #6366f1;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}
.filters { display: flex; gap: 12px; margin-bottom: 20px; }
.filters select {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  font-size: 14px;
}
.btn-refresh {
  padding: 10px 16px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
.card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 14px 16px; font-size: 12px; color: #64748b; border-bottom: 1px solid #e2e8f0; text-transform: uppercase; }
td { padding: 14px 16px; border-bottom: 1px solid #f1f5f9; }
.tag { background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 12px; font-size: 12px; }
.status { padding: 4px 10px; border-radius: 12px; font-size: 12px; }
.status.pending { background: #f1f5f9; color: #64748b; }
.status.processing { background: #fef3c7; color: #92400e; }
.status.completed, .status.approved { background: #dcfce7; color: #166534; }
.status.failed, .status.rejected { background: #fee2e2; color: #991b1b; }
.empty { padding: 60px; text-align: center; color: #94a3b8; }
</style>
