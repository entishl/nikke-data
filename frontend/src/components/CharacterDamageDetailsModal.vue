<template>
  <div v-if="show" class="modal-overlay" @click.self="close">
    <div class="modal-content">
      <h3>角色伤害详情</h3>
      <div v-if="teamDetails && teamDetails.characters && teamDetails.characters.length > 0">
        <table>
          <thead>
            <tr>
              <th>角色名称</th>
              <th>模拟伤害</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="char in teamDetails.characters" :key="char.character_id">
              <td>{{ char.name_cn }}</td>
              <td>{{ (char.simulated_damage / 10000).toFixed(2) }}w</td>
            </tr>
          </tbody>
        </table>
        <h4>总伤害: {{ (teamDetails.total_damage / 10000).toFixed(2) }}w</h4>
      </div>
      <div v-else>
        <p>没有可用的角色伤害数据。</p>
      </div>
      <button @click="close" class="close-btn">关闭</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  teamDetails: {
    type: Object,
    default: () => ({ characters: [], total_damage: 0 }),
  },
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px 30px;
  border-radius: 8px;
  width: 400px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin-top: 0;
}

.modal-content table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.modal-content th,
.modal-content td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

.close-btn {
  display: block;
  margin: 10px auto 0;
}
</style>