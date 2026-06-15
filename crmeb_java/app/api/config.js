// +----------------------------------------------------------------------
// | 环境配置 - 统一管理所有服务的 base URL
// | 按环境切换：dev / staging / prod
// +----------------------------------------------------------------------

// 当前环境（开发时改这里即可切换）
const ENV = 'dev';

const configs = {
	dev: {
		AI_SERVICE_URL: 'http://localhost:8081',       // Python OCR+AI解析服务
		BUSINESS_SERVICE_URL: 'http://localhost:8080',  // CRMEB Java 业务服务
		MOCK_BASE: 'http://localhost:20500'             // Mock 模拟服务
	},
	staging: {
		AI_SERVICE_URL: 'https://staging-ai.example.com',
		BUSINESS_SERVICE_URL: 'https://staging-api.example.com',
		MOCK_BASE: 'https://staging-mock.example.com'
	},
	prod: {
		AI_SERVICE_URL: 'https://ai.example.com',
		BUSINESS_SERVICE_URL: 'https://api.example.com',
		MOCK_BASE: ''
	}
};

const current = configs[ENV] || configs.dev;

// 是否使用 mock 模式
function isMockMode() {
	var stored = uni.getStorageSync('use_mock_api');
	return stored === true;
}

export const AI_SERVICE_URL = current.AI_SERVICE_URL;
export const BUSINESS_SERVICE_URL = current.BUSINESS_SERVICE_URL;
export const MOCK_BASE = current.MOCK_BASE;

export function getBaseURL() {
	return isMockMode() ? current.MOCK_BASE : current.BUSINESS_SERVICE_URL;
}

export function getAIBaseURL() {
	return isMockMode() ? current.MOCK_BASE : current.AI_SERVICE_URL;
}

export default {
	AI_SERVICE_URL,
	BUSINESS_SERVICE_URL,
	MOCK_BASE,
	getBaseURL,
	getAIBaseURL,
	isMockMode
};
