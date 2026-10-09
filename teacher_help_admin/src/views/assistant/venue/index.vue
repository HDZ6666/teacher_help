<template>
  <div class="app-container">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="场地管理" name="manage">
        <venue-manage ref="manageRef" @changed="dirty = true" />
      </el-tab-pane>
      <el-tab-pane label="订场管理" name="grid" lazy>
        <booking-grid ref="gridRef" @show-locks="showLocks" />
      </el-tab-pane>
      <el-tab-pane label="预订记录" name="record">
        <booking-record ref="recordRef" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup name="AssistantVenue">
import { nextTick, ref } from 'vue'
import VenueManage from './components/VenueManage'
import BookingGrid from './components/BookingGrid'
import BookingRecord from './components/BookingRecord'

const activeTab = ref('manage')
const dirty = ref(false)
const manageRef = ref()
const gridRef = ref()
const recordRef = ref()

function handleTabChange(name) {
  nextTick(() => {
    if (name === 'grid' && dirty.value) {
      gridRef.value?.reload()
      dirty.value = false
    }
    if (name === 'record') {
      recordRef.value?.loadVenues()
      recordRef.value?.getList()
    }
  })
}

function showLocks() {
  activeTab.value = 'record'
  nextTick(() => recordRef.value?.showLocks())
}
</script>
