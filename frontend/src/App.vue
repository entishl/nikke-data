<template>
  <div id="app-container">
    <header>
      <h1>Nikke 角色练度管理器</h1>
    </header>

    <main>
      <div class="upload-section">
        <h2>上传 JSON 文件</h2>
        <input type="file" @change="handleFileUpload" accept=".json" multiple />
        <button @click="submitFile" :disabled="filesToUpload.length === 0">上传</button>
        <button @click="clearAllData" class="delete-btn">清空所有数据</button>
        <p v-if="uploadStatus">{{ uploadStatus }}</p>
      </div>

      <div class="tabs">
        <button @click="activeTab = 'settings'" :class="{ active: activeTab === 'settings' }">设置</button>
        <button @click="activeTab = 'players'" :class="{ active: activeTab === 'players' }">玩家管理</button>
        <button @click="activeTab = 'characters'" :class="{ active: activeTab === 'characters' }">角色总表</button>
        <button @click="activeTab = 'fire'" :class="{ active: activeTab === 'fire' }">燃烧</button>
      </div>

      <div v-if="activeTab === 'characters'">
        <CharacterList :key="characterListKey" />
      </div>
      <PlayerManagement v-if="activeTab === 'players'" />
      <Settings v-if="activeTab === 'settings'" />
      <Fire v-if="activeTab === 'fire'" />

      <!-- Modal has been moved to CharacterList.vue -->
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import PlayerManagement from './components/PlayerManagement.vue';
import CharacterList from './components/CharacterList.vue';
import Settings from './components/Settings.vue';
import Fire from './components/Fire.vue';

const filesToUpload = ref([]);
const uploadStatus = ref('');
const activeTab = ref('fire'); // 'characters' or 'players' or 'fire'
const characterListKey = ref(0);

const handleFileUpload = (event) => {
  filesToUpload.value = Array.from(event.target.files);
};

const submitFile = async () => {
  if (filesToUpload.value.length === 0) return;
  const formData = new FormData();
  filesToUpload.value.forEach(file => {
    formData.append('files', file);
  });

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
  background-color: #42b983;
  color: white;
  border-color: #42b983;
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
