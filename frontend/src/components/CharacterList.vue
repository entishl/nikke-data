<template>
  <div class="character-section">
    <h2>角色总表</h2>
    <div class="main-layout">
      <div class="sidebar">
        <h4>按联盟筛选</h4>
        <div v-for="union in unions" :key="union.id" class="player-filter-item">
          <input
            type="checkbox"
            :id="'union-' + union.id"
            :value="union.id"
            v-model="selectedUnionIds"
          />
          <label :for="'union-' + union.id">{{ union.name }}</label>
        </div>

        <h4 style="margin-top: 20px;">按玩家筛选</h4>
        <div class="sidebar-actions">
          <button @click="selectAllPlayers">全选</button>
          <button @click="clearSelection">清空</button>
        </div>
        <div v-for="player in players" :key="player.id" class="player-filter-item">
          <input
            type="checkbox"
            :id="'player-' + player.id"
            :value="player.name"
            v-model="selectedPlayers"
          />
          <label :for="'player-' + player.id">
            {{ player.name }} (Lvl: {{ player.synchro_level }})
          </label>
        </div>
      </div>
      <div class="content">
        <div class="filters">
          <input type="text" v-model="characterNameFilter" placeholder="按角色名筛选" />
          
          <!-- New Filters -->
          <select v-model="classFilter">
            <option value="">所有职业</option>
            <option v-for="c in filterOptions.class" :key="c" :value="c">{{ c }}</option>
          </select>
          <select v-model="elementFilter">
            <option value="">所有属性</option>
            <option v-for="e in filterOptions.element" :key="e" :value="e">{{ e }}</option>
          </select>
          <select v-model="weaponTypeFilter">
            <option value="">所有武器</option>
            <option v-for="wt in filterOptions.weapon_type" :key="wt" :value="wt">{{ wt }}</option>
          </select>
          <select v-model="burstSkillFilter">
            <option value="">所有爆裂</option>
            <option v-for="bs in filterOptions.use_burst_skill" :key="bs" :value="bs">{{ bs }}</option>
          </select>

          <button @click="resetFilters" class="secondary-btn">重置</button>
          <label class="superiority-toggle">
            <input type="checkbox" v-model="showTotalSuperiority">
            显示总优越
          </label>
        </div>
        
        <table>
      <thead>
        <tr>
          <th @click="sortBy('name_cn')">角色名</th>
          <th @click="sortBy('player_name')">玩家</th>
          <th @click="sortBy('core')">核心</th>
          <th @click="sortBy('skill1_level')">技能1</th>
          <th @click="sortBy('skill2_level')">技能2</th>
          <th @click="sortBy('skill_burst_level')">爆发</th>
          <th @click="sortBy('item_level')">收藏品</th>
          <th @click="sortBy('total_stat_atk')">攻击力</th>
          <th @click="sortBy(superioritySortKey)">优越</th>
          <th @click="sortBy('total_stat_ammo_load')">弹夹</th>
          <th @click="sortBy('relative_training_degree')">相对练度</th>
          <th @click="sortBy('absolute_training_degree')">绝对练度</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="char in characters" :key="char.id">
          <td>{{ char.name_cn }}</td>
          <td>{{ char.player_name }}</td>
          <td>{{ formatGradeAndCore(char) }}</td>
          <td>{{ char.skill1_level }}</td>
          <td>{{ char.skill2_level }}</td>
          <td>{{ char.skill_burst_level }}</td>
          <td>{{ formatItem(char) }}</td>
          <td>{{ char.total_stat_atk.toFixed(2) }}</td>
          <td>{{ (showTotalSuperiority ? char.total_superiority : char.total_inc_element_dmg).toFixed(2) }}</td>
          <td>{{ char.total_stat_ammo_load.toFixed(2) }}</td>
          <td>{{ char.relative_training_degree.toFixed(4) }}</td>
          <td>{{ formatKilo(char.absolute_training_degree) }}</td>
          <td>
            <button @click="showDetails(char.id)">详情</button>
            <button @click="deletePlayer(char.player_name)" class="delete-btn">删除</button>
          </td>
        </tr>
      </tbody>
        </table>
      </div>
    </div>
  </div>

  <CharacterDetailsModal
    v-if="isModalVisible"
    :character="characterToShowInModal"
    :visible="isModalVisible"
    @close="isModalVisible = false"
  />
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import CharacterDetailsModal from './CharacterDetailsModal.vue';
import { formatGradeAndCore, formatItem, formatKilo } from '../utils.js';
import { useUnionStore } from '../stores/unionStore';
import { storeToRefs } from 'pinia';

const unionStore = useUnionStore();
const { unions } = storeToRefs(unionStore);

const allCharacters = ref([]); // Store all characters fetched from the backend
const characters = computed(() => filteredAndSortedCharacters.value); // This will be the computed property for display

const characterNameFilter = ref('');
const players = ref([]);
const selectedPlayers = ref([]);
const selectedUnionIds = ref([]); // Changed from selectedUnionId

// Filter refs
const classFilter = ref('');
const elementFilter = ref('');
const weaponTypeFilter = ref('');
const burstSkillFilter = ref('');
const filterOptions = ref({
  class: [],
  element: [],
  weapon_type: [],
  use_burst_skill: [],
});

const showTotalSuperiority = ref(false);
const superioritySortKey = computed(() => showTotalSuperiority.value ? 'total_superiority' : 'total_inc_element_dmg');

