<template>
  <div class="union-management">
    <h2>联盟管理</h2>

    <div class="add-union">
      <input
        v-model="newUnionName"
        type="text"
        placeholder="输入新联盟名称"
        :disabled="addUnionMutation.isPending.value"
        @keyup.enter="handleAddUnion"
      />
      <button :disabled="addUnionMutation.isPending.value" @click="handleAddUnion">
        {{ addUnionMutation.isPending.value ? '添加中...' : '添加联盟' }}
      </button>
    </div>
    <p v-if="addUnionMutation.isError.value" class="error">
      添加失败: {{ addUnionMutation.error.value.message }}
    </p>

    <div v-if="isLoading">正在加载联盟列表...</div>
    <div v-else-if="isError">加载联盟列表失败: {{ error.message }}</div>
    <table v-else-if="unions && unions.length">
      <thead>
        <tr>
          <th>联盟名称</th>
          <th>操作</th>
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
              <button @click="handleUpdateUnion(union.id)">保存</button>
              <button class="secondary-btn" @click="cancelEdit">取消</button>
            </div>
            <div v-else>
              <button @click="startEdit(union)">编辑</button>
              <button class="delete-btn" @click="handleDeleteUnion(union.id)">删除</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else>
      <p>暂无联盟，请先添加一个。</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { getUnions, addUnion, updateUnion, deleteUnion } from '../services/unionService';

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
    alert('联盟名称不能为空。');
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
    alert('联盟名称不能为空。');
    return;
  }
  updateUnionMutation.mutate({ id, name: editingUnionName.value.trim() });
};

const handleDeleteUnion = (id) => {
  if (confirm('确定要删除这个联盟吗？此操作将一并删除关联的玩家数据。')) {
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
