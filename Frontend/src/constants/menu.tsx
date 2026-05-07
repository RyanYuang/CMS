import type { ItemType } from 'antd/es/menu/interface'
import type { ReactNode } from 'react'
import {
  DashboardOutlined,
  LinkOutlined,
  PictureOutlined,
  SettingOutlined,
} from '@ant-design/icons'

type MenuEntry = {
  key: string
  path: string
  label: string
  icon: ReactNode
}

export const appMenuEntries: MenuEntry[] = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: '仪表盘', path: '/dashboard' },
  { key: '/links', icon: <LinkOutlined />, label: '链接管理', path: '/links' },
  { key: '/media', icon: <PictureOutlined />, label: '媒体库', path: '/media' },
  { key: '/settings', icon: <SettingOutlined />, label: '站点设置', path: '/settings' },
]

export const appMenuItems: ItemType[] = appMenuEntries.map((entry) => ({
  key: entry.key,
  icon: entry.icon,
  label: entry.label,
}))
