<template>
  <div class="water-container">
    <h2>水冷 - 角色练度总览</h2>

    <div class="controls">
      <div class="control-group">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span>相对练度</span>
          <label class="switch">
            <input type="checkbox" v-model="showRelativeDegree">
            <span class="slider round"></span>
          </label>
          <span>绝对练度</span>
        </div>
      </div>
      <div class="control-group">
        <label>
          <input type="checkbox" v-model="showDetails" />
          显示详情
        </label>
      </div>
      <div class="control-group">
        <h4>按联盟筛选</h4>
        <div class="filter-items-container">
          <div v-for="union in unions" :key="union.id" class="filter-item">
            <input
              type="checkbox"
              :id="'union-water-' + union.id"
              :value="union.id"
              v-model="selectedUnionIds"
            />
            <label :for="'union-water-' + union.id">{{ union.name }}</label>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">正在加载数据...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!loading && !error" class="table-container">
      <table>
        <thead>
          <tr v-if="!showDetails">
            <th>玩家</th>
            <th v-for="char in waterCharacterHeaders" :key="char.id" @click="handleSort(String(char.id))" class="sortable">
              {{ char.name_cn }}
              <span v-if="sortKey === String(char.id)">{{ sortDirection === 'desc' ? '▼' : '▲' }}</span>
            </th>
          </tr>
          <template v-else>
            <tr>
              <th rowspan="2" class="player-header">玩家</th>
              <th v-for="char in waterCharacterHeaders" :key="char.id" :colspan="detailAttributes.length" class="character-header">
                {{ char.name_cn }}
              </th>
            </tr>
            <tr>
              <template v-for="char in waterCharacterHeaders" :key="char.id + '-details'">
                <th v-for="attr in detailAttributes" :key="attr.key" class="detail-header sortable" @click="handleSort(`${char.id}:${attr.raw_key || attr.key}`)">
                  {{ attr.label }}
                  <span v-if="sortKey === `${char.id}:${attr.raw_key || attr.key}`">{{ sortDirection === 'desc' ? '▼' : '▲' }}</span>
                </th>
              </template>
            </tr>
          </template>
        </thead>
        <tbody>
          <tr v-for="player in sortedPlayers" :key="player.id">
            <td>{{ player.name }}</td>
            <template v-if="!showDetails">
              <td v-for="headerChar in waterCharacterHeaders" :key="headerChar.id">
                {{ getFormattedDegree(player.name, headerChar.id) }}
              </td>
            </template>
            <template v-else>
              <template v-for="headerChar in waterCharacterHeaders" :key="headerChar.id + '-details-body'">
                <template v-if="getCharacterDetails(player.name, headerChar.id)">
                  <td v-for="attr in detailAttributes" :key="attr.key">
                    {{ getCharacterDetails(player.name, headerChar.id)[attr.key] }}
                  </td>
                </template>
                <template v-else>
                  <td v-for="attr in detailAttributes" :key="attr.key" :colspan="1">
                    -
                  </td>
                </template>
              </template>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import { formatKilo, formatGradeAndCore, formatItem } from '../utils.js';

const loading = ref(true);
const error = ref(null);
const players = ref([]);
const uniqueCharacters = ref([]);
const characterData = ref([]);
const showRelativeDegree = ref(false);
const showDetails = ref(false);
const unions = ref([]);
const selectedUnionIds = ref([]);

// Sorting state
const sortKey = ref(null);
const sortDirection = ref('desc');

const degreeType = computed(() => showRelativeDegree.value ? 'absolute_training_degree' : 'relative_training_degree');

const detailAttributes = [
  { key: 'core', label: '核心', raw_key: 'core' },
  { key: 'skill1', label: '技能1', raw_key: 'skill1_level' },
  { key: 'skill2', label: '技能2', raw_key: 'skill2_level' },
  { key: 'burst', label: '爆发', raw_key: 'skill_burst_level' },
  { key: 'item', label: '收藏品', raw_key: 'item_level' },
  { key: 'atk', label: '攻击', raw_key: 'total_stat_atk' },
  { key: 'superiority', label: '优越', raw_key: 'total_inc_element_dmg' },
  { key: 'ammo', label: '弹夹', raw_key: 'total_stat_ammo_load' },
  { key: 'relative_degree', label: '相对练度', raw_key: 'relative_training_degree' },
  { key: 'absolute_degree', label: '绝对练度', raw_key: 'absolute_training_degree' },
];

