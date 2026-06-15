<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch')
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
page {
  background-color: #F8FAFC;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

view, text {
  box-sizing: border-box;
}

button {
  margin: 0;
  padding: 0;
  background: transparent;
  border: none;
}

button::after {
  border: none;
}
</style>
