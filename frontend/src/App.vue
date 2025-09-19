<template>
  <div id="app-container">
    <header>
      <h1>Nikke 联盟练度管理</h1>
    </header>

    <nav class="main-nav">
      <router-link to="/unions">联盟管理</router-link>
      <router-link to="/players">玩家数据中心</router-link>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
// All logic has been moved to specific views or composables.
// This component is now only responsible for the main layout and routing.
</script>

<style>
#app-container {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 20px;
  max-width: 1200px;
  margin: 20px auto;
}

header {
  text-align: center;
  margin-bottom: 40px;
}

.main-nav {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.main-nav a {
  text-decoration: none;
  color: #42b983;
  font-weight: bold;
  padding: 10px 15px;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.main-nav a.router-link-exact-active {
  background-color: #42b983;
  color: white;
}
</style>
