import { defineStore } from 'pinia';
import axios from 'axios';

export const useUnionStore = defineStore('unions', {
  state: () => ({
    unions: [],
  }),
  actions: {
    async fetchUnions() {
      console.log('--- Step 3: fetchUnions action called in unionStore ---');
      try {
        const response = await axios.get('/api/unions/');
        this.unions = response.data;
        console.log('--- Step 4: unions state updated in store. New value:', this.unions);
      } catch (error) {
        console.error('获取联盟列表失败:', error);
        // 在这里可以添加更复杂的错误处理逻辑
      }
    },
    async addUnion(union) {
      try {
        const res = await axios.post('/api/unions/', union);
        this.unions.push(res.data);
      } catch (error) {
        console.error('添加联盟失败:', error);
        alert('添加联盟失败。');
        throw error; // 重新抛出错误，以便组件可以捕获它
      }
    },
    async updateUnion(id, union) {
      try {
        const res = await axios.put(`/api/unions/${id}`, union);
        const index = this.unions.findIndex(u => u.id === id);
        if (index !== -1) {
          this.unions[index] = res.data;
        }
      } catch (error) {
        console.error('更新联盟失败:', error);
        alert('更新联盟失败。');
        throw error;
      }
    },
    async deleteUnion(id) {
      try {
        await axios.delete(`/api/unions/${id}`);
        this.unions = this.unions.filter(u => u.id !== id);
      } catch (error) {
        console.error('删除联盟失败:', error);
        alert(`删除联盟失败: ${error.response?.data?.detail || '未知错误'}`);
        throw error;
      }
    }
  },
});