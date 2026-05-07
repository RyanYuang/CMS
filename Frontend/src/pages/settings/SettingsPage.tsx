import { UploadOutlined } from '@ant-design/icons'
import { Button, Card, Form, Input, Space, Typography, Upload, message } from 'antd'
import { useState } from 'react'

type SettingsForm = {
  siteName: string
  siteDescription: string
  twitterUrl: string
  githubUrl: string
  emailUrl: string
}

export function SettingsPage() {
  const [form] = Form.useForm<SettingsForm>()
  const [logoPreview, setLogoPreview] = useState<string | null>(null)

  const initialValues: SettingsForm = {
    siteName: '我的个人网站',
    siteDescription: '分享生活，记录点滴',
    twitterUrl: '',
    githubUrl: '',
    emailUrl: '',
  }

  const onSubmit = (values: SettingsForm) => {
    if (!values.siteName) {
      message.error('站点名称不能为空')
      return
    }
    window.setTimeout(() => message.success('设置已保存'), 500)
  }

  return (
    <Space direction="vertical" size={24} className="w-full">
      <div>
        <Typography.Title level={1} style={{ fontSize: 30, marginBottom: 8 }}>
          站点设置
        </Typography.Title>
        <Typography.Text type="secondary">配置站点的基本信息</Typography.Text>
      </div>
      <Form<SettingsForm> form={form} layout="vertical" initialValues={initialValues} onFinish={onSubmit}>
        <Card className="cms-card" style={{ marginBottom: 16 }}>
          <Typography.Title level={4}>基本信息</Typography.Title>
          <Typography.Paragraph type="secondary">设置站点的名称、简介等基本信息</Typography.Paragraph>
          <Form.Item label="站点名称" name="siteName" rules={[{ required: true, message: '请输入站点名称' }]}>
            <Input placeholder="请输入站点名称" />
          </Form.Item>
          <Form.Item label="站点简介" name="siteDescription">
            <Input placeholder="请输入站点简介" />
          </Form.Item>
          <Form.Item label="站点 Logo">
            <Space>
              {logoPreview ? (
                <img
                  src={logoPreview}
                  alt="logo preview"
                  style={{ width: 64, height: 64, borderRadius: 8, border: '1px solid #e5e5e5', objectFit: 'cover' }}
                />
              ) : null}
              <Upload
                accept="image/*"
                showUploadList={false}
                beforeUpload={(file) => {
                  if (!file.type.startsWith('image/')) {
                    message.error('请上传图片文件')
                    return Upload.LIST_IGNORE
                  }
                  if (file.size > 2 * 1024 * 1024) {
                    message.error('Logo 文件大小不能超过 2MB')
                    return Upload.LIST_IGNORE
                  }
                  const reader = new FileReader()
                  reader.onloadend = () => setLogoPreview(String(reader.result))
                  reader.readAsDataURL(file)
                  return false
                }}
              >
                <Button icon={<UploadOutlined />}>上传 Logo</Button>
              </Upload>
            </Space>
            <Typography.Paragraph type="secondary" style={{ marginTop: 8 }}>
              建议尺寸：512x512，格式：PNG、JPG，不超过 2MB
            </Typography.Paragraph>
          </Form.Item>
        </Card>
        <Card className="cms-card">
          <Typography.Title level={4}>社交链接</Typography.Title>
          <Typography.Paragraph type="secondary">配置站点的社交媒体链接（选填）</Typography.Paragraph>
          <Form.Item label="Twitter / X" name="twitterUrl">
            <Input placeholder="https://twitter.com/username" />
          </Form.Item>
          <Form.Item label="GitHub" name="githubUrl">
            <Input placeholder="https://github.com/username" />
          </Form.Item>
          <Form.Item label="联系邮箱" name="emailUrl">
            <Input type="email" placeholder="contact@example.com" />
          </Form.Item>
        </Card>
        <Form.Item style={{ marginTop: 16, marginBottom: 0 }}>
          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            <Button
              onClick={() => {
                form.resetFields()
                setLogoPreview(null)
                message.success('已重置为默认值')
              }}
            >
              重置
            </Button>
            <Button type="primary" htmlType="submit">
              保存设置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Space>
  )
}
