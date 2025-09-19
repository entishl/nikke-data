import apiClient from './api';

export const getUnions = () => {
  return apiClient.get('/unions/');
};

export const addUnion = (unionName) => {
  return apiClient.post('/unions/', { name: unionName });
};

export const updateUnion = (id, unionName) => {
  // The backend endpoint for updating a union seems to expect a name string, not a full object.
  // Based on the old code: `axios.put(`/api/unions/${id}`, union)`. Let's assume it expects an object.
  // If this fails, we can adjust. The old code was ambiguous. Let's send an object for consistency.
  return apiClient.put(`/unions/${id}`, { name: unionName });
};

export const deleteUnion = (id) => {
  return apiClient.delete(`/unions/${id}`);
};

// This function will be used in the PlayerDataHubView
export const uploadPlayerData = (formData) => {
  return apiClient.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
