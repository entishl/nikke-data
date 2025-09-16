<template>
  <div v-if="visible" class="modal">
    <div class="modal-content">
      <span class="close" @click="$emit('close')">&times;</span>
      <div v-if="character">
        <h2>{{ character.name_cn }} - 详细信息</h2>
        <p><strong>玩家:</strong> {{ character.player_name }}</p>
        <p><strong>核心:</strong> {{ formatGradeAndCore(character) }}</p>
        <p><strong>技能:</strong> {{ character.skill1_level }} / {{ character.skill2_level }} / {{ character.skill_burst_level }}</p>
        <p><strong>攻击力词条:</strong> {{ character.total_stat_atk.toFixed(2) }}</p>
        <p><strong>优越代码词条:</strong> {{ character.total_inc_element_dmg.toFixed(2) }}</p>
        <p><strong>总优越（包括基础优越和魔方）:</strong> {{ character.total_superiority.toFixed(2) }}</p>
        <p><strong>总弹夹增加:</strong> {{ character.total_stat_ammo_load.toFixed(2) }}</p>
        <p><strong>相对练度:</strong> {{ character.relative_training_degree.toFixed(4) }}</p>
        <p><strong>绝对练度:</strong> {{ formatKilo(character.absolute_training_degree) }}</p>
        <h3>装备词条:</h3>
        <ul>
          <li v-for="equip in character.equipments" :key="equip.id">
            槽位 {{ equip.equipment_slot }}: {{ translateStat(equip.function_type) }} - {{ equip.function_value }} (Lv. {{ equip.level }})
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatGradeAndCore, formatItem, formatKilo } from '../utils.js';

defineProps({
  character: {
    type: Object,
    required: true,
  },
  visible: {
    type: Boolean,
    required: true,
  },
});

defineEmits(['close']);

const translateStat = (stat) => {
  const translations = {
    'IncElementDmg': '优越代码',
    'StatAtk': '攻击力',
    'StatAmmoLoad': '弹夹',
    'StatDef': '防御',
    'StatCriticalDamage': '暴击伤害',
    'StatCritical': '暴击率',
    'StatChargeTime': '蓄力速度',
    'StatChargeDamage': '蓄力伤害',
    'StatAccuracyCircle': '命中率',
  };
  return translations[stat] || stat;
};
</script>

<style scoped>
.modal {
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0,0,0,0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
  max-width: 600px;
  border-radius: 8px;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
}
</style>