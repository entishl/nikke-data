<template>
  <div class="union-management">
    <h2>联盟管理</h2>
    
    <div class="add-union">
      <input type="text" v-model="newUnionName" placeholder="输入新联盟名称" />
      <button @click="addUnion">添加联盟</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>联盟名称</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="union in unions" :key="union.id">
          <td>
            <input v-if="editingUnionId === union.id" v-model="editingUnionName" />
            <span v-else>{{ union.name }}</span>
          </td>
          <td>
            <div v-if="editingUnionId === union.id">
              <button @click="updateUnion(union.id)">保存</button>
              <button @click="cancelEdit" class="secondary-btn">取消</button>
            </div>
            <div v-else>
              <button @click="startEdit(union)">编辑</button>
              <button @click="deleteUnion(union.id)" class="delete-btn">删除</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, defineEmits } from 'vue';
import axios from 'axios';

const unions = ref([]);
const newUnionName = ref('');
const editingUnionId = ref(null);
const editingUnionName = ref('');

const emit = defineEmits(['unions-updated']);

const fetchUnions = async () => {
  try {
    const response = await axios.get('/api/unions/');
    unions.value = response.data;
  } catch (error) {
    console.error('获取联盟列表失败:', error);
    alert('获取联盟列表失败。');
  }
};

const addUnion = async () => {
  if (!newUnionName.value.trim()) {
    alert('联盟名称不能为空。');
    return;
  }
  try {
    await axios.post('/api/unions/', null, { params: { name: newUnionName.value } });
    newUnionName.value = '';
    await fetchUnions();
    emit('unions-updated');
  } catch (error) {
    console.error('添加联盟失败:', error);
    alert('添加联盟失败。');
  }
};

const startEdit = (union) => {
  editingUnionId.value = union.id;
  editingUnionName.value = union.name;
};

const cancelEdit = () => {
  editingUnionId.value = null;
  editingUnionName.value = '';
};

const updateUnion = async (id) => {
  if (!editingUnionName.value.trim()) {
    alert('联盟名称不能为空。');
    return;
  }
  try {
    await axios.put(`/api/unions/${id}`, null, { params: { name: editingUnionName.value } });
    cancelEdit();
    await fetchUnions();
    emit('unions-updated');
  } catch (error) {
    console.error('更新联盟失败:', error);
    alert('更新联盟失败。');
  }
};

const deleteUnion = async (id) => {
  if (confirm('确定要删除这个联盟吗？')) {
    try {
      await axios.delete(`/api/unions/${id}`);
      await fetchUnions();
      emit('unions-updated');
    } catch (error) {
      console.error('删除联盟失败:', error);
      alert(`删除联盟失败: ${error.response?.data?.detail || '未知错误'}`);
    }
  }
};

onMounted(fetchUnions);
</script>

<style scoped>
.union-management {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
.secondary-btn {
  background-color: #6c757d;
  margin-left: 5px;
}
.delete-btn {
  background-color: #ff4d4f;
  margin-left: 5px;
}
</style>