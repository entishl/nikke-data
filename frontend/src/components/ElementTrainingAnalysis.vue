<template>
  <div class="element-training-analysis">
    <h1>元素练度分析</h1>

    <div class="controls">
      <!-- Union Filter -->
      <div class="control-group">
        <label for="union-select">联盟:</label>
        <select id="union-select" v-model="selectedUnions" multiple>
          <option v-for="union in unions" :key="union.id" :value="union.id">{{ union.name }}</option>
        </select>
      </div>

      <!-- Training Type Switch -->
      <div class="control-group">
        <label>类:</label>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span>相对练度</span>
          <label class="switch">
            <input type="checkbox" v-model="showAbsoluteDegree">
            <span class="slider round"></span>
          </label>
          <span>绝对练度</span>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- Character Selector -->
      <div class="character-selector">
        <h2>选择角色(仅限C)</h2>
        <div v-for="(group, element) in groupedCharacters" :key="element">
          <h3>{{ element }}</h3>
          <div v-for="char in group" :key="char.id" class="character-item">
            <input type="checkbox" :id="'char-' + char.id" :value="char.id" v-model="selectedCharacters">
            <label :for="'char-' + char.id">{{ char.name_cn }}</label>
            <input type="number" v-model.number="coefficients[char.id]" min="0" step="0.1" placeholder="系数" :disabled="!selectedCharacters.includes(char.id)">
          </div>
        </div>
      </div>

      <!-- Results Table -->
      <div class="results-table">
        <h2>结果</h2>
        <table>
          <thead>
            <tr>
              <th @click="sortBy('player_name')">
                玩家
                <span v-if="sortKey === 'player_name'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('Fire')" class="fire-header">
                燃烧
                <span v-if="sortKey === 'Fire'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('Water')" class="water-header">
                水冷
                <span v-if="sortKey === 'Water'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('Wind')" class="wind-header">
                风压
                <span v-if="sortKey === 'Wind'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('Electronic')" class="electronic-header">
                电击
                <span v-if="sortKey === 'Electronic'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </th>
              <th @click="sortBy('Iron')" class="iron-header">
                铁甲
                <span v-if="sortKey === 'Iron'">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="player in sortedAnalysisResults" :key="player.player_name">
              <td>{{ player.player_name }}</td>
              <td :class="getCellClass(player, 'Fire')">{{ formatElementValue(player.elements.Fire) }}</td>
              <td :class="getCellClass(player, 'Water')">{{ formatElementValue(player.elements.Water) }}</td>
              <td :class="getCellClass(player, 'Wind')">{{ formatElementValue(player.elements.Wind) }}</td>
              <td :class="getCellClass(player, 'Electronic')">{{ formatElementValue(player.elements.Electronic) }}</td>
              <td :class="getCellClass(player, 'Iron')">{{ formatElementValue(player.elements.Iron) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { formatKilo } from '../utils.js';

export default {
  name: 'ElementTrainingAnalysis',
  setup() {
    const unions = ref([]);
    const selectedUnions = ref([]);
    const showAbsoluteDegree = ref(false);
    const trainingType = computed(() => showAbsoluteDegree.value ? 'absolute_training_degree' : 'relative_training_degree');
    const characters = ref([]);
    const selectedCharacters = ref([]);
    const coefficients = ref({});
    const analysisResults = ref([]);
    const sortKey = ref('');
    const sortOrder = ref('asc');

    const fetchUnions = async () => {
      try {
        const response = await axios.get('/api/unions/');
        unions.value = response.data;
      } catch (error) {
        console.error('Error fetching unions:', error);
      }
    };

    const fetchCharacters = async () => {
      try {
        const response = await axios.get(`/api/characters/?_t=${new Date().getTime()}`);
        const allCharacters = response.data;
        
        const uniqueCharacters = [];
        const seenIds = new Set();
        
        for (const char of allCharacters) {
          if (char.is_C && !seenIds.has(char.character_id)) {
            uniqueCharacters.push({
              id: char.character_id,
              name_cn: char.name_cn,
              element: char.element, // Keep element for grouping
            });
            seenIds.add(char.character_id);
          }
        }
        
        characters.value = uniqueCharacters.sort((a, b) => a.id - b.id);
        
        // Default select all characters
        selectedCharacters.value = characters.value.map(char => char.id);

        // Initialize coefficients
        characters.value.forEach(char => {
            coefficients.value[char.id] = 1;
        });

      } catch (error) {
        console.error('Error fetching characters:', error);
      }
    };

    const performAnalysis = async () => {
      if (selectedCharacters.value.length === 0) {
        analysisResults.value = [];
        return;
      }

      const characterCoefficients = {};
      selectedCharacters.value.forEach(id => {
        characterCoefficients[id] = coefficients.value[id] || 1;
      });

      const formData = new FormData();
      if (selectedUnions.value.length > 0) {
          formData.append('union_ids', selectedUnions.value.join(','));
      }
      formData.append('character_coefficients', JSON.stringify(characterCoefficients));
      formData.append('training_type', trainingType.value);

      try {
        const response = await axios.post('/api/element-training-analysis/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        analysisResults.value = response.data;
      } catch (error) {
        console.error('Error performing analysis:', error);
      }
    };

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
      } else {
        sortKey.value = key;
        sortOrder.value = 'asc';
      }
    };

    const sortedAnalysisResults = computed(() => {
      if (!sortKey.value) {
        return analysisResults.value;
      }

      return [...analysisResults.value].sort((a, b) => {
        let aValue, bValue;

        if (sortKey.value === 'player_name') {
          aValue = a.player_name;
          bValue = b.player_name;
        } else {
          aValue = a.elements[sortKey.value];
          bValue = b.elements[sortKey.value];
        }

        if (aValue < bValue) {
          return sortOrder.value === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortOrder.value === 'asc' ? 1 : -1;
        }
        return 0;
      });
    });

    const groupedCharacters = computed(() => {
      return characters.value.reduce((groups, char) => {
        const element = char.element || 'Unknown';
        if (!groups[element]) {
          groups[element] = [];
        }
        groups[element].push(char);
        return groups;
      }, {});
    });

    onMounted(() => {
      fetchUnions();
      fetchCharacters();
    });

    watch([selectedUnions, selectedCharacters, trainingType, coefficients], performAnalysis, { deep: true });

    const formatElementValue = (value) => {
      if (trainingType.value === 'absolute_training_degree') {
        return formatKilo(value);
      }
      return value.toFixed(2);
    };

    const getCellClass = (player, element) => {
      const topElements = getTopElements(player);
      if (topElements.includes(element)) {
        return `${element.toLowerCase()}-highlight`;
      }
      return '';
    };

    const getTopElements = (player) => {
      const elements = player.elements;
      const sortedElements = Object.entries(elements)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 3)
        .map(([name]) => name);
      return sortedElements;
    };

    return {
      unions,
      selectedUnions,
      showAbsoluteDegree,
      trainingType,
      characters,
      selectedCharacters,
      coefficients,
      analysisResults,
      groupedCharacters,
      formatElementValue,
      getCellClass,
      sortedAnalysisResults,
      sortBy,
      sortKey,
      sortOrder,
    };
  },
};
</script>

<style scoped>
.element-training-analysis {
  padding: 20px;
}

.controls {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.character-selector {
  width: 300px;
  border: 1px solid #ccc;
  padding: 10px;
  height: 500px;
  overflow-y: auto;
}

.character-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.character-item input[type="number"] {
    width: 60px;
    margin-left: auto;
}

.results-table {
  flex-grow: 1;
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

th span {
  float: right;
}

.fire-header { background-color: #f44336; color: white; }
.water-header { background-color: #2196F3; color: white; }
.wind-header { background-color: #4CAF50; color: white; }
.electronic-header { background-color: #9C27B0; color: white; }
.iron-header { background-color: #FFEB3B; color: black; }

.fire-highlight { background-color: #f44336; color: white; }
.water-highlight { background-color: #2196F3; color: white; }
.wind-highlight { background-color: #4CAF50; color: white; }
.electronic-highlight { background-color: #9C27B0; color: white; }
.iron-highlight { background-color: #FFEB3B; color: black; }

button.active {
  background-color: #4CAF50;
  color: white;
}
button.active {
  background-color: #4CAF50;
  color: white;
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
  background-color: #4CAF50;
}

input:focus + .slider {
  box-shadow: 0 0 1px #4CAF50;
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