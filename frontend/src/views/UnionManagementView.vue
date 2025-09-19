<template>
  <div class="union-management">
    <h2>{{ t('unionManagement.title') }}</h2>

    <div class="add-union">
      <input
        v-model="newUnionName"
        type="text"
        :placeholder="t('unionManagement.add.placeholder')"
        :disabled="addUnionMutation.isPending.value"
        @keyup.enter="handleAddUnion"
      />
      <button :disabled="addUnionMutation.isPending.value" @click="handleAddUnion">
        {{ addUnionMutation.isPending.value ? t('unionManagement.add.addingButton') : t('unionManagement.add.addButton') }}
      </button>
    </div>
    <p v-if="addUnionMutation.isError.value" class="error">
      {{ t('unionManagement.add.errorMessage') }} {{ addUnionMutation.error.value.message }}
    </p>

    <div v-if="isLoading">{{ t('unionManagement.loading') }}</div>
    <div v-else-if="isError">{{ t('unionManagement.loadError') }} {{ error.message }}</div>
    <table v-else-if="unions && unions.length">
      <thead>
        <tr>
          <th>{{ t('unionManagement.table.header.name') }}</th>
          <th>{{ t('unionManagement.table.header.actions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="union in unions" :key="union.id">
          <td>
            <input
              v-if="editingUnionId === union.id"
              v-model="editingUnionName"
              @keyup.enter="handleUpdateUnion(union.id)"
            />
            <span v-else>{{ union.name }}</span>
          </td>
          <td>
            <div v-if="editingUnionId === union.id">
              <button @click="handleUpdateUnion(union.id)">{{ t('unionManagement.table.buttons.save') }}</button>
              <button class="secondary-btn" @click="cancelEdit">{{ t('unionManagement.table.buttons.cancel') }}</button>
            </div>
            <div v-else>
              <button @click="startEdit(union)">{{ t('unionManagement.table.buttons.edit') }}</button>
              <button class="delete-btn" @click="handleDeleteUnion(union.id)">{{ t('unionManagement.table.buttons.delete') }}</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else>
      <p>{{ t('unionManagement.emptyState') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { getUnions, addUnion, updateUnion, deleteUnion } from '../services/unionService';

const { t } = useI18n();
const queryClient = useQueryClient();

// --- Data Fetching ---
const { data: unions, isLoading, isError, error } = useQuery({
  queryKey: ['unions'],
  queryFn: async () => (await getUnions()).data,
});

// --- State for Forms ---
const newUnionName = ref('');
const editingUnionId = ref(null);
const editingUnionName = ref('');

// --- Mutations ---
const addUnionMutation = useMutation({
  mutationFn: addUnion,
  onSuccess: () => {
    queryClient.invalidateQueries(['unions']);
    newUnionName.value = '';
  },
});

const updateUnionMutation = useMutation({
  mutationFn: ({ id, name }) => updateUnion(id, name),
  onSuccess: () => {
    queryClient.invalidateQueries(['unions']);
    cancelEdit();
  },
});

const deleteUnionMutation = useMutation({
  mutationFn: deleteUnion,
  onSuccess: () => {
    queryClient.invalidateQueries(['unions']);
  },
});


// --- Event Handlers ---
const handleAddUnion = () => {
  if (!newUnionName.value.trim()) {
    alert(t('unionManagement.alerts.nameRequired'));
    return;
  }
  addUnionMutation.mutate(newUnionName.value.trim());
};

const startEdit = (union) => {
  editingUnionId.value = union.id;
  editingUnionName.value = union.name;
};

const cancelEdit = () => {
  editingUnionId.value = null;
  editingUnionName.value = '';
};

const handleUpdateUnion = (id) => {
  if (!editingUnionName.value.trim()) {
    alert(t('unionManagement.alerts.nameRequired'));
    return;
  }
  updateUnionMutation.mutate({ id, name: editingUnionName.value.trim() });
};

const handleDeleteUnion = (id) => {
  if (confirm(t('unionManagement.alerts.confirmDelete'))) {
    deleteUnionMutation.mutate(id);
  }
};
</script>

<style scoped>
.union-management {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.add-union {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: left;
}
th {
  background-color: #f8f8f8;
}
.secondary-btn {
  background-color: #6c757d;
  margin-left: 5px;
}
.delete-btn {
  background-color: #ff4d4f;
  margin-left: 5px;
}
.error {
  color: #ff4d4f;
}
</style>
