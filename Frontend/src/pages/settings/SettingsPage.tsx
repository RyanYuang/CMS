import { UploadOutlined } from '@ant-design/icons'
import { Button, Card, Form, Input, Space, Spin, Typography, Upload, message } from 'antd'
import { useEffect, useState } from 'react'
import { assetsApi, settingsApi } from '../../services'
import { hasPermission } from '../../utils/auth'

type SettingsForm = {
  siteName: string
  siteDescription: string
  logoUrl: string
  twitterUrl: string
  githubUrl: string
  emailUrl: string
}

export function SettingsPage() {
  const [form] = Form.useForm<SettingsForm>()
  const [logoPreview, setLogoPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const canWrite = hasPermission('setting:write')

  useEffect(() => {
    settingsApi
      .list()
      .then((rows) => {
        const basic = (rows.find((item) => item.key === 'site.basic')?.value ?? {}) as Record<string, string>
        const social = (rows.find((item) => item.key === 'social.links')?.value ?? {}) as Record<string, string>
        const initialValues: SettingsForm = {
          siteName: basic.siteName ?? '',
          siteDescription: basic.siteDescription ?? '',
          logoUrl: basic.logoUrl ?? '',
          twitterUrl: social.twitter ?? '',
          githubUrl: social.github ?? '',
          emailUrl: social.email ?? '',
        }
        form.setFieldsValue(initialValues)
        setLogoPreview(initialValues.logoUrl || null)
      })
      .finally(() => setLoading(false))
  }, [form])

  const onSubmit = async (values: SettingsForm) => {
    await settingsApi.upsert([
      {
        key: 'site.basic',
        value: {
          siteName: values.siteName,
          siteDescription: values.siteDescription,
          logoUrl: values.logoUrl || '',
        },
      },
      {
        key: 'social.links',
        value: {
          twitter: values.twitterUrl || '',
          github: values.githubUrl || '',
          email: values.emailUrl || '',
        },
      },
    ])
    message.success('设置已保存')
  }

  return (
    <Space direction="vertical" size={24} className="w-full">
      <div>
        <Typography.Title level={1} style={{ fontSize: 30, marginBottom: 8 }}>
          站点设置
        </Typography.Title>
        <Typography.Text type="secondary">配置站点的基本信息</Typography.Text>
      </div>
      {loading ? <Spin /> : null}
      <Form<SettingsForm> form={form} layout="vertical" onFinish={onSubmit}>
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
                beforeUpload={async (file) => {
                  if (!canWrite) {
                    message.warning('当前账号无设置修改权限')
                    return Upload.LIST_IGNORE
                  }
                  if (!file.type.startsWith('image/')) {
                    message.error('请上传图片文件')
                    return Upload.LIST_IGNORE
                  }
                  if (file.size > 2 * 1024 * 1024) {
                    message.error('Logo 文件大小不能超过 2MB')
                    return Upload.LIST_IGNORE
                  }
                  const uploaded = await assetsApi.upload(file)
                  setLogoPreview(uploaded.public_url)
                  form.setFieldValue('logoUrl', uploaded.public_url)
                  message.success('Logo 上传成功')
                  return false
                }}
              >
                <Button icon={<UploadOutlined />} disabled={!canWrite}>
                  上传 Logo
                </Button>
              </Upload>
            </Space>
            <Form.Item name="logoUrl" hidden>
              <Input />
            </Form.Item>
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
            <Button type="primary" htmlType="submit" disabled={!canWrite}>
              保存设置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Space>
  )
}
