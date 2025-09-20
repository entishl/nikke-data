import { createApp, ref } from 'vue';
import ToastContainer from '../components/ToastContainer.vue';

const toastPlugin = {
  install(app) {
    const toastContainerRef = ref(null);

    const show = (message, type = 'success', duration = 3000) => {
      if (toastContainerRef.value) {
        toastContainerRef.value.addToast(message, type, duration);
      }
    };

    app.config.globalProperties.$toast = {
      show,
      success: (message, duration = 3000) => show(message, 'success', duration),
      error: (message, duration = 3000) => show(message, 'error', duration),
    };

    const mountPoint = document.createElement('div');
    document.body.appendChild(mountPoint);
    
    const toastApp = createApp(ToastContainer, { ref: toastContainerRef });
    const instance = toastApp.mount(mountPoint);
    toastContainerRef.value = instance;
  },
};

export default toastPlugin;