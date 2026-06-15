<template>
	<view class="tab-bar-container">
		<view class="tab-pill">
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 0 }"
				@click="switchTab(0)"
			>
				<svg class="tab-icon" viewBox="0 0 18 18">
					<path d="M2.25 1.5h13.5v15H2.25z" :stroke="currentIndex === 0 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M6.75 9v7.5" :stroke="currentIndex === 0 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none" stroke-linecap="round"/>
				</svg>
				<text class="tab-label">首页</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 1 }"
				@click="switchTab(1)"
			>
				<svg class="tab-icon" viewBox="0 0 18 18">
					<circle cx="9" cy="9" r="7.5" :stroke="currentIndex === 1 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none"/>
					<path d="M9 4.5v6" :stroke="currentIndex === 1 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none" stroke-linecap="round"/>
				</svg>
				<text class="tab-label">历史</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 2 }"
				@click="switchTab(2)"
			>
				<svg class="tab-icon" viewBox="0 0 18 18">
					<path d="M6 3h6v9H6z" :stroke="currentIndex === 2 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
					<path d="M3 12h12v3H3z" :stroke="currentIndex === 2 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
				<text class="tab-label">上传</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 3 }"
				@click="switchTab(3)"
			>
				<svg class="tab-icon" viewBox="0 0 18 18">
					<circle cx="9" cy="9" r="7.5" :stroke="currentIndex === 3 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none"/>
					<path d="M6.75 7.5v3" :stroke="currentIndex === 3 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none" stroke-linecap="round"/>
				</svg>
				<text class="tab-label">结果</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentIndex === 4 }"
				@click="switchTab(4)"
			>
				<svg class="tab-icon" viewBox="0 0 18 18">
					<circle cx="9" cy="6" r="3" :stroke="currentIndex === 4 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none"/>
					<path d="M3 16.5c0-3.3 2.7-6 6-6s6 2.7 6 6" :stroke="currentIndex === 4 ? '#FFFFFF' : '#94A3B8'" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
				<text class="tab-label">我的</text>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{
	current: number
}>()

const emit = defineEmits<{
	change: [index: number]
}>()

const currentIndex = ref(0)

watch(() => props.current, (val) => {
	currentIndex.value = val
})

onMounted(() => {
	currentIndex.value = props.current
	updateCurrentIndex()
})

const updateCurrentIndex = () => {
	const pages = getCurrentPages()
	if (pages.length > 0) {
		const currentPage = pages[pages.length - 1]
		const route = '/' + currentPage.route
		
		if (route.indexOf('pages/index/index') !== -1) {
			currentIndex.value = 0
		} else if (route.indexOf('pages/records/records') !== -1) {
			currentIndex.value = 1
		} else if (route.indexOf('pages/upload/upload') !== -1) {
			currentIndex.value = 2
		} else if (route.indexOf('pages/result/result') !== -1) {
			currentIndex.value = 3
		} else if (route.indexOf('pages/profile/profile') !== -1) {
			currentIndex.value = 4
		}
	}
}

const switchTab = (index: number) => {
	if (currentIndex.value === index) return
	
	currentIndex.value = index
	emit('change', index)
	
	const routes: Record<number, string> = {
		0: '/pages/index/index',
		1: '/pages/records/records',
		2: '/pages/upload/upload',
		3: '/pages/result/result',
		4: '/pages/profile/profile'
	}
	
	const url = routes[index]
	if (!url) return
	
	uni.navigateTo({ url })
}
</script>

<style lang="scss" scoped>
.tab-bar-container {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	height: 88rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: #F8FAFC;
	z-index: 1000;
	padding-bottom: env(safe-area-inset-bottom);
}

.tab-pill {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 72rpx;
	padding: 8rpx;
	box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.06);
	gap: 4rpx;
}

.tab-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 124rpx;
	height: 108rpx;
	border-radius: 52rpx;
	gap: 4rpx;
	transition: all 0.25s ease;
	
	&.active {
		background: linear-gradient(135deg, #6366F1, #A855F7);
		
		.tab-label {
			color: #FFFFFF;
			font-weight: 600;
		}
	}
}

.tab-icon {
	width: 36rpx;
	height: 36rpx;
	flex-shrink: 0;
}

.tab-label {
	font-size: 20rpx;
	color: #94A3B8;
	font-weight: 500;
}
</style>
