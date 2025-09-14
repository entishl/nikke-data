<template>
  <div class="fire-container">
    <h2>燃烧 - 角色练度总览</h2>

    <div class="controls">
      <label>
        <input type="checkbox" v-model="showRelativeDegree" />
        切换为{{ showRelativeDegree ? '绝对练度' : '相对练度' }}
      </label>
    </div>

    <div v-if="loading" class="loading">正在加载数据...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!loading && !error" class="table-container">
      <table>
        <thead>
          <tr>
            <th>玩家</th>
            <th v-for="char in fireCharacterHeaders" :key="char.id" @click="handleSort(char.id)" class="sortable">
              {{ char.name_cn }}
              <span v-if="sortColumnId === char.id">{{ sortDirection === 'desc' ? '▼' : '▲' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="player in sortedPlayers" :key="player.id">
            <td>{{ player.name }}</td>
            <td v-for="headerChar in fireCharacterHeaders" :key="headerChar.id">
              {{ getFormattedDegree(player.name, headerChar.id) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { formatKilo } from '../utils.js';

const loading = ref(true);
const error = ref(null);
const players = ref([]);
const uniqueCharacters = ref([]);
const characterData = ref([]);
const showRelativeDegree = ref(false);

// Sorting state
const sortColumnId = ref(null);
const sortDirection = ref('desc');

const degreeType = computed(() => showRelativeDegree.value ? 'relative_training_degree' : 'absolute_training_degree');

// Fetch all necessary data on component mount
onMounted(async () => {
  try {
    const [playersRes, uniqueCharsRes, charDataRes] = await Promise.all([
      axios.get('/api/players/'),
      axios.get('/api/characters/all-unique'),
      axios.get('/api/characters/?element=Fire')
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

// Filter unique characters to get only fire characters that are also marked as is_C
const fireCharacterHeaders = computed(() => {
  const fireCharsFromData = new Set(characterData.value.filter(c => c.is_C).map(c => c.character_id));
  return uniqueCharacters.value.filter(char =>
    char.element === 'Fire' && fireCharsFromData.has(char.id)
  ).sort((a, b) => a.id - b.id);
});

// Function to get the raw degree value for sorting
const getRawDegree = (playerName, characterId) => {
  const playerMap = characterDataMap.value.get(playerName);
  if (playerMap && playerMap.has(characterId)) {
    const char = playerMap.get(characterId);
    return char[degreeType.value] || -1; // Return -1 for sorting if degree is null/0
  }
  return -1; // Return -1 for sorting if character not found
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

// Sorting handler
const handleSort = (characterId) => {
  if (sortColumnId.value === characterId) {
    sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc';
  } else {
    sortColumnId.value = characterId;
    sortDirection.value = 'desc';
  }
};

// Computed property for sorted players
const sortedPlayers = computed(() => {
  if (!sortColumnId.value) {
    return players.value;
  }
  return [...players.value].sort((a, b) => {
    const degreeA = getRawDegree(a.name, sortColumnId.value);
    const degreeB = getRawDegree(b.name, sortColumnId.value);

    if (sortDirection.value === 'desc') {
      return degreeB - degreeA;
    } else {
      return degreeA - degreeB;
    }
  });
});

</script>

<style scoped>
.fire-container {
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
  background-color: #42b983;
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
</style>