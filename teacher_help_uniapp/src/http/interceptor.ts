import type { CustomRequestOptions } from '@/http/types'
import { isDoubleTokenRes, isSingleTokenRes } from '@/api/types/login'
import { useTokenStore } from '@/store/token'
import { getEnvBaseUrl } from '@/utils'
import { platform } from '@/utils/platform'
import { stringifyQuery } from './tools/queryString'

// 请求基准地址
const baseUrl = getEnvBaseUrl()

function getHeaderValue(header: Record<string, any> = {}, name: string) {
  const target = name.toLowerCase()
  const key = Object.keys(header).find(item => item.toLowerCase() === target)
  return key ? header[key] : ''
}

// 拦截器配置
const httpInterceptor = {
  // 拦截前触发
  invoke(options: CustomRequestOptions) {
    // 接口请求支持通过 query 参数配置 queryString
    if (options.query) {
      const queryStr = stringifyQuery(options.query)
      if (options.url.includes('?')) {
        options.url += `&${queryStr}`
      }
      else {
        options.url += `?${queryStr}`
      }
    }
    // 非 http 开头需拼接地址
    if (!options.url.startsWith('http')) {
      // #ifdef H5
      // console.log(__VITE_APP_PROXY__)
      if (JSON.parse(__VITE_APP_PROXY__)) {
        // 自动拼接代理前缀
        options.url = import.meta.env.VITE_APP_PROXY_PREFIX + options.url
      }
      else {
        options.url = baseUrl + options.url
      }
      // #endif
      // 非H5正常拼接
      // #ifndef H5
      options.url = baseUrl + options.url
      // #endif
      // TIPS: 如果需要对接多个后端服务，也可以在这里处理，拼接成所需要的地址
    }
    // 1. 请求超时
    options.timeout = 60000 // 60s
    // 2. （可选）添加小程序端请求头标识
    options.header = {
      platform, // 可选，与 uniapp 定义的平台一致，告诉后台来源
      ...options.header,
    }
    const contentType = `${getHeaderValue(options.header, 'content-type')}`.toLowerCase()
    if (
      contentType.includes('application/x-www-form-urlencoded')
      && options.data
      && typeof options.data === 'object'
      && !Array.isArray(options.data)
    ) {
      options.data = stringifyQuery(options.data as Record<string, any>)
    }
    // 3. 添加 token 请求头标识
    const tokenStore = useTokenStore()
    const tokenInfo = tokenStore.tokenInfo
    let token = ''
    if (isSingleTokenRes(tokenInfo)) {
      token = tokenInfo.token
    }
    else if (isDoubleTokenRes(tokenInfo)) {
      token = tokenInfo.accessToken
    }
    if (token) {
      options.header.Authorization = `Bearer ${token}`
    }
  },
}

export const requestInterceptor = {
  install() {
    // 拦截 request 请求
    uni.addInterceptor('request', httpInterceptor)
    // 拦截 uploadFile 文件上传
    uni.addInterceptor('uploadFile', httpInterceptor)
  },
}
