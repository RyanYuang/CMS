import { LockOutlined, MailOutlined } from '@ant-design/icons'
import { Button, Card, Checkbox, Form, Input, Typography, message } from 'antd'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LoginBuildStamp } from '../../components/LoginBuildStamp'
import { authApi } from '../../services'
import { TOKEN_KEY } from '../../services/http'
import { setCurrentUser } from '../../utils/auth'

type LoginForm = {
  username: string
  password: string
  remember: boolean
}

export function LoginPage() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)

  const onFinish = async (values: LoginForm) => {
    if (!values.username || !values.password) {
      message.error('请填写完整的登录信息')
      return
    }
    setIsLoading(true)
    try {
      const tokenResp = await authApi.login(values.username, values.password)
      localStorage.setItem(TOKEN_KEY, tokenResp.access_token)
      localStorage.setItem('isAuthenticated', 'true')
      if (values.remember) {
        localStorage.setItem('rememberMe', 'true')
      }
      const me = await authApi.me()
      setCurrentUser(me)
      message.success('登录成功！')
      navigate('/dashboard', { replace: true })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <Card className="login-card">
        <Typography.Title level={2}>CMS 后台登录</Typography.Title>
        <Typography.Paragraph type="secondary">
          输入您的账号和密码以访问后台管理系统
        </Typography.Paragraph>
        <Form<LoginForm> layout="vertical" initialValues={{ remember: false }} onFinish={onFinish}>
          <Form.Item name="username" label="账号" rules={[{ required: true }]}>
            <Input prefix={<MailOutlined />} placeholder="请输入账号" size="large" disabled={isLoading} />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" size="large" disabled={isLoading} />
          </Form.Item>
          <Form.Item name="remember" valuePropName="checked">
            <Checkbox>记住我</Checkbox>
          </Form.Item>
          <Button type="primary" htmlType="submit" size="large" block loading={isLoading}>
            {isLoading ? '登录中...' : '登录'}
          </Button>
        </Form>
        <Typography.Paragraph type="secondary" className="m-0" style={{ marginTop: 12 }}>
          默认账号：admin / admin123456
        </Typography.Paragraph>
      </Card>
      <LoginBuildStamp />
    </div>
  )
}
