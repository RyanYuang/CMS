import { LogoutOutlined, UserOutlined } from '@ant-design/icons'
import { Button, Layout, Menu, Modal, Space, Typography } from 'antd'
import { useMemo } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { appMenuEntries, appMenuItems } from '../constants/menu'

const { Header, Sider, Content } = Layout

export function AdminLayout() {
  const handleLogout = () => {
    Modal.confirm({
      title: '确认退出',
      content: '您确定要退出登录吗？',
      okText: '确认退出',
      cancelText: '取消',
      onOk: () => {
        localStorage.removeItem('isAuthenticated')
        navigate('/login')
      },
    })
  }

  const location = useLocation()
  const navigate = useNavigate()

  const selectedKey = useMemo(() => {
    const target = appMenuEntries.find((entry) => location.pathname.startsWith(entry.path))
    return target ? [target.key] : []
  }, [location.pathname])

  return (
    <Layout className="app-shell">
      <Sider width={256} className="figma-sider">
        <div className="logo-wrap">
          <Typography.Title level={4} className="logo-text">
            CMS 后台
          </Typography.Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedKey}
          items={appMenuItems}
          onClick={({ key }) => navigate(String(key))}
          className="figma-menu"
        />
        <div className="sider-footer">© 2026 站长后台</div>
      </Sider>
      <Layout>
        <Header className="app-header">
          <Space size={12}>
            <Typography.Title level={4} className="m-0">
              欢迎回来
            </Typography.Title>
          </Space>
          <Space size={12}>
            <Space size={8}>
              <UserOutlined />
              <Typography.Text>管理员</Typography.Text>
            </Space>
            <Button icon={<LogoutOutlined />} onClick={handleLogout}>
              退出登录
            </Button>
          </Space>
        </Header>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
