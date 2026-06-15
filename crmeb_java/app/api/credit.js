// +----------------------------------------------------------------------
// | 征信报告识别 - API接口 (对接FastAPI后端 + Mock API兜底)
// +----------------------------------------------------------------------

import { getBaseURL, getAIBaseURL } from './config.js';

// ─── 通用请求 ──────────────────────────────────────────────

function request(opts) {
	return new Promise((resolve, reject) => {
		var url = opts.baseUrl || getBaseURL();
		uni.request({
			url: url + opts.url,
			method: opts.method || 'GET',
			data: opts.data,
			header: { 'Authorization': 'Bearer ' + (uni.getStorageSync('token') || '') },
			success: function(res) {
				if (res.statusCode === 200) {
					var d = res.data;
					// 兼容 {code,data,msg} 和直接返回
					if (d && d.code === 200) resolve(d.data);
					else if (d && d.code) reject(d);
					else resolve(d);
				} else reject(res.data);
			},
			fail: reject
		});
	});
}

function uploadRequest(filePath, url, formData) {
	return new Promise((resolve, reject) => {
		var task = uni.uploadFile({
			url: getBaseURL() + url,
			filePath: filePath,
			name: 'file',
			formData: formData || {},
			header: { 'Authorization': 'Bearer ' + (uni.getStorageSync('token') || '') },
			success: function(res) {
				if (res.statusCode === 200) {
					try { resolve(JSON.parse(res.data)); }
					catch (e) { resolve(res.data); }
				} else {
					try { reject(JSON.parse(res.data)); }
					catch (e) { reject({ message: '上传失败' }); }
				}
			},
			fail: reject
		});
		// 暴露 task 供进度回调
		return task;
	});
}

// ─── 支付相关 ──────────────────────────────────────────────

/**
 * 检查是否有免费额度
 * @returns { free_count, is_vip, price_per_query }
 */
export function checkQuota() {
	return request({ url: '/api/credit/quota', method: 'GET' });
}

/**
 * 创建支付订单（征信查询付费）
 * @returns { order_id, amount, pay_sign }
 */
export function createPayOrder() {
	return request({ url: '/api/credit/pay/create', method: 'POST' });
}

/**
 * 查询支付状态
 * @param {string} orderId 订单ID
 */
export function checkPayStatus(orderId) {
	return request({ url: '/api/credit/pay/status/' + orderId, method: 'GET' });
}

// ─── 上传 + OCR + AI 分析 ─────────────────────────────────

/**
 * 上传征信报告文件（带进度回调）
 * @param {string} filePath 文件路径
 * @param {Function} onProgress 进度回调 (percent)
 * @returns { task_id, file_name }
 */
export function uploadCreditReport(filePath, onProgress) {
	return new Promise((resolve, reject) => {
		var task = uni.uploadFile({
			url: getAIBaseURL() + '/api/ocr/upload',
			filePath: filePath,
			name: 'file',
			success: function(res) {
				if (res.statusCode === 200) {
					try { 
						var data = JSON.parse(res.data);
						// 兼容 {code,data,msg} 格式
						if (data && data.code === 200) resolve(data.data);
						else resolve(data);
					} catch (e) { 
						resolve(res.data); 
					}
				} else {
					try { reject(JSON.parse(res.data)); }
					catch (e) { reject({ message: '上传失败，状态码: ' + res.statusCode }); }
				}
			},
			fail: function(err) {
				reject(new Error(err.errMsg || '上传失败'));
			}
		});
		if (onProgress && task && typeof task.onProgressUpdate === 'function') {
			task.onProgressUpdate(function(p) {
				onProgress(p.progress);
			});
		}
	});
}

/**
 * 开始 AI 分析
 * @param {string} taskId 任务ID
 */
export function analyzeCreditReport(taskId) {
	return request({ url: '/api/ocr/analyze/' + taskId, method: 'POST', baseUrl: getAIBaseURL() });
}

