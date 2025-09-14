<template>
  <div>
    <h2>C位角色设置</h2>
    <button @click="saveSettings">保存设置</button>
    <div v-for="(group, element) in groupedCharacters" :key="element" class="element-group">
      <h3>{{ element }}</h3>
      <ul class="character-list">
        <li v-for="char in group" :key="char.id" class="character-item">
          <label>
            <input type="checkbox" v-model="isCSettings[char.id]" />
            {{ char.name_cn }}
          </label>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const characters = ref([]);
const isCSettings = ref({});

const groupedCharacters = computed(() => {
  const groups = {};
  for (const char of characters.value) {
    const element = char.element || '未知';
    if (!groups[element]) {
      groups[element] = [];
    }
    groups[element].push(char);
  }
  return groups;
});

onMounted(async () => {
  try {
    const [uniqueCharsResponse, settingsResponse] = await Promise.all([
      axios.get('/api/characters/all-unique'),
      axios.get('/api/settings/is-c')
    ]);
    
    characters.value = uniqueCharsResponse.data;
    const settings = settingsResponse.data;

    const initialSettings = {};
    for (const char of characters.value) {
      initialSettings[char.id] = settings[char.id] !== undefined ? settings[char.id] : true;
    }
    isCSettings.value = initialSettings;

  } catch (error) {
    console.error('Error fetching initial data:', error);
  }
});

const saveSettings = async () => {
  try {
    await axios.post('/api/settings/is-c', isCSettings.value);
    alert('设置已保存！');
  } catch (error) {
    console.error('Error saving settings:', error);
    alert('保存设置失败。');
  }
};
</script>

<style scoped>
.element-group {
  margin-bottom: 20px;
}
.character-list {
  list-style-type: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}
.character-item {
  margin: 5px 0;
}
</style>