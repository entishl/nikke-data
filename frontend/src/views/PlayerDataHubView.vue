<template>
  <div class="player-data-hub-view">
    <h2>玩家数据导入</h2>
    <div class="upload-section">
      <div v-if="unionsIsLoading">正在加载联盟列表...</div>
      <div v-else-if="unionsIsError">加载联盟列表失败。</div>
      <form v-else class="upload-form" @submit.prevent="handleUpload">
        <div class="form-group">
          <label for="union-select">选择联盟:</label>
          <select id="union-select" v-model="selectedUnionId" :disabled="!unions || unions.length === 0">
            <option :value="null" disabled>
              {{ unions && unions.length > 0 ? '请选择一个联盟' : '请先创建一个联盟' }}
            </option>
            <option v-for="union in unions" :key="union.id" :value="union.id">
              {{ union.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="file-input">选择 JSON 文件:</label>
          <input
            id="file-input"
            type="file"
            accept=".json"
            multiple
            @change="handleFileChange"
          />
        </div>

        <button type="submit" :disabled="!selectedUnionId || filesToUpload.length === 0 || uploadMutation.isPending.value">
          {{ uploadMutation.isPending.value ? '上传中...' : '上传数据' }}
        </button>
      </form>

      <div v-if="uploadMutation.isSuccess.value" class="status-message success">
        <p>上传成功!</p>
        <p>{{ uploadMutation.data.value?.data.successful_files }} 个文件成功, {{ uploadMutation.data.value?.data.failed_files }} 个失败。</p>
      </div>
      <div v-if="uploadMutation.isError.value" class="status-message error">
        <p>上传失败: {{ uploadMutation.error.value?.message }}</p>
      </div>
    </div>

    <!-- The player list display will be implemented in a later phase -->
    <div class="player-list-section">
      <h3>玩家列表</h3>
      <p>(列表展示功能将在后续阶段实现)</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useQuery, useMutation } from '@tanstack/vue-query';
import { getUnions, uploadPlayerData } from '../services/unionService';

// --- State ---
const selectedUnionId = ref(null);
const filesToUpload = ref([]);

// --- Queries ---
const { data: unions, isLoading: unionsIsLoading, isError: unionsIsError } = useQuery({
  queryKey: ['unions'],
  queryFn: async () => (await getUnions()).data,
});

// --- Mutations ---
const uploadMutation = useMutation({
  mutationFn: uploadPlayerData,
});

// --- Event Handlers ---
const handleFileChange = (event) => {
  filesToUpload.value = Array.from(event.target.files);
};

const handleUpload = () => {
  if (!selectedUnionId.value || filesToUpload.value.length === 0) {
    alert('请选择一个联盟并选择至少一个文件。');
    return;
  }

  const formData = new FormData();
  filesToUpload.value.forEach(file => {
    formData.append('files', file);
  });
  formData.append('union_id', selectedUnionId.value);

  uploadMutation.mutate(formData);
};
</script>

<style scoped>
.player-data-hub-view {
  padding: 20px;
}
.upload-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.upload-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.status-message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 5px;
}
.status-message.success {
  background-color: #e6ffed;
  border-left: 5px solid #4caf50;
  color: #2e7d32;
}
.status-message.error {
  background-color: #ffebee;
  border-left: 5px solid #f44336;
  color: #c62828;
}
</style>