/**
 * 查询分析结果
 * @param {string} taskId 任务ID
 */
export function getCreditResult(taskId) {
	return request({ url: '/api/ocr/result/' + taskId, method: 'GET', baseUrl: getAIBaseURL() });
}

/**
 * 轮询结果直到完成
 * @param {string} taskId 任务ID
 * @param {Function} onStep 步骤回调 (step, detail)
 * @param {number} maxRetries 最大轮询次数
 */
export function pollUntilComplete(taskId, onStep, maxRetries) {
	maxRetries = maxRetries || 60;
	var retries = 0;
	return new Promise(function(resolve, reject) {
		function check() {
			retries++;
			if (onStep) onStep('polling', { attempt: retries, max: maxRetries });
			getCreditResult(taskId).then(function(res) {
				if (res.status === 'completed') {
					resolve(res);
				} else if (res.status === 'failed') {
					reject(new Error(res.error_message || '分析失败'));
				} else if (retries >= maxRetries) {
					reject(new Error('分析超时，请稍后查看'));
				} else {
					setTimeout(check, 2000);
				}
			}).catch(function(err) {
				if (retries >= maxRetries) reject(err);
				else setTimeout(check, 2000);
			});
		}
		check();
	});
}

// ─── 历史记录 ─────────────────────────────────────────────

/**
 * 获取查询历史
 */
export function getHistory() {
	return request({ url: '/api/credit/records', method: 'GET' });
}

/**
 * 获取单条记录详情
 */
export function getRecordDetail(recordId) {
	return request({ url: '/api/credit/detail/' + recordId, method: 'GET' });
}

/**
 * 删除查询记录
 */
export function deleteRecord(recordId) {
	return request({ url: '/api/credit/delete/' + recordId, method: 'DELETE' });
}

// ─── 分销/佣金 ─────────────────────────────────────────────

/**
 * 获取用户佣金信息
 */
export function getCommission() {
	return request({ url: '/api/credit/commission', method: 'GET' });
}

/**
 * 获取分销推广码
 * @returns { share_code, qrcode_url, share_link }
 */
export function getShareInfo() {
	return request({ url: '/api/credit/share/info', method: 'GET' });
}

/**
 * 通过分享码记录分销关系
 * @param {string} shareCode 分享码
 */
export function bindShareCode(shareCode) {
	return request({ url: '/api/credit/share/bind', method: 'POST', data: { share_code: shareCode } });
}

// ─── 本地缓存工具 ─────────────────────────────────────────

const CACHE_KEY = 'credit_result_cache';
const HISTORY_KEY = 'credit_history';
const MAX_CACHE = 20;

/**
 * 缓存分析结果到本地
 */
export function cacheResult(taskId, result) {
	var list = uni.getStorageSync(CACHE_KEY) || [];
	// 去重
	list = list.filter(function(item) { return item.taskId !== taskId; });
	list.unshift({ taskId: taskId, time: Date.now(), result: result });
	uni.setStorageSync(CACHE_KEY, list.slice(0, MAX_CACHE));
}

/**
 * 从本地缓存读取结果
 */
export function getCachedResult(taskId) {
	var list = uni.getStorageSync(CACHE_KEY) || [];
	for (var i = 0; i < list.length; i++) {
		if (list[i].taskId === taskId) return list[i].result;
	}
	return null;
}

/**
 * 获取所有本地历史
 */
export function getCachedHistory() {
	return uni.getStorageSync(CACHE_KEY) || [];
}

/**
 * 删除本地缓存
 */
export function clearCache(taskId) {
	if (taskId) {
		var list = uni.getStorageSync(CACHE_KEY) || [];
		uni.setStorageSync(CACHE_KEY, list.filter(function(item) { return item.taskId !== taskId; }));
	} else {
		uni.setStorageSync(CACHE_KEY, []);
	}
}
