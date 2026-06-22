import type { IAuthLoginRes, ICaptcha, IUpdateInfo, IUpdatePassword, IUserInfoRes } from './types/login'
import { http } from '@/http/http'

/**
 * 登录表单
 */
export interface ILoginForm {
  username: string
  password: string
  code: string
  uuid: string
}

/**
 * 获取验证码
 * @returns ICaptcha 验证码
 */
export function getCode() {
  return http.get<ICaptcha>('/captchaImage').then((res: any) => {
    const img = res.img || res.data?.img || ''
    return {
      ...res,
      data: {
        captchaEnabled: res.captchaEnabled ?? res.data?.captchaEnabled ?? true,
        registerEnabled: res.registerEnabled ?? res.data?.registerEnabled,
        uuid: res.uuid || res.data?.uuid || '',
        img,
        image: img ? `data:image/gif;base64,${img}` : '',
      },
    } as IResData<ICaptcha>
  })
}

/**
 * 用户登录
 * @param loginForm 登录表单
 */
export function login(loginForm: ILoginForm) {
  return http.post<any>(
    '/teach/mobile/login',
    {
      phone: loginForm.username,
      password: loginForm.password,
      code: loginForm.code,
      uuid: loginForm.uuid,
    },
  ).then((res: any) => {
    return {
      ...res,
      data: {
        token: res.token || res.data?.token || '',
        expiresIn: res.expiresIn || res.data?.expiresIn || 60 * 60 * 24,
      },
    } as IResData<IAuthLoginRes>
  })
}

/**
 * 刷新token
 * @param refreshToken 刷新token
 */
export function refreshToken(_refreshToken: string) {
  return Promise.reject(new Error('当前后端使用单 token 登录，暂不支持刷新 token'))
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  return http.get<any>('/teach/mobile/me').then((res: any) => {
    const user = res.data || {}
    return {
      ...res,
      data: {
        ...user,
        userId: user.userId || 0,
        username: user.username || '',
        nickname: user.nickname || user.username || '',
        avatar: user.avatar,
        roles: user.roles || [],
        permissions: user.permissions || [],
        teacherId: user.teacherId,
        isAdmin: user.isAdmin,
      },
    } as IResData<IUserInfoRes>
  })
}

/**
 * 退出登录
 */
export function logout() {
  return http.post<void>('/logout')
}

/**
 * 修改用户信息
 */
export function updateInfo(_data: IUpdateInfo) {
  return Promise.reject(new Error('当前移动端暂不支持修改用户信息，请在后台管理端维护'))
}

/**
 * 修改用户密码
 */
export function updateUserPassword(_data: IUpdatePassword) {
  return Promise.reject(new Error('当前移动端暂不支持修改密码，请在后台管理端重置'))
}

/**
 * 获取微信登录凭证
 * @returns Promise 包含微信登录凭证(code)
 */
export function getWxCode() {
  return new Promise<UniApp.LoginRes>((resolve, reject) => {
    uni.login({
      provider: 'weixin',
      success: res => resolve(res),
      fail: err => reject(new Error(err)),
    })
  })
}

/**
 * 微信登录
 * @param params 微信登录参数，包含code
 * @returns Promise 包含登录结果
 */
export function wxLogin(_data: { code: string }) {
  return Promise.reject(new Error('当前后端暂未接入微信登录，请使用手机号和密码登录'))
}
