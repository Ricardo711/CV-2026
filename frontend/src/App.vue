<template>
  <n-config-provider>
    <n-message-provider>
      <AppLayout />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { NConfigProvider, NMessageProvider } from "naive-ui";
import AppLayout from "./layouts/AppLayout.vue";
</script>
