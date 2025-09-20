<template>
  <div class="player-data-hub-view">
    <h2>{{ t('playerDataHub.title') }}</h2>
    <div class="upload-section">
      <div v-if="unionsIsLoading">{{ t('playerDataHub.loadingUnions') }}</div>
      <div v-else-if="unionsIsError">{{ t('playerDataHub.loadUnionsError') }}</div>
      <form v-else class="upload-form" @submit.prevent="handleUpload">
        <div class="form-group">
          <label for="union-select">{{ t('playerDataHub.form.selectUnionLabel') }}</label>
          <select id="union-select" v-model="selectedUnionId" :disabled="!unions || unions.length === 0">
            <option :value="null" disabled>
              {{ unions && unions.length > 0 ? t('playerDataHub.form.selectUnionPlaceholder') : t('playerDataHub.form.noUnionsPlaceholder') }}
            </option>
            <option v-for="union in unions" :key="union.id" :value="union.id">
              {{ union.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="file-input">{{ t('playerDataHub.form.selectFileLabel') }}</label>
          <input
            id="file-input"
            type="file"
            accept=".json"
            multiple
            @change="handleFileChange"
          />
        </div>

        <button type="submit" :disabled="!selectedUnionId || filesToUpload.length === 0 || uploadMutation.isPending.value">
          {{ uploadMutation.isPending.value ? t('playerDataHub.form.uploadingButton') : t('playerDataHub.form.uploadButton') }}
        </button>
      </form>

      <div v-if="uploadMutation.isSuccess.value" class="status-message success">
        <p>{{ t('playerDataHub.uploadStatus.successMessage') }}</p>
        <p>
          {{ uploadMutation.data.value?.data.successful_files }} {{ t('playerDataHub.uploadStatus.filesSuccess') }}
          {{ uploadMutation.data.value?.data.failed_files }} {{ t('playerDataHub.uploadStatus.filesFailed') }}
        </p>
      </div>
      <div v-if="uploadMutation.isError.value" class="status-message error">
        <p>{{ t('playerDataHub.uploadStatus.errorMessage') }} {{ uploadMutation.error.value?.message }}</p>
      </div>
    </div>

    <!-- The player list display will be implemented in a later phase -->
    <div class="player-list-section">
      <h3>{{ t('playerDataHub.playerList.title') }}</h3>
      <p>{{ t('playerDataHub.playerList.wip') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from 'vue';
import { useI18n } from 'vue-i18n';
import { useQuery, useMutation } from '@tanstack/vue-query';
import { getUnions, uploadPlayerData } from '../services/unionService';

const { t } = useI18n();
const { proxy } = getCurrentInstance();

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
    proxy.$toast.error(t('playerDataHub.alerts.selectUnionAndFile'));
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