const sortKey = ref('absolute_training_degree');
const sortOrder = ref('desc');
const isModalVisible = ref(false);
const characterToShowInModal = ref(null);

const fetchCharacters = async () => {
  try {
    const params = {};
    if (selectedUnionIds.value.length > 0) {
      params.union_ids = selectedUnionIds.value.join(',');
    }
    const response = await axios.get('/api/characters/', { params });
    allCharacters.value = response.data;
  } catch (error) {
    console.error('获取角色列表失败:', error);
  }
};

const filteredAndSortedCharacters = computed(() => {
  let result = [...allCharacters.value];

  // 1. Filtering
  if (selectedPlayers.value.length > 0) {
    result = result.filter(c => selectedPlayers.value.includes(c.player_name));
  }
  if (characterNameFilter.value) {
    result = result.filter(c => c.name_cn.toLowerCase().includes(characterNameFilter.value.toLowerCase()));
  }
  if (classFilter.value) {
    result = result.filter(c => c.class === classFilter.value);
  }
  if (elementFilter.value) {
    result = result.filter(c => c.element === elementFilter.value);
  }
  if (weaponTypeFilter.value) {
    result = result.filter(c => c.weapon_type === weaponTypeFilter.value);
  }
  if (burstSkillFilter.value) {
    result = result.filter(c => c.use_burst_skill === burstSkillFilter.value);
  }

  // 2. Sorting
  const key = sortKey.value;
  const order = sortOrder.value;
  
  if (key) {
    result.sort((a, b) => {
      let valA = a[key];
      let valB = b[key];

      // Handle nested properties for superiority
      if (key === 'total_superiority' || key === 'total_inc_element_dmg') {
        valA = a[superioritySortKey.value];
        valB = b[superioritySortKey.value];
      }

      if (valA < valB) return order === 'asc' ? -1 : 1;
      if (valA > valB) return order === 'asc' ? 1 : -1;
      return 0;
    });
  }

  return result;
});


const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'desc';
  }
  // No need to call fetchCharacters() anymore
};

const showDetails = async (id) => {
  try {
    const response = await axios.get(`/api/characters/${id}`);
    characterToShowInModal.value = response.data;
    isModalVisible.value = true;
  } catch (error) {
    console.error('获取角色详情失败:', error);
  }
};

const fetchFilterOptions = async () => {
  try {
    const response = await axios.get('/api/filter-options');
    filterOptions.value = response.data;
  } catch (error) {
    console.error('获取筛选选项失败:', error);
  }
};

const resetFilters = () => {
  characterNameFilter.value = '';
  selectedPlayers.value = [];
  classFilter.value = '';
  elementFilter.value = '';
  weaponTypeFilter.value = '';
  burstSkillFilter.value = '';
  // No need to call fetchCharacters() anymore
};

const fetchPlayers = async () => {
  try {
    const params = {
      sort_by: 'synchro_level',
      order: 'desc',
    };
    if (selectedUnionIds.value.length > 0) {
      params.union_ids = selectedUnionIds.value.join(',');
    }
    const response = await axios.get('/api/players/', { params });
    players.value = response.data;
  } catch (error) {
    console.error('获取玩家列表失败:', error);
  }
};

watch(selectedUnionIds, () => {
  fetchPlayers();
  fetchCharacters();
  selectedPlayers.value = []; // Clear player selection when union changes
});

watch(selectedPlayers, () => {
  // This watcher is now less critical since filtering is client-side,
  // but can be kept for immediate reactivity if needed, or removed.
});

const selectAllPlayers = () => {
  selectedPlayers.value = players.value.map(p => p.name);
  // No need to call fetchCharacters() anymore
};

const clearSelection = () => {
  selectedPlayers.value = [];
  // No need to call fetchCharacters() anymore
};

onMounted(() => {
  fetchFilterOptions();
  fetchPlayers();
  fetchCharacters();
});

const deletePlayer = async (playerName) => {
  if (confirm(`确定要删除玩家 "${playerName}" 的所有数据吗？此操作不可逆！`)) {
    try {
      await axios.delete(`/api/players/${playerName}`);
      alert(`玩家 "${playerName}" 的数据已成功删除。`);
      fetchCharacters(); // Re-fetch all data to refresh the list
    } catch (error) {
      alert(`删除玩家 "${playerName}" 的数据时出错。`);
      console.error(`Error deleting player ${playerName}:`, error);
    }
  }
};

</script>

<style scoped>
.character-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.main-layout {
  display: flex;
  gap: 20px;
}

.sidebar {
  width: 250px;
  flex-shrink: 0;
  background: #f2f2f2;
  padding: 15px;
  border-radius: 8px;
}

.sidebar h4 {
  margin-top: 0;
  margin-bottom: 15px;
  border-bottom: 2px solid #ddd;
  padding-bottom: 10px;
}

.sidebar-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.sidebar-actions button {
  flex-grow: 1;
}

.sidebar-actions button:first-child {
  margin-right: 5px;
}

.sidebar-actions button:last-child {
  margin-left: 5px;
}

.player-filter-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.player-filter-item input {
  margin-right: 10px;
}

.player-filter-item label {
  cursor: pointer;
}

.content {
  flex-grow: 1;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
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

.secondary-btn {
  background-color: #6c757d;
}

.delete-btn {
  background-color: #ff4d4f;
  margin-left: 5px;
}
</style>