// Fetch all necessary data on component mount
const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const params = {};
    if (selectedUnionIds.value.length > 0) {
      params.union_ids = selectedUnionIds.value.join(',');
    }

    const [playersRes, uniqueCharsRes, charDataRes] = await Promise.all([
      axios.get('/api/players/', { params }),
      axios.get('/api/characters/all-unique'), // This does not need filtering
      axios.get('/api/characters/', { params: { ...params, element: 'Water' } })
    ]);
    players.value = playersRes.data;
    uniqueCharacters.value = uniqueCharsRes.data;
    characterData.value = charDataRes.data;
  } catch (e) {
    error.value = '无法加载数据，请检查后端服务是否正常。';
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const fetchUnions = async () => {
  try {
    const response = await axios.get('/api/unions/');
    unions.value = response.data;
  } catch (error) {
    console.error('获取联盟列表失败:', error);
  }
};

onMounted(() => {
  fetchUnions();
  fetchData();
});

watch(selectedUnionIds, () => {
  fetchData();
});

// Create a map for quick lookup of character data
const characterDataMap = computed(() => {
  const map = new Map();
  for (const char of characterData.value) {
    if (!map.has(char.player_name)) {
      map.set(char.player_name, new Map());
    }
    map.get(char.player_name).set(char.character_id, char);
  }
  return map;
});

// Filter unique characters to get only water characters that are also marked as is_C
const waterCharacterHeaders = computed(() => {
  const waterCharsFromData = new Set(characterData.value.filter(c => c.is_C).map(c => c.character_id));
  return uniqueCharacters.value.filter(char =>
    char.element === 'Water' && waterCharsFromData.has(char.id)
  ).sort((a, b) => a.id - b.id);
});

// Function to get the raw value for sorting, works for both modes
const getRawValue = (playerName, key) => {
  if (!key) return -1;

  const playerMap = characterDataMap.value.get(playerName);
  if (!playerMap) return -1;

  const [characterId, attributeKey] = key.split(':');
  const charId = parseInt(characterId);

  if (!playerMap.has(charId)) return -1;
  const char = playerMap.get(charId);

  if (attributeKey) {
    // Detail view sorting
    if (attributeKey === 'core') {
      return (char.limit_break_grade || 0) * 10 + (char.core || 0);
    }
    return char[attributeKey] || -1;
  } else {
    // Simple view sorting (by training degree)
    return char[degreeType.value] || -1;
  }
};

// Function to get the formatted degree for display
const getFormattedDegree = (playerName, characterId) => {
  const playerMap = characterDataMap.value.get(playerName);
  if (playerMap && playerMap.has(characterId)) {
    const char = playerMap.get(characterId);
    const degree = char[degreeType.value];
    if (!degree) return '-';

    if (degreeType.value === 'absolute_training_degree') {
      return formatKilo(degree);
    }
    return degree.toFixed(2);
  }
  return '-';
};

const getCharacterDetails = (playerName, characterId) => {
  const playerMap = characterDataMap.value.get(playerName);
  if (playerMap && playerMap.has(characterId)) {
    const char = playerMap.get(characterId);
    return {
      core: formatGradeAndCore(char),
      skill1: char.skill1_level,
      skill2: char.skill2_level,
      burst: char.skill_burst_level,
      item: formatItem(char),
      atk: char.total_stat_atk.toFixed(0),
      superiority: char.total_inc_element_dmg.toFixed(2),
      ammo: char.total_stat_ammo_load.toFixed(2),
      relative_degree: char.relative_training_degree.toFixed(4),
      absolute_degree: formatKilo(char.absolute_training_degree),
    };
  }
  return null;
};

// Sorting handler
const handleSort = (key) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc';
  } else {
    sortKey.value = key;
    sortDirection.value = 'desc';
  }
};

// Computed property for sorted players
const sortedPlayers = computed(() => {
  if (!sortKey.value) {
    return players.value;
  }
  return [...players.value].sort((a, b) => {
    const valueA = getRawValue(a.name, sortKey.value);
    const valueB = getRawValue(b.name, sortKey.value);

    if (sortDirection.value === 'desc') {
      return valueB - valueA;
    } else {
      return valueA - valueB;
    }
  });
});

</script>

<style scoped>
.water-container {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.sortable {
  cursor: pointer;
}

.sortable:hover {
  background-color: #e0e0e0;
}

.controls {
  margin-bottom: 20px;
  display: flex;
  gap: 30px;
  align-items: flex-start;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-group h4 {
  margin: 0 0 5px 0;
}

.filter-items-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-item {
  display: inline-flex;
  align-items: center;
}

.controls label {
  font-size: 16px;
  cursor: pointer;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}

.error {
  color: #ff4d4f;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: center;
}

th {
  background-color: #409EFF;
  color: white;
  position: relative;
}

th span {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
}

tbody tr:nth-child(even) {
  background-color: #f2f2f2;
}
.character-header, .detail-header, .player-header {
  position: sticky;
  top: 0;
  z-index: 2;
}

.character-header {
  background-color: #337ecc; /* A slightly darker blue */
}

.detail-header {
  background-color: #409EFF;
  top: 38px; /* Adjust based on the height of the character header row */
}

.player-header {
  left: 0;
  z-index: 3;
}

tbody td, tbody th {
  position: relative;
}

tbody th {
  left: 0;
  z-index: 1;
  background-color: #f9f9f9;
}
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #409EFF;
}

input:focus + .slider {
  box-shadow: 0 0 1px #409EFF;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>