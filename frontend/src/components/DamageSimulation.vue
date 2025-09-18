<template>
  <div class="damage-simulation-container">
    <h2>伤害模拟</h2>
    <div class="main-layout">
      <div class="control-panel">
        <h3>控制面板</h3>
        <div class="selectors">
          <select v-model="selectedUnionId">
            <option :value="null">选择联盟</option>
            <option v-for="union in unions" :key="union.id" :value="union.id">{{ union.name }}</option>
          </select>
          <select v-model="selectedBasePlayerId" :disabled="!selectedUnionId">
            <option :value="null">选择基准玩家</option>
            <option v-for="player in players" :key="player.id" :value="player.id">{{ player.name }}</option>
          </select>
        </div>
        <div class="coor-level-input">
          <label for="coor-level">企业等级:</label>
          <input type="number" id="coor-level" v-model.number="coor_level" />
        </div>

        <div class="team-tabs">
          <button
            v-for="element in elements"
            :key="element"
            @click="activeElementTab = element"
            :class="['tab-' + element.toLowerCase(), { active: activeElementTab === element }]"
          >
            {{ element }}
          </button>
        </div>

        <div class="team-input-table">
          <h4>{{ activeElementTab }} 队</h4>
          <table>
            <thead>
              <tr>
                <th>角色ID</th>
                <th>伤害</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(character, index) in teams[activeElementTab]" :key="index">
                <td>
                  <select v-model.number="character.character_id">
                    <option :value="null">选择角色</option>
                    <option v-for="char in allCharacters" :key="char.id" :value="char.id">
                      {{ char.name_cn }}
                    </option>
                  </select>
                </td>
                <td>
                  <input
                    type="text"
                    :value="character.damage_display"
                    @input="onDamageInput($event, character)"
                    @blur="onDamageBlur(character)"
                    placeholder="输入伤害"
                    style="text-align: right;"
                  />
                </td>
                <td><button @click="removeCharacter(activeElementTab, index)" class="delete-btn-small">删除</button></td>
              </tr>
            </tbody>
          </table>
          <button @click="addCharacter(activeElementTab)">添加角色</button>
        </div>
        <div class="simulation-controls">
          <button @click="startSimulation" class="start-simulation-btn">开始模拟</button>
        </div>
      </div>
      <div class="results-panel">
        <h3>模拟结果</h3>
        <div v-if="isLoading">
          <p>正在计算，请稍候...</p>
        </div>
        <div v-else-if="error" class="error-message">
          <p>{{ error }}</p>
        </div>
        <div v-else-if="simulationResults.length > 0" class="results-table">
          <table>
            <thead>
              <tr>
                <th>玩家名称</th>
                <th v-for="element in elements" :key="element">{{ element }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in simulationResults" :key="result.player_id">
                <td>{{ result.player_name }}</td>
                <td
                  v-for="element in elements"
                  :key="element"
                  @click="showTeamDetails(result.team_damages[element])"
                  class="clickable-cell"
                >
                  {{ formatDamage(result.team_damages[element]?.total_damage) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else>
          <p>暂无模拟结果。请在左侧输入数据并点击“开始模拟”。</p>
        </div>
      </div>
    </div>
    <CharacterDamageDetailsModal
      :show="showDetailsModal"
      :team-details="selectedTeamDetails"
      @close="showDetailsModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import CharacterDamageDetailsModal from './CharacterDamageDetailsModal.vue';

const unions = ref([]);
const players = ref([]);
const selectedUnionId = ref(null);
const selectedBasePlayerId = ref(null);
const allCharacters = ref([]);
const coor_level = ref(0);

const elements = ['Fire', 'Water', 'Wind', 'Iron', 'Electronic'];
const activeElementTab = ref('Fire');
const teams = ref(
  elements.reduce((acc, element) => {
    acc[element] = [];
    return acc;
  }, {})
);

const simulationResults = ref([]);
const isLoading = ref(false);
const error = ref(null);

// Modal state
const showDetailsModal = ref(false);
const selectedTeamDetails = ref(null);

const showTeamDetails = (teamDamage) => {
  if (teamDamage && teamDamage.characters && teamDamage.characters.length > 0) {
    selectedTeamDetails.value = teamDamage;
    showDetailsModal.value = true;
  }
};

const formatDamage = (damage) => {
  if (damage === null || damage === undefined) {
    return 'N/A';
  }
  const roundedDamage = Math.round(damage);
  return new Intl.NumberFormat().format(roundedDamage);
};

const addCharacter = (element) => {
  if (teams.value[element].length < 5) {
    teams.value[element].push({ character_id: null, damage: null, damage_display: '' });
  } else {
    alert('每个队伍最多只能有5个角色。');
  }
};

const removeCharacter = (element, index) => {
  teams.value[element].splice(index, 1);
};

const onDamageInput = (event, character) => {
  character.damage_display = event.target.value;
  if (event.target.value.trim() === '') {
    character.damage = null;
    return;
  }
  const num = parseInt(event.target.value.replace(/,/g, ''), 10);
  character.damage = isNaN(num) ? null : num;
};

const onDamageBlur = (character) => {
  if (character.damage !== null && character.damage !== undefined) {
    character.damage_display = new Intl.NumberFormat().format(character.damage);
  } else {
    character.damage_display = '';
  }
};

const startSimulation = async () => {
  error.value = null;
  if (!selectedUnionId.value || !selectedBasePlayerId.value) {
    alert('请先选择一个联盟和基准玩家。');
    return;
  }

  const teamsWithData = Object.entries(teams.value)
    .map(([element, characters]) => ({
      element,
      characters: characters.filter(c => c.character_id && c.damage > 0),
    }))
    .filter(team => team.characters.length > 0);

  if (teamsWithData.length === 0) {
    alert('请输入至少一个角色的有效伤害数据。');
    return;
  }

  const requestBody = {
    union_id: selectedUnionId.value,
    base_player_id: selectedBasePlayerId.value,
    coor_level: coor_level.value,
    teams: teamsWithData,
  };

  isLoading.value = true;
  simulationResults.value = [];
  try {
    const response = await axios.post('/api/damage_simulation', requestBody);
    simulationResults.value = response.data.simulation_results;
  } catch (err) {
    error.value = '伤害模拟计算失败，请检查输入或联系管理员。';
    console.error(err);
  } finally {
    isLoading.value = false;
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

const fetchPlayers = async (unionId) => {
  if (!unionId) {
    players.value = [];
    selectedBasePlayerId.value = null;
    return;
  }
  try {
    const response = await axios.get(`/api/unions/${unionId}/players`);
    players.value = response.data;
  } catch (error) {
    console.error(`获取联盟 ${unionId} 的玩家列表失败:`, error);
    players.value = [];
  }
};

const fetchAllCharacters = async () => {
  try {
    const response = await axios.get('/api/characters/all-unique');
    allCharacters.value = response.data;
  } catch (error) {
    console.error('获取所有角色列表失败:', error);
  }
};

onMounted(() => {
  fetchUnions();
  fetchAllCharacters();
});

watch(selectedUnionId, (newUnionId) => {
  fetchPlayers(newUnionId);
});
</script>

<style scoped>
.damage-simulation-container {
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.main-layout {
  display: flex;
  gap: 20px;
}

.control-panel {
  width: 40%;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
}

.selectors {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.selectors select {
  padding: 8px;
  border-radius: 4px;
}

.coor-level-input {
  margin-bottom: 15px;
}

.coor-level-input label {
  margin-right: 10px;
}

.coor-level-input input {
  width: 80px;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.results-panel {
  width: 60%;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
}

.team-tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 15px;
}

.team-tabs button {
  padding: 8px 12px;
  border: 1px solid #ccc;
  background-color: #f0f0f0;
  cursor: pointer;
  width: 100px; /* 设置固定宽度 */
  text-align: center; /* 文本居中 */
}

.team-tabs button.active {
  background-color: #42b983;
  color: white;
  border-color: #42b983;
}
.team-tabs .tab-fire { background-color: #f44336; color: white; }
.team-tabs .tab-water { background-color: #2196F3; color: white; }
.team-tabs .tab-electronic { background-color: #9C27B0; color: white; }
.team-tabs .tab-iron { background-color: #FFEB3B; color: black; }
.team-tabs .tab-wind { background-color: #4CAF50; color: white; }

.team-tabs button.active {
   filter: brightness(1.2);
   transform: translateY(-1px);
}

.team-input-table table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 10px;
}

.team-input-table th,
.team-input-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.team-input-table input {
  width: 95%;
}

.delete-btn-small {
  background-color: #ff4d4f;
  padding: 4px 8px;
  font-size: 12px;
}

.simulation-controls {
  margin-top: 20px;
  text-align: center;
}

.start-simulation-btn {
  padding: 12px 25px;
  font-size: 16px;
  background-color: #28a745;
  border: none;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.start-simulation-btn:hover {
  background-color: #218838;
}

.results-table table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

.results-table th {
  background-color: #f2f2f2;
}

.clickable-cell {
  cursor: pointer;
}

.clickable-cell:hover {
  background-color: #f5f5f5;
}

.error-message {
  color: #ff4d4f;
  font-weight: bold;
}
</style>