<template>
  <div class="player-management-section">
    <h2>玩家管理</h2>
    <table>
      <thead>
        <tr>
          <th @click="sortBy('name')">玩家名</th>
          <th @click="sortBy('synchro_level')">同步器等级</th>
          <th @click="sortBy('resilience_cube_level')">遗迹巨熊魔方</th>
          <th @click="sortBy('bastion_cube_level')">战术巨熊魔方</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="player in players" :key="player.id">
          <td>{{ player.name }}</td>
          <td>{{ player.synchro_level }}</td>
          <td>{{ player.resilience_cube_level }}</td>
          <td>{{ player.bastion_cube_level }}</td>
          <td>
            <button @click="deletePlayer(player.name)" class="delete-btn">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const players = ref([]);
const sortKey = ref('name');
const sortOrder = ref('asc');

const fetchPlayers = async () => {
  try {
    const response = await axios.get('/api/players/', {
      params: {
        sort_by: sortKey.value,
        order: sortOrder.value,
      },
    });
    players.value = response.data;
  } catch (error) {
    console.error('获取玩家列表失败:', error);
  }
};

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'desc';
  }
  fetchPlayers();
};

const deletePlayer = async (playerName) => {
  if (confirm(`确定要删除玩家 "${playerName}" 的所有数据吗？此操作不可逆！`)) {
    try {
      await axios.delete(`/api/players/${playerName}`);
      alert(`玩家 "${playerName}" 的数据已成功删除。`);
      fetchPlayers(); // Refresh the list
    } catch (error) {
      alert(`删除玩家 "${playerName}" 的数据时出错。`);
      console.error(`Error deleting player ${playerName}:`, error);
    }
  }
};

onMounted(() => {
  fetchPlayers();
});
</script>

<style scoped>
.player-management-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  cursor: pointer;
}

.delete-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}
</style>