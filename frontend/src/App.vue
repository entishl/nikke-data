<template>
  <div id="app-container">
    <header>
      <h1>Nikke 联盟练度管理</h1>
    </header>

    <main>
      <div class="upload-section">
        <h2 @click="toggleUploadVisibility" style="cursor: pointer;">上传 JSON 文件 (点击隐藏)</h2>
        <div v-if="isUploadVisible" class="upload-content">
          <div class="upload-controls">
            <select v-model="selectedUnionId">
              <option :value="null">选择一个联盟</option>
              <option v-for="union in unions" :key="union.id" :value="union.id">{{ union.name }}</option>
            </select>
            <input type="file" @change="handleFileUpload" accept=".json" multiple />
            <button @click="submitFile" :disabled="filesToUpload.length === 0 || selectedUnionId === null">上传</button>
          </div>
          <button @click="clearAllData" class="delete-btn">清空所有数据</button>
          <span style="margin-left: 10px; color: #666;">先添加一个联盟后并选中该联盟再上传。 <br> 演示页面，试用后请清空数据，如需自用点击右上角三个点，duplicate this space</span>
          <p v-if="uploadStatus">{{ uploadStatus }}</p>
        </div>
      </div>

      <div class="tabs">
        <button @click="activeTab = 'settings'" :class="{ active: activeTab === 'settings' }">设置</button>
        <button @click="activeTab = 'unions'" :class="{ active: activeTab === 'unions' }">联盟管理</button>
        <button @click="activeTab = 'players'" :class="{ active: activeTab === 'players' }">玩家管理</button>
        <button @click="activeTab = 'characters'" :class="{ active: activeTab === 'characters' }">角色总表</button>
        <button @click="activeTab = 'fire'" class="tab-fire" :class="{ active: activeTab === 'fire' }">燃烧</button>
        <button @click="activeTab = 'water'" class="tab-water" :class="{ active: activeTab === 'water' }">水冷</button>
        <button @click="activeTab = 'electronic'" class="tab-electronic" :class="{ active: activeTab === 'electronic' }">电击</button>
        <button @click="activeTab = 'iron'" class="tab-iron" :class="{ active: activeTab === 'iron' }">铁甲</button>
        <button @click="activeTab = 'wind'" class="tab-wind" :class="{ active: activeTab === 'wind' }">风压</button>
        <button @click="activeTab = 'element-training'" :class="{ active: activeTab === 'element-training' }">元素总览</button>
        <button @click="activeTab = 'damage_simulation'" :class="{ active: activeTab === 'damage_simulation' }">伤害模拟</button>
      </div>

      <div v-if="activeTab === 'characters'">
        <CharacterList :key="characterListKey" />
      </div>
      <UnionManagement v-if="activeTab === 'unions'" @unions-updated="fetchUnions" />
      <PlayerManagement v-if="activeTab === 'players'" />
      <Settings v-if="activeTab === 'settings'" @settings-updated="refreshElementTraining" />
      <Fire v-if="activeTab === 'fire'" />
      <Water v-if="activeTab === 'water'" />
      <Electronic v-if="activeTab === 'electronic'" />
      <Iron v-if="activeTab === 'iron'" />
      <Wind v-if="activeTab === 'wind'" />
      <ElementTrainingAnalysis v-if="activeTab === 'element-training'" :key="elementTrainingKey" />
      <DamageSimulation v-if="activeTab === 'damage_simulation'" />

      <!-- Modal has been moved to CharacterList.vue -->
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import PlayerManagement from './components/PlayerManagement.vue';
import CharacterList from './components/CharacterList.vue';
import Settings from './components/Settings.vue';
import Fire from './components/Fire.vue';
import Water from './components/water.vue';
import Electronic from './components/Electronic.vue';
import Iron from './components/iron.vue';
import Wind from './components/wind.vue';
import UnionManagement from './components/UnionManagement.vue';
import ElementTrainingAnalysis from './components/ElementTrainingAnalysis.vue';
import DamageSimulation from './components/DamageSimulation.vue';

const filesToUpload = ref([]);
const uploadStatus = ref('');
const activeTab = ref('unions'); // 'characters' or 'players' or 'fire' or 'water' or 'electronic' or 'unions' or 'iron' or 'wind'
const characterListKey = ref(0);
const elementTrainingKey = ref(0);
const unions = ref([]);
const selectedUnionId = ref(null);
const isUploadVisible = ref(true);

const toggleUploadVisibility = () => {
  isUploadVisible.value = !isUploadVisible.value;
};

const refreshElementTraining = () => {
  elementTrainingKey.value++;
};

const handleFileUpload = (event) => {
  filesToUpload.value = Array.from(event.target.files);
};

const submitFile = async () => {
  if (filesToUpload.value.length === 0) return;
  const formData = new FormData();
  filesToUpload.value.forEach(file => {
    formData.append('files', file);
  });
  if (selectedUnionId.value) {
    formData.append('union_id', selectedUnionId.value);
  }

  try {
    const response = await axios.post('/api/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    uploadStatus.value = `${response.data.successful_files} 个文件上传成功, ${response.data.failed_files} 个文件上传失败。`;
    characterListKey.value++;
  } catch (error) {
    uploadStatus.value = '文件上传失败。';
    console.error(error);
  }
};

const clearAllData = async () => {
  if (confirm('确定要清空所有数据吗？此操作不可逆！')) {
    try {
      await axios.delete('/api/clear-all-data');
      alert('所有数据已成功清空。');
      characterListKey.value++;
    } catch (error) {
      alert('清空数据时出错。');
      console.error('Error clearing all data:', error);
    }
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

onMounted(fetchUnions);
</script>

<style>
#app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 20px;
}

header {
  text-align: center;
  margin-bottom: 40px;
}

main {
  max-width: 2150px;
  margin: 0 auto;
}

.upload-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.upload-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.tabs {
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  cursor: pointer;
  border: 1px solid #ccc;
  background-color: #e0e0e0;
  color: #333;
  margin-right: 5px;
}

.tabs button.active {
  background-color: black;
  color: white;
  border-color: black;
}

.tabs .tab-fire { background-color: #f44336; color: white; border-color: #f44336;}
.tabs .tab-water { background-color: #2196F3; color: white; border-color: #2196F3;}
.tabs .tab-electronic { background-color: #9C27B0; color: white; border-color: #9C27B0;}
.tabs .tab-iron { background-color: #FFEB3B; color: black; border-color: #FFEB3B;}
.tabs .tab-wind { background-color: #4CAF50; color: white; border-color: #4CAF50;}

.tabs button.active.tab-fire,
.tabs button.active.tab-water,
.tabs button.active.tab-electronic,
.tabs button.active.tab-iron,
.tabs button.active.tab-wind {
  filter: brightness(1.2);
  transform: translateY(-1px);
}

input[type="file"] {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 8px 15px;
  border: none;
  background-color: #42b983;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
}

.delete-btn {
  background-color: #ff4d4f;
  margin-left: 5px;
}
</style>
